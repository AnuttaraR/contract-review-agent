import json
import os
import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from app.agent.prompts import EXTRACTION_SYSTEM_PROMPT, EXTRACTION_USER_PROMPT, RAG_ENRICHMENT_PROMPT
from app.knowledge_base.query import query_knowledge_base, build_rag_query

MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
_client = None


def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY environment variable is not set. Add it to your .env file.")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def extract_from_text(text: str) -> dict:
    """Extract structured contract data from text using Claude."""
    prompt = EXTRACTION_USER_PROMPT.format(document_text=text[:12000])

    response = get_client().messages.create(
        model=MODEL,
        max_tokens=4096,
        temperature=0,
        system=EXTRACTION_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()
    return _parse_json_response(raw)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def extract_from_image(image_b64: str, media_type: str) -> dict:
    """Extract structured contract data from an image using Claude vision."""
    response = get_client().messages.create(
        model=MODEL,
        max_tokens=4096,
        temperature=0,
        system=EXTRACTION_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": EXTRACTION_USER_PROMPT.format(document_text="[See image above]"),
                    },
                ],
            }
        ],
    )

    raw = response.content[0].text.strip()
    return _parse_json_response(raw)


@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=2, max=8))
def enrich_with_rag(extracted: dict) -> dict:
    """Use RAG context + Claude to validate extracted data against internal policies."""
    rag_query = build_rag_query(extracted)
    rag_context = query_knowledge_base(rag_query, n_results=6)

    prompt = RAG_ENRICHMENT_PROMPT.format(
        contract_json=json.dumps(extracted, indent=2),
        rag_context=rag_context,
    )

    response = get_client().messages.create(
        model=MODEL,
        max_tokens=4096,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()
    return _parse_json_response(raw)


def process_document(parsed: dict) -> dict:
    """
    Full pipeline: parse → extract → RAG enrich.
    parsed = output of intake/parser.py parse_document()
    Returns complete processing result dict.
    """
    file_type = parsed["file_type"]

    if file_type == "image":
        extracted = extract_from_image(parsed["image_b64"], parsed["image_media_type"])
    else:
        extracted = extract_from_text(parsed["raw_text"])

    enrichment = enrich_with_rag(extracted)

    final_confidence = enrichment.get(
        "adjusted_confidence_score",
        extracted.get("confidence_score", 0.5)
    )

    return {
        "extracted": extracted,
        "enrichment": enrichment,
        "confidence_score": final_confidence,
        "file_type": file_type,
        "raw_text": parsed.get("raw_text", ""),
    }


def _parse_json_response(raw: str) -> dict:
    """Strip markdown fences and parse JSON."""
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(raw[start:end])
            except Exception:
                pass
        raise ValueError(f"Failed to parse Claude response as JSON: {e}\nRaw: {raw[:500]}")
