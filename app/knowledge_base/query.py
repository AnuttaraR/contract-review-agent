import os

from app.knowledge_base.loader import get_store


def query_knowledge_base(query_text: str, n_results: int = 5) -> str:
    """Query the vector store and return concatenated context."""
    store = get_store()

    if store.count() == 0:
        return "No knowledge base content available."

    results = store.query(query_text, n_results=n_results)

    if not results:
        return "No relevant policy context found."

    context_parts = []
    for r in results:
        source = r["metadata"].get("source", "unknown")
        score = r["score"]
        context_parts.append(f"[Source: {source} | Relevance: {score:.3f}]\n{r['text']}")

    return "\n\n---\n\n".join(context_parts)


def answer_question(question: str, n_results: int = 5) -> dict:
    """Retrieve KB context then synthesise a policy answer using Claude."""
    from app.agent.extractor import get_client

    store = get_store()
    if store.count() == 0:
        return {"answer": "Knowledge base is empty.", "sources": [], "chunks": []}

    chunks = store.query(question, n_results=n_results)
    if not chunks:
        return {"answer": "No relevant policy content found for that question.", "sources": [], "chunks": []}

    context = "\n\n---\n\n".join(
        f"[{c['metadata']['source']} | score {c['score']:.3f}]\n{c['text']}"
        for c in chunks
    )

    model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
    client = get_client()

    response = client.messages.create(
        model=model,
        max_tokens=1024,
        system=(
            "You are a procurement policy assistant. "
            "Answer the user's question using ONLY the provided policy document context. "
            "Be concise (3-5 sentences), precise, and cite the source document name when referencing specific rules. "
            "If the context does not cover the question, say so clearly."
        ),
        messages=[{
            "role": "user",
            "content": f"Policy context:\n\n{context}\n\nQuestion: {question}"
        }]
    )

    return {
        "answer": response.content[0].text.strip(),
        "sources": list({c["metadata"]["source"] for c in chunks}),
        "chunks": chunks,
    }


def build_rag_query(extracted: dict) -> str:
    """Build a targeted RAG query from extracted contract fields."""
    parts = []
    if v := extracted.get("vendor_name"):
        parts.append(f"vendor: {v}")
    if ct := extracted.get("contract_type"):
        parts.append(f"contract type: {ct}")
    if pt := extracted.get("payment_terms"):
        parts.append(f"payment terms: {pt}")
    if gl := extracted.get("governing_law"):
        parts.append(f"governing law: {gl}")
    if sl := extracted.get("sla_uptime_percentage"):
        parts.append(f"SLA uptime: {sl}%")
    if rf := extracted.get("risk_flags"):
        parts.append(f"risk flags: {', '.join(rf)}")
    if bt := extracted.get("blacklisted_terms_found"):
        parts.append(f"blacklisted terms: {', '.join(bt)}")

    base = " | ".join(parts) if parts else "vendor contract policy compliance"
    return f"Policy context for {base}"
