"""
chatbot/rag.py
──────────────
RAG engine for the Homexo property chatbot.

• build_property_text()     → creates a rich text snippet from a Property obj
• get_embedding()           → calls OpenAI text-embedding-3-small
• search_properties()       → pgvector cosine similarity search
• generate_response()       → GPT-4o chat with retrieved context
"""

import json
import logging
import os
from typing import Optional

from django.conf import settings

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM   = 1536
CHAT_MODEL      = "gpt-4o-mini"          # cheap + fast; swap to gpt-4o if needed
MAX_CONTEXT_PROPS = 5


# ─── OpenAI Client (lazy init) ────────────────────────────────────────────────
_openai_client = None

def _get_client():
    global _openai_client
    if _openai_client is None:
        try:
            from openai import OpenAI
            api_key = getattr(settings, 'OPENAI_API_KEY', None) or os.environ.get('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY is not set in settings or environment.")
            _openai_client = OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("openai package is not installed. Run: pip install openai")
    return _openai_client


# ─── Text Builder ─────────────────────────────────────────────────────────────
def build_property_text(prop) -> str:
    """
    Converts a Property model instance into a rich text blob used for embedding.
    The more descriptive this is, the better the similarity search.
    """
    parts = [
        f"Title: {prop.title}",
        f"Type: {prop.get_property_type_display()}",
        f"Listing: {prop.get_listing_type_display()}",
        f"Location: {prop.locality}, {prop.city}, {prop.state}",
        f"Price: {prop.display_price}",
        f"BHK: {prop.get_bhk_display() if prop.bhk else 'N/A'}",
    ]
    if prop.area_sqft:
        parts.append(f"Area: {prop.area_sqft} sq.ft")
    if prop.bedrooms:
        parts.append(f"Bedrooms: {prop.bedrooms}, Bathrooms: {prop.bathrooms}")
    if prop.construction_status:
        parts.append(f"Status: {prop.get_construction_status_display()}")
    if prop.furnishing:
        parts.append(f"Furnishing: {prop.get_furnishing_display()}")
    if prop.developer:
        parts.append(f"Developer: {prop.developer.name}")
    if prop.description:
        parts.append(f"Description: {prop.description[:500]}")
    if prop.rera_approved:
        parts.append("RERA Approved: Yes")
    if prop.is_exclusive:
        parts.append("Exclusive listing")
    if prop.is_signature:
        parts.append("Signature/Ultra-premium collection")

    # Amenities
    features = list(prop.features.values_list('name', flat=True)[:10])
    if features:
        parts.append(f"Amenities: {', '.join(features)}")

    return "\n".join(parts)


# ─── Embedding ────────────────────────────────────────────────────────────────
def get_embedding(text: str) -> list[float]:
    """Returns a 1536-dim embedding vector for the given text."""
    client = _get_client()
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text.replace("\n", " "),
    )
    return response.data[0].embedding


# ─── Vector Search ────────────────────────────────────────────────────────────
def search_properties(query: str, top_k: int = MAX_CONTEXT_PROPS):
    """
    Embeds the user query and performs cosine similarity search against
    stored property embeddings using pgvector.

    Returns a queryset of matching Property objects (or [] on error).
    """
    from properties.models import Property
    from chatbot.models import PropertyEmbedding

    try:
        from pgvector.django import CosineDistance
    except ImportError:
        logger.warning("pgvector not available — falling back to keyword search.")
        return Property.objects.filter(status='active').order_by('-is_featured')[:top_k]

    try:
        query_vec = get_embedding(query)
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        return Property.objects.filter(status='active').order_by('-is_featured')[:top_k]

    try:
        # Find the top_k most similar embeddings
        similar = (
            PropertyEmbedding.objects
            .annotate(distance=CosineDistance('embedding', query_vec))
            .order_by('distance')
            .select_related('property')[:top_k]
        )
        return [pe.property for pe in similar if pe.property.status == 'active']
    except Exception as e:
        logger.error(f"pgvector search error: {e}")
        return Property.objects.filter(status='active').order_by('-is_featured')[:top_k]


# ─── Response Generator ───────────────────────────────────────────────────────
def generate_response(user_message: str, history: list[dict] | None = None) -> dict:
    """
    Full RAG pipeline:
      1. Semantic search for relevant properties
      2. Build context from retrieved properties
      3. Call GPT to generate a natural response
      4. Return response + matched property data
    """
    history = history or []

    # Retrieve similar properties
    matched_props = search_properties(user_message)

    # Build context string
    context_blocks = []
    for i, prop in enumerate(matched_props, 1):
        context_blocks.append(
            f"[Property {i}]\n"
            f"ID: {prop.id}\n"
            f"Slug: {prop.slug}\n"
            f"{build_property_text(prop)}"
        )
    context = "\n\n".join(context_blocks) if context_blocks else "No specific properties found."

    system_prompt = f"""You are Urvashi, a warm, knowledgeable, and professional AI property consultant for Homexo — India's premier luxury real estate platform.

Your personality:
- Speak in a friendly yet sophisticated tone
- Be proactive: ask clarifying questions if needed
- Always reference specific properties when relevant
- Express prices in Indian format (Lakhs/Crores)
- Never make up prices or details not in the context

When recommending properties, always mention:
- Property name, location, price, and BHK configuration
- Key amenities or USPs
- A direct link hint so the user can view the listing

Available Properties (retrieved from our database for this query):
─────────────────────────────────────────────────────
{context}
─────────────────────────────────────────────────────

If the user's query is unrelated to real estate, politely steer the conversation back.
If no properties match, acknowledge this and ask for different preferences.
Always end with a helpful follow-up question or call to action."""

    messages = [{"role": "system", "content": system_prompt}]

    # Add recent history (last 6 turns to stay within context)
    for msg in history[-6:]:
        messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": user_message})

    client = _get_client()
    try:
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            max_tokens=800,
            temperature=0.7,
        )
        reply = response.choices[0].message.content
    except Exception as e:
        logger.error(f"Chat completion error: {e}")
        reply = "I'm having trouble connecting right now. Please try again in a moment."

    # Serialize property data for the front-end cards
    props_data = []
    for prop in matched_props:
        primary_img = prop.primary_image
        props_data.append({
            "id":         prop.id,
            "slug":       prop.slug,
            "title":      prop.title,
            "locality":   prop.locality,
            "city":       prop.city,
            "price":      prop.display_price,
            "bhk":        prop.get_bhk_display() if prop.bhk else "",
            "area_sqft":  prop.area_sqft,
            "property_type": prop.get_property_type_display(),
            "image_url":  primary_img.image.url if primary_img and primary_img.image else "",
            "url":        prop.get_absolute_url(),
            "is_featured": prop.is_featured,
            "is_signature": prop.is_signature,
        })

    return {
        "reply":      reply,
        "properties": props_data,
    }
