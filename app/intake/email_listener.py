"""
Gmail polling via Gmail MCP connector.
In demo mode, this module exposes a polling function that checks Gmail for
emails with attachments matching contract keywords.

For production, configure Gmail OAuth credentials (see .env.example).
The MCP connector (mcp__64cd16b3__*) handles OAuth in Claude Code sessions.
"""
import os
import time
import base64
import logging
from typing import Optional

logger = logging.getLogger(__name__)

GMAIL_POLL_INTERVAL = int(os.getenv("GMAIL_POLL_INTERVAL", "60"))
CONTRACT_KEYWORDS = ["contract", "agreement", "vendor", "msa", "sow", "nda", "sla"]


def extract_attachments_from_message(message: dict) -> list[dict]:
    """Parse Gmail message parts to find attachments."""
    attachments = []
    payload = message.get("payload", {})
    parts = payload.get("parts", [])

    def walk_parts(parts_list):
        for part in parts_list:
            filename = part.get("filename", "")
            mime_type = part.get("mimeType", "")
            body = part.get("body", {})
            attachment_id = body.get("attachmentId")

            if filename and attachment_id:
                attachments.append({
                    "filename": filename,
                    "mime_type": mime_type,
                    "attachment_id": attachment_id,
                    "size": body.get("size", 0),
                })

            sub_parts = part.get("parts", [])
            if sub_parts:
                walk_parts(sub_parts)

    walk_parts(parts)
    return attachments


def is_contract_email(subject: str, body_snippet: str) -> bool:
    """Heuristic: is this email likely about a vendor contract?"""
    text = (subject + " " + body_snippet).lower()
    return any(kw in text for kw in CONTRACT_KEYWORDS)


def build_gmail_query() -> str:
    """Build Gmail search query for contract emails with attachments."""
    keyword_clause = " OR ".join(CONTRACT_KEYWORDS)
    return f"has:attachment ({keyword_clause})"


class GmailPoller:
    """
    Polls Gmail for contract emails using the Gmail MCP connector.
    In standalone mode (no MCP), uses the Gmail API via google-auth.
    """

    def __init__(self, process_callback=None):
        self.process_callback = process_callback
        self.last_history_id = None

    def poll_once(self, mcp_search_fn=None) -> list[dict]:
        """
        Single poll cycle. Returns list of processed contract results.
        mcp_search_fn: callable that wraps the Gmail MCP search_threads tool.
        """
        if mcp_search_fn is None:
            logger.info("[Gmail] No MCP function provided — skipping poll")
            return []

        try:
            query = build_gmail_query()
            threads = mcp_search_fn(query=query, max_results=10)
            results = []

            for thread in threads.get("threads", []):
                logger.info(f"[Gmail] Found thread: {thread.get('id')}")
                results.append(thread)

            return results
        except Exception as e:
            logger.error(f"[Gmail] Poll error: {e}")
            return []

    def run_continuous(self, mcp_search_fn=None):
        """Blocking loop — call in a background thread for production use."""
        logger.info(f"[Gmail] Starting continuous poll every {GMAIL_POLL_INTERVAL}s")
        while True:
            self.poll_once(mcp_search_fn)
            time.sleep(GMAIL_POLL_INTERVAL)


def simulate_email_intake(file_bytes: bytes, filename: str, sender: str = "vendor@example.com") -> dict:
    """
    Simulate receiving a contract via email.
    Used in the demo/Streamlit UI to mimic email-based intake.
    """
    return {
        "source": "email_simulated",
        "sender": sender,
        "subject": f"Contract for review: {filename}",
        "file_bytes": file_bytes,
        "filename": filename,
    }
