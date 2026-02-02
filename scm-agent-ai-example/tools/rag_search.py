from typing import List, Dict, Optional

def search(query: str, top_k: int = 3, domain: Optional[str] = None) -> List[Dict]:
    # Mock RAG search results
    return [
        {
            "chunk_id": "mock_chunk_1",
            "source": "SCM Handook v1.pdf",
            "score": 0.85,
            "text": "Effective demand forecasting requires high-quality historical data and collaboration between sales and supply chain teams.",
            "page_text": "Effective demand forecasting requires high-quality historical data and collaboration between sales and supply chain teams."
        }
    ]
