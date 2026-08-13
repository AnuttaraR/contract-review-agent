import json
import os
import time
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from app.storage.database import (
    init_db, SessionLocal, Contract, ContractStatus,
    save_contract, update_contract_status
)
from app.knowledge_base.loader import load_knowledge_base
from app.intake.parser import parse_document
from app.agent.extractor import process_document
from app.agent.router import route_contract, get_status_badge, get_status_color

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Contract Review Agent",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .status-badge {
        padding: 3px 10px; border-radius: 12px;
        font-size: 12px; font-weight: 600; display: inline-block;
    }
    .badge-green  { background-color: #d4edda; color: #155724; }
    .badge-orange { background-color: #fff3cd; color: #856404; }
    .badge-red    { background-color: #f8d7da; color: #721c24; }
    .badge-gray   { background-color: #e2e3e5; color: #383d41; }
</style>
""", unsafe_allow_html=True)


# ── Init ─────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading knowledge base...")
def init_app():
    init_db()
    load_knowledge_base()
    return True


init_app()


def get_db_session():
    return SessionLocal()


# ═══════════════════════════════════════════════════════════════════════════════
# Helper rendering functions (defined before page blocks)
# ═══════════════════════════════════════════════════════════════════════════════

def render_extracted_table(extracted: dict):
    import pandas as pd

    rows = []
    simple_fields = [
        ("Vendor Name", "vendor_name"),
        ("Contract Type", "contract_type"),
        ("Payment Terms", "payment_terms"),
        ("Start Date", "start_date"),
        ("End Date", "end_date"),
        ("Governing Law", "governing_law"),
        ("Auto Renewal", "auto_renewal"),
        ("Notice Period (days)", "notice_period_days"),
        ("SLA Uptime %", "sla_uptime_percentage"),
        ("SLA Response (hrs)", "sla_response_time_hours"),
        ("GDPR Compliant", "gdpr_compliant"),
        ("DPA Required", "data_processing_agreement"),
        ("Termination for Convenience", "termination_for_convenience"),
        ("IP Ownership", "ip_ownership"),
        ("Dispute Resolution", "dispute_resolution"),
    ]

    for label, key in simple_fields:
        val = extracted.get(key)
        if isinstance(val, bool):
            val = "Yes" if val else "No"
        rows.append({"Field": label, "Value": str(val) if val is not None else "—"})

    val = extracted.get("contract_value_total")
    currency = extracted.get("contract_value_currency", "")
    rows.insert(2, {"Field": "Contract Value", "Value": f"{currency} {val:,.0f}" if val else "—"})

    cap = extracted.get("liability_cap")
    cap_cur = extracted.get("liability_cap_currency", "")
    rows.append({"Field": "Liability Cap", "Value": f"{cap_cur} {cap:,.0f}" if cap else "—"})

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    if risk_flags := extracted.get("risk_flags"):
        st.warning("**Risk Flags Detected:**\n" + "\n".join(f"- {f}" for f in risk_flags))

    if blacklisted := extracted.get("blacklisted_terms_found"):
        st.error("**Blacklisted Terms Found:**\n" + "\n".join(f"- {t}" for t in blacklisted))

    if deliverables := extracted.get("key_deliverables"):
        st.success("**Key Deliverables:**\n" + "\n".join(f"- {d}" for d in deliverables))

    if notes := extracted.get("extraction_notes"):
        st.info(f"**Extraction notes:** {notes}")


def render_enrichment(enrichment: dict):
    col1, col2, col3 = st.columns(3)
    vendor_ok = enrichment.get("vendor_approved")
    sla_ok = enrichment.get("sla_compliant")
    col1.metric("Vendor Approved", "Yes" if vendor_ok else ("No" if vendor_ok is False else "Unknown"))
    col2.metric("SLA Compliant", "Yes" if sla_ok else ("No" if sla_ok is False else "Unknown"))
    col3.metric("Risk Assessment", enrichment.get("risk_assessment", "—"))

    if violations := enrichment.get("policy_violations"):
        st.error("**Policy Violations:**\n" + "\n".join(f"- {v}" for v in violations))

    if gaps := enrichment.get("compliance_gaps"):
        st.warning("**Compliance Gaps:**\n" + "\n".join(f"- {g}" for g in gaps))

    if notes := enrichment.get("enrichment_notes"):
        st.info(f"**Notes:** {notes}")


def render_rag_evidence(extracted: dict, inline: bool = False):
    """Show which KB chunks were retrieved for RAG enrichment of this contract.

    inline=True renders without nested expanders (use when already inside a st.expander).
    """
    from app.knowledge_base.query import build_rag_query
    from app.knowledge_base.loader import get_store

    store = get_store()
    query = build_rag_query(extracted)
    chunks = store.query(query, n_results=6)

    if not chunks:
        st.info("No KB chunks matched for this contract.")
        return

    st.caption(f"BM25 retrieval query: `{query[:120]}`")
    st.markdown(f"**{len(chunks)} policy chunk(s) retrieved and fed to Claude:**")

    if inline:
        for i, chunk in enumerate(chunks, 1):
            source = chunk["metadata"]["source"].replace(".md", "").replace("_", " ").title()
            score = chunk["score"]
            preview = chunk["text"][:280].strip()
            st.markdown(f"**Chunk {i} — {source}** `score: {score:.3f}`")
            st.code(preview, language=None)
            if i < len(chunks):
                st.divider()
    else:
        for i, chunk in enumerate(chunks, 1):
            source = chunk["metadata"]["source"].replace(".md", "").replace("_", " ").title()
            score = chunk["score"]
            preview = chunk["text"][:300].strip()
            with st.expander(f"Chunk {i} — {source}   (relevance: {score:.3f})", expanded=(i == 1)):
                st.code(preview, language=None)


def render_processing_result(contract, result, status, reason, elapsed: float = 0.0):
    extracted = result.get("extracted", {})
    enrichment = result.get("enrichment", {})
    conf = result.get("confidence_score", 0)

    color = get_status_color(status)
    badge = get_status_badge(status)
    badge_class = f"badge-{color}"

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Contract ID", f"#{contract.id}")
    col2.metric("Confidence", f"{conf:.0%}")
    col3.metric("Risk", enrichment.get("risk_assessment", "—"))
    col4.markdown(
        f"**Status**<br><span class='status-badge {badge_class}'>{badge}</span>",
        unsafe_allow_html=True,
    )

    st.info(f"**Routing reason:** {reason}")
    if elapsed:
        st.caption(f"Processed in {elapsed:.1f}s — extraction + RAG enrichment via Claude")

    tab1, tab2, tab3, tab4 = st.tabs(["Extracted Data", "RAG Enrichment", "RAG Evidence", "Raw JSON"])
    with tab1:
        render_extracted_table(extracted)
    with tab2:
        render_enrichment(enrichment)
    with tab3:
        render_rag_evidence(extracted)
    with tab4:
        st.json(result)

    st.divider()
    act_col1, act_col2 = st.columns(2)
    with act_col1:
        st.download_button(
            "⬇ Export as JSON",
            data=json.dumps(result, indent=2, default=str),
            file_name=f"contract_{contract.id}_{(contract.vendor_name or 'unknown').replace(' ', '_')}.json",
            mime="application/json",
            use_container_width=True,
        )
    with act_col2:
        if status == ContractStatus.NEEDS_REVIEW:
            if st.button("Go to Review Queue →", use_container_width=True):
                st.session_state["_nav_target"] = "Review Queue"
                st.rerun()


def render_review_card(contract: Contract):
    extracted = contract.get_extracted()
    enrichment = contract.get_enrichment()
    conf = contract.confidence_score or 0

    with st.expander(
        f"#{contract.id} — {contract.vendor_name or 'Unknown Vendor'} "
        f"| Conf: {conf:.0%} | {contract.contract_type or '—'} "
        f"| {contract.created_at.strftime('%Y-%m-%d %H:%M') if contract.created_at else ''}",
        expanded=False,
    ):
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Vendor", contract.vendor_name or "—")
        val_str = (
            f"{contract.contract_currency or ''} {contract.contract_value:,.0f}"
            if contract.contract_value else "—"
        )
        col2.metric("Value", val_str)
        col3.metric("Confidence", f"{conf:.0%}")
        col4.metric("Risk", enrichment.get("risk_assessment", "—"))

        tab1, tab2, tab3 = st.tabs(["Details", "Policy Analysis", "RAG Evidence"])
        with tab1:
            render_extracted_table(extracted)
        with tab2:
            render_enrichment(enrichment)
        with tab3:
            render_rag_evidence(extracted, inline=True)

        st.divider()
        reviewer_notes = st.text_area(
            "Reviewer notes (optional)",
            key=f"notes_{contract.id}",
            placeholder="Add context or justification for your decision...",
        )

        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("Approve", key=f"approve_{contract.id}", type="primary", use_container_width=True):
                db = get_db_session()
                try:
                    update_contract_status(db, contract.id, ContractStatus.HUMAN_APPROVED, reviewer_notes)
                    st.success(f"Contract #{contract.id} approved.")
                    st.rerun()
                finally:
                    db.close()
        with btn_col2:
            if st.button("Reject", key=f"reject_{contract.id}", type="secondary", use_container_width=True):
                db = get_db_session()
                try:
                    update_contract_status(db, contract.id, ContractStatus.HUMAN_REJECTED, reviewer_notes)
                    st.error(f"Contract #{contract.id} rejected.")
                    st.rerun()
                finally:
                    db.close()


# ── Sidebar navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.title("Contract Review Agent")
    st.caption("Powered by Claude AI + RAG")
    st.divider()

    _nav_options = ["Upload & Process", "Review Queue", "Approved Contracts", "All Contracts", "Knowledge Base"]
    _nav_default = st.session_state.pop("_nav_target", "Upload & Process")
    _nav_idx = _nav_options.index(_nav_default) if _nav_default in _nav_options else 0
    page = st.radio(
        "Navigation",
        _nav_options,
        index=_nav_idx,
        label_visibility="collapsed",
    )

    st.divider()
    st.caption("Confidence Thresholds")
    st.caption(f"✅ Auto-approve: ≥ {os.getenv('CONFIDENCE_AUTO_APPROVE', '0.75')}")
    st.caption(f"⚠️ Review:  ≥ {os.getenv('CONFIDENCE_NEEDS_REVIEW', '0.50')}")
    st.caption(f"❌ Reject:  < {os.getenv('CONFIDENCE_NEEDS_REVIEW', '0.50')}")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: UPLOAD & PROCESS
# ═══════════════════════════════════════════════════════════════════════════════
if page == "Upload & Process":
    st.title("📥 Upload Contract for Review")
    st.markdown("Upload a vendor contract as **PDF**, **image** (JPEG/PNG), or **CSV/Excel**.")

    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded_file = st.file_uploader(
            "Drop your contract here",
            type=["pdf", "png", "jpg", "jpeg", "csv", "xlsx"],
        )
    with col2:
        source_mode = st.selectbox(
            "Intake source",
            ["Direct Upload", "Email Simulation", "Webhook"],
        )
        sender_email = ""
        if source_mode == "Email Simulation":
            sender_email = st.text_input("Sender email", value="vendor@techsolutions-ltd.com")

    if uploaded_file:
        st.divider()
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("File name", uploaded_file.name)
        col_b.metric("File size", f"{len(uploaded_file.getvalue()) / 1024:.1f} KB")
        col_c.metric("Type", uploaded_file.type or "auto-detect")

        if st.button("Process Contract", type="primary", use_container_width=True):
            file_bytes = uploaded_file.getvalue()
            filename = uploaded_file.name
            content_type = uploaded_file.type or ""
            source = source_mode.lower().replace(" ", "_")

            with st.spinner("Parsing document..."):
                try:
                    parsed = parse_document(file_bytes, filename, content_type)
                    st.success(f"Parsed as: **{parsed['file_type'].upper()}**")
                except ValueError as e:
                    st.error(f"Parse error: {e}")
                    st.stop()

            progress = st.progress(0, text="Extracting contract data with Claude AI...")
            _t0 = time.time()
            try:
                result = process_document(parsed)
                _elapsed = time.time() - _t0
                progress.progress(75, text=f"Routing decision... (extracted in {_elapsed:.1f}s)")
            except Exception as e:
                st.error(f"AI extraction failed: {e}")
                st.stop()

            status, reason = route_contract(result["confidence_score"], result["enrichment"])
            progress.progress(90, text="Saving to database...")

            db = get_db_session()
            try:
                contract = save_contract(
                    db,
                    {
                        **result,
                        "source": source,
                        "file_name": filename,
                        "file_type": parsed["file_type"],
                        "status": status,
                    },
                )
                progress.progress(100, text="Done!")
            finally:
                db.close()

            st.divider()
            render_processing_result(contract, result, status, reason, elapsed=_elapsed)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: REVIEW QUEUE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Review Queue":
    st.title("🔍 Review Queue")
    st.markdown("Contracts flagged for human review.")

    db = get_db_session()
    try:
        pending = (
            db.query(Contract)
            .filter(Contract.status == ContractStatus.NEEDS_REVIEW)
            .order_by(Contract.created_at.desc())
            .all()
        )
    finally:
        db.close()

    if not pending:
        st.info("No contracts pending review.")
    else:
        st.metric("Pending Reviews", len(pending))
        for contract in pending:
            render_review_card(contract)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: APPROVED CONTRACTS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Approved Contracts":
    st.title("Approved Contracts")

    db = get_db_session()
    try:
        approved = (
            db.query(Contract)
            .filter(Contract.status.in_([ContractStatus.AUTO_APPROVED, ContractStatus.HUMAN_APPROVED]))
            .order_by(Contract.created_at.desc())
            .all()
        )
    finally:
        db.close()

    if not approved:
        st.info("No approved contracts yet.")
    else:
        import pandas as pd

        total_value = sum(c.contract_value or 0 for c in approved)
        auto_count = sum(1 for c in approved if c.status == ContractStatus.AUTO_APPROVED)

        m1, m2, m3 = st.columns(3)
        m1.metric("Total Approved", len(approved))
        m2.metric("Auto-Approved", auto_count)
        m3.metric("Total Contract Value", f"${total_value:,.0f}")

        st.divider()
        rows = []
        for c in approved:
            rows.append({
                "ID": c.id,
                "Vendor": c.vendor_name or "—",
                "Type": c.contract_type or "—",
                "Value": f"{c.contract_currency or ''} {c.contract_value:,.0f}" if c.contract_value else "—",
                "Confidence": f"{c.confidence_score:.0%}" if c.confidence_score else "—",
                "Status": c.status.value if c.status else "—",
                "Date": c.created_at.strftime("%Y-%m-%d") if c.created_at else "—",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ALL CONTRACTS (DASHBOARD)
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "All Contracts":
    st.title("Dashboard — All Contracts")

    db = get_db_session()
    try:
        all_contracts = db.query(Contract).order_by(Contract.created_at.desc()).all()
    finally:
        db.close()

    if not all_contracts:
        st.info("No contracts processed yet. Upload one to get started.")
    else:
        import pandas as pd

        auto_approved = [c for c in all_contracts if c.status == ContractStatus.AUTO_APPROVED]
        needs_review = [c for c in all_contracts if c.status == ContractStatus.NEEDS_REVIEW]
        rejected = [c for c in all_contracts if c.status in (ContractStatus.REJECTED, ContractStatus.HUMAN_REJECTED)]
        human_approved = [c for c in all_contracts if c.status == ContractStatus.HUMAN_APPROVED]

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total", len(all_contracts))
        col2.metric("Auto-Approved", len(auto_approved))
        col3.metric("Human Approved", len(human_approved))
        col4.metric("Needs Review", len(needs_review))
        col5.metric("Rejected", len(rejected))

        # ── Charts ────────────────────────────────────────────────────────────
        try:
            import altair as alt

            chart_c1, chart_c2 = st.columns(2)

            with chart_c1:
                _status_rows = [
                    {"Status": "Auto-Approved", "Count": len(auto_approved)},
                    {"Status": "Human Approved", "Count": len(human_approved)},
                    {"Status": "Needs Review", "Count": len(needs_review)},
                    {"Status": "Rejected", "Count": len(rejected)},
                ]
                _status_df = pd.DataFrame([r for r in _status_rows if r["Count"] > 0])
                if not _status_df.empty:
                    _donut = (
                        alt.Chart(_status_df)
                        .mark_arc(innerRadius=50, outerRadius=100)
                        .encode(
                            theta=alt.Theta("Count:Q"),
                            color=alt.Color(
                                "Status:N",
                                scale=alt.Scale(
                                    domain=["Auto-Approved", "Human Approved", "Needs Review", "Rejected"],
                                    range=["#28a745", "#20c997", "#ffc107", "#dc3545"],
                                ),
                                legend=alt.Legend(orient="bottom"),
                            ),
                            tooltip=["Status:N", "Count:Q"],
                        )
                        .properties(title="Status Distribution", width=260, height=220)
                    )
                    st.altair_chart(_donut, use_container_width=True)

            with chart_c2:
                _bins = [("< 50%", 0, 0.5), ("50–75%", 0.5, 0.75), ("≥ 75%", 0.75, 1.01)]
                _conf_rows = [
                    {"Range": label, "Count": sum(1 for c in all_contracts if lo <= (c.confidence_score or 0) < hi),
                     "Color": color}
                    for label, lo, hi, color in [
                        ("< 50%", 0, 0.5, "#dc3545"),
                        ("50–75%", 0.5, 0.75, "#ffc107"),
                        ("≥ 75%", 0.75, 1.01, "#28a745"),
                    ]
                ]
                _conf_df = pd.DataFrame(_conf_rows)
                _bar = (
                    alt.Chart(_conf_df)
                    .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
                    .encode(
                        x=alt.X("Range:O", sort=["< 50%", "50–75%", "≥ 75%"], title="Confidence Range", axis=alt.Axis(labelAngle=0)),
                        y=alt.Y("Count:Q", title="Contracts", axis=alt.Axis(tickMinStep=1)),
                        color=alt.Color("Color:N", scale=None, legend=None),
                        tooltip=["Range:N", "Count:Q"],
                    )
                    .properties(title="Confidence Distribution", width=260, height=220)
                )
                st.altair_chart(_bar, use_container_width=True)
        except Exception:
            pass  # charts are non-critical

        st.divider()
        rows = []
        for c in all_contracts:
            enrichment = c.get_enrichment()
            rows.append({
                "ID": c.id,
                "File": c.file_name or "—",
                "Vendor": c.vendor_name or "—",
                "Type": c.contract_type or "—",
                "Value": f"{c.contract_currency or ''} {c.contract_value:,.0f}" if c.contract_value else "—",
                "Conf.": f"{c.confidence_score:.0%}" if c.confidence_score else "—",
                "Risk": enrichment.get("risk_assessment", "—"),
                "Status": c.status.value if c.status else "—",
                "Source": c.source or "—",
                "Date": c.created_at.strftime("%Y-%m-%d %H:%M") if c.created_at else "—",
            })

        df = pd.DataFrame(rows)
        status_filter = st.multiselect(
            "Filter by status",
            options=[s.value for s in ContractStatus],
            default=[s.value for s in ContractStatus],
        )
        st.dataframe(df[df["Status"].isin(status_filter)], use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: KNOWLEDGE BASE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Knowledge Base":
    st.title("Knowledge Base")
    st.markdown("Internal policy documents loaded into the RAG vector store.")

    import glob as _glob
    from app.knowledge_base.loader import get_store, KNOWLEDGE_DOCS_DIR

    store = get_store()
    docs_path = os.path.abspath(KNOWLEDGE_DOCS_DIR)
    md_files = _glob.glob(os.path.join(docs_path, "*.md"))

    col1, col2 = st.columns(2)
    col1.metric("Policy Documents", len(md_files))
    col2.metric("Vector Chunks", store.count())

    if st.button("Reload Knowledge Base", type="secondary"):
        from app.knowledge_base.loader import load_knowledge_base as _lkb
        with st.spinner("Reloading..."):
            _lkb(force_reload=True)
        st.success("Knowledge base reloaded.")
        st.rerun()

    st.divider()
    for filepath in sorted(md_files):
        fname = os.path.basename(filepath)
        with st.expander(f"📄 {fname}"):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            st.markdown(content)

    st.divider()
    st.subheader("Policy Assistant")
    st.caption(
        "Ask a natural language question about your procurement policies. "
        "The system retrieves the most relevant policy chunks via BM25 and uses Claude to synthesise a precise answer."
    )

    _example_questions = [
        "What is the maximum contract value for auto-approval?",
        "Which vendors are pre-approved for fast-track processing?",
        "What are our SLA uptime requirements?",
        "What payment terms do we accept?",
        "When is a Data Processing Agreement required?",
    ]
    _selected_example = st.selectbox(
        "Try an example question or type your own below:",
        ["— select —"] + _example_questions,
        key="kb_example",
    )

    _question = st.text_input(
        "Your question",
        value=_selected_example if _selected_example != "— select —" else "",
        placeholder="e.g. What are our SLA uptime requirements?",
        key="kb_question",
    )

    if _question and _question != "— select —":
        with st.spinner("Retrieving policy context and generating answer..."):
            from app.knowledge_base.query import answer_question
            _qa = answer_question(_question)

        st.markdown("**Answer:**")
        st.info(_qa["answer"])

        if _qa.get("sources"):
            st.caption(f"Sources consulted: {', '.join(_qa['sources'])}")

        with st.expander(f"Retrieved policy chunks ({len(_qa.get('chunks', []))})", expanded=False):
            for _chunk in _qa.get("chunks", []):
                _src = _chunk["metadata"]["source"]
                _score = _chunk["score"]
                st.markdown(f"**{_src}** — relevance score: `{_score:.3f}`")
                st.code(_chunk["text"][:400], language=None)
                st.divider()
