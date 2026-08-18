"""
End-to-end routing accuracy + latency eval.

Runs the full pipeline (parse -> extract -> RAG enrich -> route) on each sample
document and checks the routing decision against the outcome the document was
designed to produce (see generate_samples.py header comments / README table).

Usage: python eval_routing.py
"""
import json
import os
import time
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

from app.intake.parser import parse_document
from app.agent.extractor import process_document
from app.agent.router import route_contract
from app.knowledge_base.loader import load_knowledge_base

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "sample_docs")

# Expected outcome each document was designed to produce (see generate_samples.py
# section comments: "expect AUTO_APPROVE" / "expect NEEDS_REVIEW" / "expect REJECT").
EXPECTED = {
    "techsolutions_msa.pdf": "AUTO_APPROVED",
    "globalsoft_sow.png": "NEEDS_REVIEW",
    "cloudsecure_saas.pdf": "AUTO_APPROVED",
    "futuretech_development.pdf": "REJECTED",
}


def main():
    print("Loading knowledge base...")
    load_knowledge_base()

    results = []
    for filename, expected in EXPECTED.items():
        path = os.path.join(SAMPLE_DIR, filename)
        with open(path, "rb") as f:
            file_bytes = f.read()

        t0 = time.time()
        parsed = parse_document(file_bytes, filename)
        result = process_document(parsed)
        status, reason = route_contract(result["confidence_score"], result["enrichment"])
        elapsed = time.time() - t0

        actual = status.value if hasattr(status, "value") else str(status)
        match = actual == expected
        results.append({
            "file": filename,
            "expected": expected,
            "actual": actual,
            "match": match,
            "confidence": result["confidence_score"],
            "risk": result["enrichment"].get("risk_assessment"),
            "seconds": round(elapsed, 1),
            "reason": reason,
        })
        mark = "OK  " if match else "MISS"
        print(f"[{mark}] {filename:32s} expected={expected:14s} actual={actual:14s} "
              f"conf={result['confidence_score']:.2f} risk={result['enrichment'].get('risk_assessment')} "
              f"({elapsed:.1f}s)")

    n_match = sum(r["match"] for r in results)
    avg_time = sum(r["seconds"] for r in results) / len(results)
    print(f"\nRouting accuracy: {n_match}/{len(results)} "
          f"({n_match / len(results) * 100:.1f}%)  |  avg. {avg_time:.1f}s/contract "
          f"(parse + extract + RAG enrich + route)")

    out = {
        "run_at": datetime.utcnow().isoformat() + "Z",
        "routing_accuracy": n_match / len(results),
        "avg_seconds_per_contract": avg_time,
        "documents": results,
    }
    with open(os.path.join(os.path.dirname(__file__), "eval_routing_results.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)


if __name__ == "__main__":
    main()
