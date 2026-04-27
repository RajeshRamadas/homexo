"""
chatbot/rag/embedder.py
────────────────────────
Local sentence-transformer embedder (all-MiniLM-L6-v2, 384-dim).
No API key needed — model downloads on first use (~90 MB).
"""

import os
from functools import lru_cache

_model = None


def _get_model():
    """Load and cache the SentenceTransformer model (lazy, singleton)."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        model_name = os.environ.get('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
        _model = SentenceTransformer(model_name)
    return _model


@lru_cache(maxsize=512)
def embed_query(text: str) -> list:
    """
    Encode a natural-language query to a 384-dim unit vector.
    Cached to avoid recomputing identical queries.
    """
    vec = _get_model().encode(text, normalize_embeddings=True)
    return vec.tolist()


def embed_property(prop) -> list:
    """
    Build a rich text representation of a Homexo Property instance
    and encode it to a 384-dim vector.
    """
    features = ', '.join(prop.features.values_list('name', flat=True)[:10])
    connectivity = ', '.join(
        prop.connectivity.values_list('name', flat=True)[:5]
    )

    text = (
        f"{prop.title} in {prop.locality}, {prop.city}. "
        f"Type: {prop.get_property_type_display()}. "
        f"Price: {prop.display_price}. "
        f"{prop.get_bhk_display() if prop.bhk else ''} "
        f"{str(prop.area_sqft) + ' sqft' if prop.area_sqft else ''}. "
        f"{prop.description[:300] if prop.description else ''}. "
        f"Amenities: {features}. "
        f"Nearby: {connectivity}."
    )
    vec = _get_model().encode(text, normalize_embeddings=True)
    return vec.tolist()
