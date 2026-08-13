EXTRACTION_SYSTEM_PROMPT = """You are a specialized contract analysis AI for a procurement team.
Your task is to extract structured data from vendor contracts with high accuracy.

IMPORTANT RULES:
- Extract ONLY information explicitly present in the document
- Use null for any field not found — never hallucinate or guess values
- Dates must be in ISO 8601 format (YYYY-MM-DD)
- Monetary values must be numeric (no currency symbols in the value field)
- Confidence score reflects your certainty about the extraction quality (0.0-1.0)

OUTPUT FORMAT: Return a single valid JSON object matching the schema exactly."""

EXTRACTION_USER_PROMPT = """Analyze this vendor contract document and extract all information into the following JSON schema.

DOCUMENT CONTENT:
{document_text}

REQUIRED JSON SCHEMA:
{{
  "vendor_name": "string | null",
  "vendor_registration_number": "string | null",
  "vendor_address": "string | null",
  "vendor_contact_email": "string | null",
  "vendor_contact_phone": "string | null",
  "contract_title": "string | null",
  "contract_id": "string | null",
  "contract_type": "string | null (e.g. MSA, SOW, NDA, SLA, License)",
  "contract_value_total": "number | null",
  "contract_value_currency": "string | null (ISO 4217, e.g. USD, EUR)",
  "payment_terms": "string | null (e.g. Net-30, Net-60)",
  "payment_schedule": "string | null",
  "start_date": "YYYY-MM-DD | null",
  "end_date": "YYYY-MM-DD | null",
  "auto_renewal": "boolean | null",
  "notice_period_days": "integer | null",
  "governing_law": "string | null",
  "dispute_resolution": "string | null",
  "liability_cap": "number | null",
  "liability_cap_currency": "string | null",
  "indemnification_clause": "boolean | null",
  "ip_ownership": "string | null",
  "data_processing_agreement": "boolean | null",
  "gdpr_compliant": "boolean | null",
  "sla_uptime_percentage": "number | null",
  "sla_response_time_hours": "number | null",
  "sla_penalty_clause": "boolean | null",
  "termination_for_convenience": "boolean | null",
  "termination_for_cause": "boolean | null",
  "services_description": "string | null",
  "key_deliverables": ["string"] or [],
  "soc2_certified": "boolean | null",
  "iso27001_certified": "boolean | null",
  "security_breach_notification_hours": "integer | null (e.g. 24, 72)",
  "modern_slavery_statement": "boolean | null",
  "blacklisted_terms_found": ["string"] or [],
  "risk_flags": ["string"] or [],
  "confidence_score": "number between 0.0 and 1.0",
  "extraction_notes": "string | null"
}}

Return ONLY the JSON object, no markdown, no explanation."""

RAG_ENRICHMENT_PROMPT = """You are a contract compliance analyst. Validate this extracted contract data against the internal policy context provided.

EXTRACTED CONTRACT DATA:
{contract_json}

INTERNAL POLICY CONTEXT:
{rag_context}

CRITICAL RULES:
- policy_violations: ONLY include items where the contract EXPLICITLY BREACHES a stated policy rule.
  Do NOT include items where the contract meets or exceeds the policy requirement.
  Do NOT include process steps (e.g. "approval required") — those are not contract violations.
  Do NOT include gaps in documentation — put those in compliance_gaps.
  IMPORTANT for thresholds: compare actual contract_value_total against the numeric threshold.
  If value is BELOW the threshold (e.g. $65,000 < $100,000 threshold), do NOT flag it as a violation.
- compliance_gaps: items that are unclear, undocumented, or require pre-execution verification but are NOT rule breaches.
  Do not put threshold-based requirements here if the contract value is clearly below the threshold.
- risk_assessment:
  LOW  = no policy violations AND vendor is approved AND core compliance certifications confirmed (SOC2, ISO27001).
         Pre-execution process steps (e.g. "provide insurance certificates before signing") do NOT raise risk above LOW.
         A Tier 1 approved vendor with no violations and confirmed SOC2/ISO27001 is LOW risk.
  MEDIUM = minor substantive gaps in contract terms OR unclearness in certification status OR minor policy ambiguity.
           Do NOT assign MEDIUM solely due to pre-execution documentation checklist items.
  HIGH = one or more genuine policy violations OR vendor not approved OR blacklisted terms found

Return ONLY a JSON object — no explanation, no markdown:
{{
  "vendor_approved": true | false | null,
  "policy_violations": ["brief string per ACTUAL breach — max 20 words each"],
  "compliance_gaps": ["brief string per gap — max 15 words each"],
  "sla_compliant": true | false | null,
  "risk_assessment": "LOW" | "MEDIUM" | "HIGH",
  "enrichment_notes": "one sentence summary",
  "adjusted_confidence_score": 0.0-1.0
}}

Keep each list item under 20 words. Maximum 5 items per list."""
