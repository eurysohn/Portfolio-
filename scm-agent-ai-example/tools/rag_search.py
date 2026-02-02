from typing import Dict, List, Optional

from tools.rag_index import search_index


def search(query: str, top_k: int = 3, domain: Optional[str] = None) -> List[Dict]:
    results = search_index(query=query, top_k=top_k)
    return [
        {
            "chunk_id": r["chunk_id"],
            "source": r["source_id"],
            "score": r["score"],
            "text": r["text"],
            "page_text": r["page_text"],
        }
        for r in results
    ]
