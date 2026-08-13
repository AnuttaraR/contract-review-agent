import os
from app.storage.database import ContractStatus

THRESHOLD_AUTO_APPROVE = float(os.getenv("CONFIDENCE_AUTO_APPROVE", "0.75"))
THRESHOLD_NEEDS_REVIEW = float(os.getenv("CONFIDENCE_NEEDS_REVIEW", "0.50"))


def route_contract(confidence_score: float, enrichment: dict) -> tuple[ContractStatus, str]:
    """
    Determine routing status and reason.
    HIGH risk → REJECT.
    Low confidence → REJECT.
    Policy violations or unknown vendor → NEEDS_REVIEW.
    High confidence, low risk, no violations → AUTO_APPROVE.
    """
    risk = enrichment.get("risk_assessment", "UNKNOWN")
    violations = enrichment.get("policy_violations", []) or []
    gaps = enrichment.get("compliance_gaps", []) or []
    vendor_approved = enrichment.get("vendor_approved")

    # Hard reject: only when confidence is below minimum OR explicit HIGH risk
    if confidence_score < THRESHOLD_NEEDS_REVIEW:
        return ContractStatus.REJECTED, (
            f"Confidence {confidence_score:.2f} below minimum threshold {THRESHOLD_NEEDS_REVIEW}. "
            f"Insufficient data to process."
        )

    if risk == "HIGH":
        return ContractStatus.REJECTED, (
            f"HIGH risk assessment. "
            + (f"Violations: {'; '.join(violations[:2])}" if violations else "")
        )

    # Auto-approve: high confidence, non-high risk, no violations, vendor approved or unknown
    if (confidence_score >= THRESHOLD_AUTO_APPROVE
            and risk in ("LOW",)
            and not violations
            and vendor_approved is not False):
        return ContractStatus.AUTO_APPROVED, (
            f"Confidence {confidence_score:.2f} ≥ {THRESHOLD_AUTO_APPROVE}. "
            f"No policy violations. Risk: {risk}."
        )

    # Everything else: send to human review
    reasons = []
    if violations:
        reasons.append(f"{len(violations)} policy item(s) to review")
    if gaps:
        reasons.append(f"{len(gaps)} compliance gap(s)")
    if vendor_approved is False:
        reasons.append("vendor not in approved registry")
    if confidence_score < THRESHOLD_AUTO_APPROVE:
        reasons.append(f"confidence {confidence_score:.2f} below auto-approve threshold")
    if risk == "MEDIUM":
        reasons.append("medium risk level")

    reason_str = "; ".join(reasons) if reasons else "requires manual review"
    return ContractStatus.NEEDS_REVIEW, f"Flagged for review: {reason_str}"


def get_status_badge(status: ContractStatus) -> str:
    badges = {
        ContractStatus.AUTO_APPROVED: "AUTO APPROVED",
        ContractStatus.NEEDS_REVIEW: "NEEDS REVIEW",
        ContractStatus.REJECTED: "REJECTED",
        ContractStatus.HUMAN_APPROVED: "APPROVED",
        ContractStatus.HUMAN_REJECTED: "REJECTED",
        ContractStatus.PENDING: "PENDING",
    }
    return badges.get(status, str(status))


def get_status_color(status: ContractStatus) -> str:
    colors = {
        ContractStatus.AUTO_APPROVED: "green",
        ContractStatus.NEEDS_REVIEW: "orange",
        ContractStatus.REJECTED: "red",
        ContractStatus.HUMAN_APPROVED: "green",
        ContractStatus.HUMAN_REJECTED: "red",
        ContractStatus.PENDING: "gray",
    }
    return colors.get(status, "gray")
