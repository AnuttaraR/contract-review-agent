"""
BM25-based knowledge base retrieval.
Pure Python, zero native DLL dependencies — works anywhere.
Sufficient quality for our 5-document internal policy knowledge base.
"""
import os
import re
import glob
import pickle

from rank_bm25 import BM25Okapi

KNOWLEDGE_DOCS_DIR = os.path.join(os.path.dirname(__file__), "../../knowledge_docs")
CACHE_PATH = os.getenv("KB_CACHE_PATH", "./kb_bm25.pkl")

_store = None


def _tokenize(text: str) -> list[str]:
    """Simple word tokeniser: lowercase, strip punctuation."""
    return re.findall(r"\b[a-z0-9]+\b", text.lower())


def _chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> list[str]:
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start += chunk_size - overlap
    return chunks


class BM25Store:
    def __init__(self, texts: list[str], metadatas: list[dict], bm25: BM25Okapi):
        self.texts = texts
        self.metadatas = metadatas
        self.bm25 = bm25

    def query(self, query_text: str, n_results: int = 5) -> list[dict]:
        tokens = _tokenize(query_text)
        scores = self.bm25.get_scores(tokens)

        top_n = min(n_results, len(scores))
        import numpy as _np
        top_indices = _np.argsort(scores)[::-1][:top_n]

        return [
            {
                "text": self.texts[i],
                "metadata": self.metadatas[i],
                "score": float(scores[i]),
            }
            for i in top_indices
            if scores[i] > 0
        ]

    def count(self) -> int:
        return len(self.texts)


def load_knowledge_base(force_reload: bool = False) -> BM25Store:
    global _store

    if not force_reload and _store is not None:
        return _store

    cache_path = os.path.abspath(CACHE_PATH)

    if not force_reload and os.path.exists(cache_path):
        print("[KB] Loading from cache...")
        with open(cache_path, "rb") as f:
            _store = pickle.load(f)
        print(f"[KB] {_store.count()} chunks loaded from cache.")
        return _store

    docs_path = os.path.abspath(KNOWLEDGE_DOCS_DIR)
    md_files = sorted(glob.glob(os.path.join(docs_path, "*.md")))

    if not md_files:
        print(f"[KB] No docs found in {docs_path}")
        _store = BM25Store([], [], BM25Okapi([["empty"]]))
        return _store

    print(f"[KB] Indexing {len(md_files)} documents...")
    all_texts = []
    all_metas = []
    all_token_lists = []

    for filepath in md_files:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        fname = os.path.basename(filepath)
        chunks = _chunk_text(content)
        for i, chunk in enumerate(chunks):
            all_texts.append(chunk)
            all_metas.append({"source": fname, "chunk_index": i})
            all_token_lists.append(_tokenize(chunk))

    bm25 = BM25Okapi(all_token_lists)
    _store = BM25Store(all_texts, all_metas, bm25)

    with open(cache_path, "wb") as f:
        pickle.dump(_store, f)

    print(f"[KB] Indexed {_store.count()} chunks from {len(md_files)} files.")
    return _store


def get_store() -> BM25Store:
    global _store
    if _store is None:
        _store = load_knowledge_base()
    return _store
