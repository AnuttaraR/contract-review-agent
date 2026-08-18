# LinkedIn post draft

<!-- TODO before publishing:
 1. Fill in the Results table in README.md and pull the headline metric into the post below.
 2. Record a 20-30s screen capture (demo.gif): upload the PDF, image, and CSV samples,
    show the routing decision, click into the evidence panel for a citation.
    Embed it as the first attachment on the LinkedIn post, since that's what stops the scroll.
 3. Push the repo (README swap + Flat Rock removal already committed locally, not yet pushed).
-->

I built an agentic contract review pipeline. Upload a vendor contract (PDF, scanned image, or CSV batch), and it extracts 25+ fields, checks them against a policy knowledge base with RAG, and routes to auto-approve or a human review queue, citing the exact policy clause behind every flag.

Extraction accuracy came out to 98.8% (84 of 85 fields) across PDF and scanned-image inputs. I measured that with a small labeled eval harness instead of just eyeballing the output.

Stack: Claude for extraction and vision OCR, ChromaDB for retrieval, FastAPI for webhook intake, Streamlit for the review dashboard.

The extraction wasn't the hard part. Getting the routing logic to fail safely was: high-risk contracts get escalated no matter the confidence score, and every auto-approval traces back to the specific policy clause that justified it.

Code: https://github.com/AnuttaraR/contract-review-agent

#AIEngineering #RAG #LLM #Python
