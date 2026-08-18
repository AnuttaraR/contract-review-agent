"""
Field-level extraction accuracy eval.

Ground truth for each sample document is read directly from the literal values
used to generate it in generate_samples.py (see GOLD below) - not hand-guessed
after the fact. Run after `python generate_samples.py`.

Scope: the four natural-language contract documents (3 PDF, 1 scanned image).
vendor_contracts_batch.csv is excluded - the extractor's schema targets a single
contract, and a 5-row batch file doesn't have one unambiguous "correct" single
extraction to grade against.

Usage:
    python eval_extraction.py            # run all 4 docs, print + save report
    python eval_extraction.py --doc techsolutions_msa.pdf
"""
import argparse
import json
import os
import sys
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

from app.intake.parser import parse_document
from app.agent.extractor import extract_from_text, extract_from_image

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "sample_docs")

# ── Ground truth, transcribed from the literal values passed into each
#    generate_pdf_*/generate_image_* function in generate_samples.py ──────────
GOLD = {
    "techsolutions_msa.pdf": {
        "vendor_name": "TechSolutions Ltd",
        "vendor_registration_number": "GB-12345678",
        "contract_type": "MSA",
        "contract_value_total": 180000,
        "contract_value_currency": "USD",
        "payment_terms": "Net-30",
        "start_date": "2026-09-01",
        "end_date": "2029-08-31",
        "auto_renewal": True,
        "notice_period_days": 60,
        "governing_law": "England and Wales",
        "liability_cap": 180000,
        "liability_cap_currency": "USD",
        "indemnification_clause": True,
        "gdpr_compliant": True,
        "data_processing_agreement": True,
        "sla_uptime_percentage": 99.9,
        "sla_response_time_hours": 1,
        "sla_penalty_clause": True,
        "termination_for_convenience": True,
        "termination_for_cause": True,
        "soc2_certified": True,
        "security_breach_notification_hours": 72,
    },
    "globalsoft_sow.png": {
        "vendor_name": "GlobalSoft Solutions",
        "vendor_registration_number": "IN-33445566",
        "contract_type": "SOW",
        "contract_value_total": 95000,
        "contract_value_currency": "EUR",
        "payment_terms": "Net-45",
        "start_date": "2026-10-01",
        "end_date": "2027-03-31",
        "auto_renewal": False,
        "notice_period_days": 60,
        "governing_law": "England and Wales",
        "liability_cap": 95000,
        "liability_cap_currency": "EUR",
        "gdpr_compliant": True,
        "data_processing_agreement": True,
        "sla_uptime_percentage": 99.5,
        "sla_response_time_hours": 4,
        "sla_penalty_clause": True,
        "termination_for_convenience": True,
        "ip_ownership": "Client",
    },
    "cloudsecure_saas.pdf": {
        "vendor_name": "CloudSecure GmbH",
        "vendor_registration_number": "DE-55443322",
        "contract_type": "SaaS License",
        "contract_value_total": 75000,
        "contract_value_currency": "EUR",
        "payment_terms": "Net-30",
        "start_date": "2026-07-01",
        "end_date": "2027-06-30",
        "auto_renewal": True,
        "governing_law": "Germany",
        "liability_cap": 150000,
        "liability_cap_currency": "EUR",
        "indemnification_clause": True,
        "gdpr_compliant": True,
        "data_processing_agreement": True,
        "soc2_certified": True,
        "iso27001_certified": True,
        "security_breach_notification_hours": 24,
        "sla_uptime_percentage": 99.99,
        "sla_response_time_hours": 0.25,
        "sla_penalty_clause": True,
        "termination_for_convenience": True,
        "termination_for_cause": True,
        "ip_ownership": "Vendor",
    },
    "futuretech_development.pdf": {
        "vendor_name": "FutureTech Systems",
        "vendor_registration_number": "XX-00000000",
        "contract_type": "Software Development",
        "contract_value_total": 500000,
        "contract_value_currency": "USD",
        "payment_terms": "Net-7",
        "start_date": "2026-10-01",
        "end_date": "2027-09-30",
        "auto_renewal": True,
        "notice_period_days": 7,
        "governing_law": "Cayman Islands",
        "liability_cap": 1000,
        "liability_cap_currency": "USD",
        "indemnification_clause": False,
        "gdpr_compliant": False,
        "data_processing_agreement": False,
        "termination_for_convenience": False,
        "ip_ownership": "Vendor",
    },
}

NUMERIC_FIELDS = {
    "contract_value_total", "liability_cap", "sla_uptime_percentage",
    "sla_response_time_hours", "notice_period_days",
    "security_breach_notification_hours",
}
BOOL_FIELDS = {
    "auto_renewal", "indemnification_clause", "gdpr_compliant",
    "data_processing_agreement", "sla_penalty_clause",
    "termination_for_convenience", "termination_for_cause",
    "soc2_certified", "iso27001_certified",
}


def compare(field: str, gold, got) -> bool:
    if got is None:
        return False
    if field in NUMERIC_FIELDS:
        try:
            return abs(float(gold) - float(got)) < 0.01
        except (TypeError, ValueError):
            return False
    if field in BOOL_FIELDS:
        return bool(gold) == bool(got)
    if field in ("start_date", "end_date"):
        return str(gold).strip() == str(got).strip()
    # string fields: case-insensitive substring match either direction,
    # since the model may return "Net-30 days" for gold "Net-30" etc.
    g, o = str(gold).strip().lower(), str(got).strip().lower()
    return g == o or g in o or o in g


def eval_doc(filename: str) -> dict:
    path = os.path.join(SAMPLE_DIR, filename)
    with open(path, "rb") as f:
        file_bytes = f.read()

    parsed = parse_document(file_bytes, filename)
    if parsed["file_type"] == "image":
        extracted = extract_from_image(parsed["image_b64"], parsed["image_media_type"])
    else:
        extracted = extract_from_text(parsed["raw_text"])

    gold = GOLD[filename]
    field_results = {}
    for field, gold_val in gold.items():
        got_val = extracted.get(field)
        field_results[field] = {
            "gold": gold_val,
            "extracted": got_val,
            "correct": compare(field, gold_val, got_val),
        }

    correct_count = sum(1 for r in field_results.values() if r["correct"])
    return {
        "file": filename,
        "field_count": len(field_results),
        "correct_count": correct_count,
        "accuracy": correct_count / len(field_results),
        "fields": field_results,
        "confidence_score": extracted.get("confidence_score"),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--doc", help="Run a single document by filename")
    args = parser.parse_args()

    docs = [args.doc] if args.doc else list(GOLD.keys())
    results = []

    for doc in docs:
        print(f"\n{'=' * 70}\nEvaluating: {doc}\n{'=' * 70}")
        try:
            r = eval_doc(doc)
        except Exception as e:
            print(f"  ERROR: {e}")
            continue
        results.append(r)
        print(f"  Accuracy: {r['correct_count']}/{r['field_count']} "
              f"({r['accuracy'] * 100:.1f}%)  |  model confidence: {r['confidence_score']}")
        for field, res in r["fields"].items():
            mark = "OK  " if res["correct"] else "MISS"
            print(f"    [{mark}] {field:38s} gold={res['gold']!r:30}  got={res['extracted']!r}")

    if not results:
        print("No results.")
        sys.exit(1)

    total_correct = sum(r["correct_count"] for r in results)
    total_fields = sum(r["field_count"] for r in results)
    overall = total_correct / total_fields

    print(f"\n{'=' * 70}\nOVERALL: {total_correct}/{total_fields} fields correct "
          f"({overall * 100:.1f}%) across {len(results)} documents\n{'=' * 70}")

    out = {
        "run_at": datetime.utcnow().isoformat() + "Z",
        "overall_accuracy": overall,
        "total_fields": total_fields,
        "total_correct": total_correct,
        "documents": results,
    }
    out_path = os.path.join(os.path.dirname(__file__), "eval_results.json")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
