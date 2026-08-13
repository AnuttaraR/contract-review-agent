# Compliance & Regulatory Requirements for Vendor Contracts

Version: 4.0 | Effective: 2026-01-15 | Owner: Legal, Compliance & DPO

## 1. GDPR & Data Protection

### When DPA is Mandatory

A Data Processing Agreement (DPA) is REQUIRED when the vendor:
- Processes personal data of EU/UK residents on our behalf
- Has access to employee personal data
- Processes customer personal data (names, emails, IDs, financial data)
- Operates analytics or monitoring on our systems

### DPA Minimum Requirements

- Lawful basis for processing documented
- Data subject rights procedures defined (access, erasure, portability)
- Sub-processor restrictions and approval process
- Data breach notification: 72-hour notification to us, we notify DPA
- Data transfer mechanism: SCCs, adequacy decision, or equivalent
- Retention and deletion schedules
- Technical and organizational security measures (TOMs) documented

### Data Residency Requirements

| Data Category | Permitted Jurisdictions |
|---|---|
| EU Personal Data | EU27, UK, Canada, Japan, Switzerland, New Zealand, Australia |
| UK Personal Data | UK, EU27, plus same as above |
| Financial Data | Must not leave EU/UK without board approval |
| Biometric Data | Processing country only, no cross-border transfer |

### GDPR Fines Exposure Assessment

- Contracts involving >10,000 EU data subjects: Requires DPO sign-off
- High-risk processing (profiling, sensitive data): DPIA required
- New vendor categories: Legitimate interests assessment

## 2. Financial Services Compliance

### Anti-Money Laundering (AML)

All vendors must:
- Complete KYC screening (UBO disclosure to beneficial owner level)
- Pass sanctions screening (OFAC, EU, UN, HMT lists)
- Provide source of funds documentation for payments > $100,000
- Pass annual re-screening for multi-year contracts

### Payment Compliance

- PCI-DSS Level 1: Required for any vendor touching card data
- Wire transfer vendors: Must be licensed payment institutions
- Crypto payments: NOT permitted without CFO + Legal approval
- Restricted payment jurisdictions: Iran, North Korea, Cuba, Syria, Russia (OFAC)

## 3. Export Controls

Vendors supplying technology, software, or technical data must confirm:
- No items on the Commerce Control List (CCL) without EAR license
- ITAR compliance for any defense-related items
- End-user certificates for controlled technology
- Deemed export analysis for foreign national employees with access

## 4. Modern Slavery & Supply Chain

For contracts > $100,000 annually:
- Vendor must provide Modern Slavery Act statement
- Supply chain transparency: Tier 1 suppliers disclosed
- Certification that no forced labor, child labor in supply chain
- Annual attestation required for multi-year contracts

## 5. Cybersecurity Requirements

### Security Standards by Contract Type

| Contract Type | Required Standard |
|---|---|
| SaaS / Cloud | SOC2 Type II or ISO 27001 |
| Payment Processing | PCI-DSS Level 1 |
| Health Data | HIPAA-compliant BAA required |
| Government Data | FedRAMP or equivalent |
| General IT Services | Cyber Essentials Plus (UK) or equivalent |

### Penetration Testing

- Cloud/SaaS vendors processing sensitive data: Annual pen test required
- Results shared with us within 30 days
- Critical findings remediated within 30 days, high within 90 days
- We reserve the right to conduct our own testing with notice

### Security Incident Response

Contract must specify:
- Vendor security contact (24/7 reachable)
- Initial notification to us: Within 72 hours of discovery
- Forensic cooperation: Vendor must assist our investigation
- Remediation timeline: Critical within 24h, High within 7 days
- Post-incident review: Written report within 30 days

## 6. Environmental & Social Governance (ESG)

For contracts > $500,000:
- Carbon footprint disclosure (Scope 1 & 2 at minimum)
- Net-zero or carbon reduction roadmap
- Diversity & inclusion reporting
- Living wage certification for services with direct labor component

## 7. Insurance Requirements

| Contract Value | Required Insurance | Minimum Coverage |
|---|---|---|
| < $50,000 | Professional Indemnity | $1M |
| $50,000 – $500,000 | PI + Public Liability | $5M / $2M |
| > $500,000 | PI + PL + Cyber Insurance | $10M / $5M / $5M |
| Any data processing | Cyber Liability | $5M minimum |

Insurance certificates must be provided before contract execution and renewed annually.

## 8. Conflict of Interest

Vendors must disclose:
- Any financial or personal relationships with our employees
- Ownership by individuals on our restricted persons list
- Competing client relationships (for consultants with access to sensitive strategy)

Automatic disqualifiers:
- Vendor owned/controlled by sanctioned individuals
- Vendor with active legal disputes against our organization
- Vendor previously terminated for cause within 24 months
