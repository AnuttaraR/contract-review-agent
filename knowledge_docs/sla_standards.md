# SLA Standards & Benchmarks

Version: 2.1 | Effective: 2026-03-01 | Owner: IT & Vendor Management

## Cloud & SaaS Services

### Uptime Requirements by Tier

| Service Tier | Min Uptime | Max Planned Downtime/Month | Response Time (Critical) |
|---|---|---|---|
| Tier 1 — Mission Critical | 99.99% | 4.3 minutes | 15 minutes |
| Tier 2 — Business Critical | 99.9% | 43.8 minutes | 1 hour |
| Tier 3 — Standard Business | 99.5% | 3.65 hours | 4 hours |
| Tier 4 — Non-Critical | 99.0% | 7.3 hours | 24 hours |

Mission Critical systems: payment processing, authentication, core data platform
Business Critical: CRM, ERP, analytics
Standard Business: internal tools, reporting
Non-Critical: test environments, archival systems

### Penalty Structure

SLA breach penalties (per calendar month with breach):

| Uptime Achieved | Penalty |
|---|---|
| 99.0% – SLA threshold | 5% of monthly fee |
| 95.0% – 99.0% | 10% of monthly fee |
| 90.0% – 95.0% | 20% of monthly fee |
| < 90.0% | 30% of monthly fee + termination right |

Penalties are credited against next invoice (not cash refunds unless contract specifies).

### Measurement Methodology

- Uptime measured as: (Total minutes – Downtime minutes) / Total minutes × 100
- Planned maintenance windows excluded IF notified 48+ hours in advance
- Emergency maintenance (security patches): excluded if notified within 2 hours and resolved within 4 hours
- Third-party dependency failures: shared liability (50/50 split)

## Professional Services / Consulting

### Delivery SLAs

| Deliverable Type | Response Time | Delivery SLA |
|---|---|---|
| Bug fix (Critical) | 4 hours | 24 hours |
| Bug fix (High) | 8 hours | 72 hours |
| Feature request | 2 business days | Per agreed milestone |
| Documentation | 2 business days | 5 business days |
| Status report | Same business day | Weekly cadence |

### Quality Standards

- Code review: All deliverables require documented review
- Testing: Unit test coverage ≥ 80% for custom software
- Security: OWASP Top 10 compliance required
- Acceptance: Client has 10 business days to accept/reject deliverables

## Data Services & Integrations

### Data Freshness SLAs

| Data Type | Maximum Latency | Reconciliation Window |
|---|---|---|
| Real-time transactions | < 100ms | N/A |
| Near-real-time feeds | < 5 minutes | 15 minutes |
| Batch processing | < 4 hours | 24 hours |
| Historical data loads | < 24 hours | 7 days |

### Data Quality Standards

- Accuracy: ≥ 99.5% (measured by automated reconciliation)
- Completeness: ≥ 99.9% (no missing critical fields)
- Consistency: Zero tolerance for duplicate primary keys
- Error handling: Failed records must be logged and retried within 1 hour

## Logistics & Physical Services

### Delivery SLAs

| Service Level | Delivery Window | Tracking Required | Insurance |
|---|---|---|---|
| Express | Next business day | Yes | Required |
| Standard | 3-5 business days | Yes | Recommended |
| Economy | 7-14 business days | Recommended | Optional |

### Service Failure Remedies

- Late delivery > 24 hours: 2% discount per day (max 10%)
- Lost/damaged shipment: Full replacement + 10% compensation
- Repeated failures (3+ in a quarter): Contract review trigger

## Escalation Paths

All contracts must define:
1. Primary operational contact (24h response)
2. Escalation contact — Manager level (4h response for critical)
3. Executive escalation (CTO/COO equivalent, for Tier 1 incidents)
4. Out-of-hours support: Required for Tier 1 and Tier 2 services
