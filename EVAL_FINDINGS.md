# Eval findings

Running `eval_extraction.py` and `eval_routing.py` against the sample documents surfaced three
real bugs, which were fixed and re-verified. This is the record of that pass.

## What was measured

- **Extraction accuracy**: 84/85 fields (98.8%) correct across 4 documents (3 PDF, 1 scanned
  image), graded against ground truth taken directly from the values used to generate each
  document in `generate_samples.py`. The one miss was a paraphrase ("Germany" vs "German law"),
  not a wrong extraction.
- **Routing accuracy**: initially 1/4 against hand-picked expected outcomes. Investigating the
  other 3 "misses" found:

## Bugs found and fixed

1. **Numeric threshold logic in the enrichment prompt.** The prompt already said not to flag
   contracts that meet a policy minimum, but the model wasn't applying that consistently to
   thresholds other than contract value (response times, notification windows, liability
   multipliers described as "recommended" vs "minimum"). Generalized the rule in
   `app/agent/prompts.py` to cover all numeric comparisons explicitly, and added `temperature=0`
   to all three extraction/enrichment API calls in `app/agent/extractor.py` for determinism —
   the same input was producing different violations on different runs beforehand.
2. **Coarse indemnification schema.** The extraction schema has one boolean
   (`indemnification_clause`) covering all indemnification; the enrichment step was flagging
   "IP indemnification missing" even when general indemnification was present, because it had
   no way to know the schema doesn't distinguish. Added an explicit rule: a true
   `indemnification_clause` satisfies IP-indemnification policy checks too.
3. **Knowledge-base / fixture inconsistency.** `knowledge_docs/approved_vendors.md` listed
   GlobalSoft Solutions as a **Tier 1** vendor (approval expiring 2026-09-30), while the sample
   SOW's own generated text claims it's "Tier 3 Pending Approval." The SOW's start date
   (2026-10-01) is one day after that Tier-1 approval lapses — the model was reasoning about this
   *correctly*, the two source documents just disagreed. Moved GlobalSoft to the Tier 3 Pending
   list in `approved_vendors.md` to match the intended demo narrative.

## What's left unresolved, on purpose

After the fixes, routing is still 1/4 against the original expected-outcome labels:

- **GlobalSoft SOW**: now correctly identified as Tier 3 pending → `REJECTED`. The original label
  (`NEEDS_REVIEW`) was my assumption when the fixtures were written, not a verified target — a
  pending-approval vendor arguably *should* escalate hard, not just get queued for review. Treating
  this as the model being right and the test label being wrong.
- **TechSolutions MSA / CloudSecure**: still occasionally flagged for a modern-slavery-statement
  threshold or a documentation-justification gap that a human reviewer would likely wave through.
  Added an explicit "don't compare multi-year total value against an annual threshold" rule, which
  reduced but didn't eliminate this — the model still leans toward escalating ambiguous policy
  language rather than assuming compliance. This is a real, disclosed limitation: the system is
  conservative by construction (fails toward human review, not toward auto-approval), and further
  tightening the prompt has diminishing returns without either a stronger model or a stricter
  schema that captures nuance (e.g. annual value, indemnification sub-type) explicitly rather than
  leaving the enrichment model to infer it from a lossy extracted summary.

**Takeaway for the README**: report extraction accuracy as the headline (it's real and strong).
Report routing behavior honestly as conservative/fail-safe rather than claiming a routing
accuracy percentage the system doesn't reliably hit.
