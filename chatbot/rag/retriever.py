"""
chatbot/rag/retriever.py
─────────────────────────
pgvector cosine similarity search with natural-language budget & location parsing.

Key improvement: `_parse_query_filters()` extracts price limits and BHK/locality
hints directly from the user's message and applies them as hard SQL WHERE clauses
BEFORE the vector similarity ranking — so "under 2 Cr" actually filters results.
"""

import os
import re
from django.db import connection
from .embedder import embed_query

TOP_K     = int(os.environ.get('TOP_K', 5))
THRESHOLD = float(os.environ.get('SIMILARITY_THRESHOLD', 0.20))   # lowered: 384-dim vectors score lower

# ── Indian price parsing ───────────────────────────────────────────────────────

# Multipliers
_LAKH = 1_00_000
_CR   = 1_00_00_000

def _to_rupees(number: float, unit: str) -> float:
    """Convert a parsed number + unit string to raw rupees."""
    unit = unit.lower().strip()
    if 'cr' in unit or 'crore' in unit:
        return number * _CR
    if 'l' in unit or 'lac' in unit or 'lakh' in unit:
        return number * _LAKH
    return number   # assume already in rupees if no unit


# Pattern: "2 Cr", "1.5 crore", "80 lakh", "80L", "80 lac" etc.
_PRICE_RE = re.compile(
    r'(\d+(?:\.\d+)?)\s*(cr(?:ore)?s?|lakh?s?|lac|l)\b',
    re.IGNORECASE
)

# "under X", "below X", "less than X", "within X", "upto X", "up to X", "maximum X", "max X", "budget X"
_UPPER_PAT = re.compile(
    r'(?:under|below|less\s+than|within|up\s*to|upto|maximum|max|budget(?:\s+of)?|budget\s+is|not\s+more\s+than|no\s+more\s+than)'
    r'\s+(?:rs\.?\s*)?(\d+(?:\.\d+)?)\s*(cr(?:ore)?s?|lakh?s?|lac|l)\b',
    re.IGNORECASE
)

# "above X", "more than X", "minimum X", "min X"
# NOTE: uses negative lookbehind for the upper-bound keywords to avoid overlap
_LOWER_PAT = re.compile(
    r'(?<!under\s)(?<!below\s)(?<!within\s)'
    r'(?:above|more\s+than|minimum|min|at\s+least|starting\s+from|from)'
    r'\s+(?:rs\.?\s*)?(\d+(?:\.\d+)?)\s*(cr(?:ore)?s?|lakh?s?|lac|l)\b',
    re.IGNORECASE
)

# "X to Y Cr" range
_RANGE_PAT = re.compile(
    r'(\d+(?:\.\d+)?)\s*(cr(?:ore)?s?|lakh?s?|lac|l)?\s*(?:to|-)\s*'
    r'(\d+(?:\.\d+)?)\s*(cr(?:ore)?s?|lakh?s?|lac|l)\b',
    re.IGNORECASE
)

# BHK: "2bhk", "2 bhk", "2 BHK"
_BHK_RE = re.compile(r'(\d)\s*bhk', re.IGNORECASE)


def _parse_query_filters(query: str) -> dict:
    """
    Extract hard budget / BHK constraints from a natural-language query.
    Returns dict with optional keys: budget_max, budget_min, bhk
    """
    result = {}
    q = query.lower()

    # Strip negation phrases so they don't confuse _LOWER_PAT
    # "not more than" / "no more than" → handled by _UPPER_PAT, remove from lower search
    q_for_lower = re.sub(
        r'(not|no)\s+more\s+than\s+[\d.]+\s*(?:cr(?:ore)?s?|lakh?s?|lac|l)\b',
        '', q, flags=re.IGNORECASE
    )

    # ── Range first ("1 to 2 Cr") ─────────────────────────────────────────────
    m = _RANGE_PAT.search(q)
    if m:
        n1, u1, n2, u2 = m.group(1), m.group(2) or m.group(4), m.group(3), m.group(4)
        result['budget_min'] = _to_rupees(float(n1), u1)
        result['budget_max'] = _to_rupees(float(n2), u2)
    else:
        # ── Upper bound ("under 2 Cr") ─────────────────────────────────────────
        m = _UPPER_PAT.search(q)
        if m:
            result['budget_max'] = _to_rupees(float(m.group(1)), m.group(2))

        # ── Lower bound ("above 80L") — search in cleaned string ──────────────
        m = _LOWER_PAT.search(q_for_lower)
        if m:
            result['budget_min'] = _to_rupees(float(m.group(1)), m.group(2))

    # ── BHK hint ("3BHK") ─────────────────────────────────────────────────────
    bhk_match = _BHK_RE.search(q)
    if bhk_match:
        result['bhk'] = int(bhk_match.group(1))

    return result


# ── Main retriever ─────────────────────────────────────────────────────────────

def retrieve(query: str, user_profile=None) -> list:
    """
    Embed the query and find the top-k most similar active properties.

    Hard SQL filters applied (in priority order):
      1. Query-extracted budget / BHK constraints
      2. UserProfile saved preferences (budget, locations)

    Args:
        query:        Natural-language search query from the user
        user_profile: chatbot.models.UserProfile (optional saved preferences)

    Returns:
        List of properties.models.Property objects ordered by similarity.
    """
    from properties.models import Property

    # ── Embed query ────────────────────────────────────────────────────────────
    vec     = embed_query(query)
    vec_str = '[' + ','.join(str(v) for v in vec) + ']'

    # ── Extract hard price filters from the query itself ───────────────────────
    query_filters = _parse_query_filters(query)

    filters = ["p.status = 'active'"]
    params  = []

    # Budget from query text takes precedence over saved profile
    budget_max = query_filters.get('budget_max')
    budget_min = query_filters.get('budget_min')

    # Fall back to saved profile if query didn't mention a budget
    if budget_max is None and user_profile and user_profile.budget_max:
        budget_max = float(user_profile.budget_max)
    if budget_min is None and user_profile and user_profile.budget_min:
        budget_min = float(user_profile.budget_min)

    if budget_max is not None:
        filters.append('p.price <= %s')
        params.append(budget_max)
    if budget_min is not None:
        filters.append('p.price >= %s')
        params.append(budget_min)

    # BHK filter (query-extracted) — maps to bedrooms column
    bhk = query_filters.get('bhk')
    if bhk:
        filters.append('p.bedrooms = %s')
        params.append(bhk)

    # Location filter from saved profile
    if user_profile and user_profile.preferred_locations:
        if not any('locality' in f for f in filters):
            placeholders = ','.join(['%s'] * len(user_profile.preferred_locations))
            filters.append(f'p.locality IN ({placeholders})')
            params.extend(user_profile.preferred_locations)

    where = 'WHERE ' + ' AND '.join(filters)

    sql = f'''
        SELECT e.property_id,
               1 - (e.embedding <=> %s::vector) AS score
        FROM   chatbot_propertyembedding e
        JOIN   properties_property p ON p.id = e.property_id
        {where}
        ORDER BY e.embedding <=> %s::vector
        LIMIT %s
    '''
    all_params = [vec_str] + params + [vec_str, TOP_K]

    with connection.cursor() as cur:
        cur.execute(sql, all_params)
        rows = cur.fetchall()

    # ── Filter by similarity threshold, with fallback ──────────────────────────
    ids = [r[0] for r in rows if r[1] >= THRESHOLD]
    if not ids and rows:
        # If no result clears the threshold, return whatever SQL gave us
        # (the price filter is already applied — these ARE within budget)
        ids = [r[0] for r in rows[:TOP_K]]

    return list(
        Property.objects
        .filter(pk__in=ids, status='active')
        .prefetch_related('images', 'features')
        .select_related('developer')
        .order_by('-is_featured', '-created_at')
    ) if ids else []
