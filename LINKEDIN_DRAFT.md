# LinkedIn post draft

<!-- TODO before publishing:
 1. Fill in the Results table in README.md and pull the headline metric into the post below.
 2. Record a 20-30s screen capture (demo.gif) — upload the PDF, image, and CSV samples,
    show the routing decision, click into the evidence panel for a citation.
    Embed it as the first attachment on the LinkedIn post — it's what stops the scroll.
 3. Push the repo (README swap + Flat Rock removal already committed locally, not yet pushed).
-->

Built an agentic contract review pipeline: upload a vendor contract (PDF, scanned image, or CSV batch), and it extracts 25+ fields, checks them against a policy knowledge base with RAG, and routes to auto-approve or a human review queue — citing the exact policy clause behind every flag.

[HEADLINE METRIC — e.g. "94% field extraction accuracy across a hand-labeled test set, X% routing precision against human review"]

Stack: Claude for extraction + vision OCR, ChromaDB for retrieval, FastAPI webhook intake, Streamlit for the review dashboard.

The interesting part wasn't the extraction — it was getting the routing logic to fail safely: high-risk contracts get escalated regardless of confidence score, and every auto-approval is traceable back to the specific policy clause that justified it.

Code: https://github.com/AnuttaraR/contract-review-agent

#AIEngineering #RAG #LLM #Python
