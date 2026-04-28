"""
chatbot/rag/retriever.py
─────────────────────────
pgvector cosine similarity search with natural-language budget, BHK,
and location parsing.

Improvements:
  - Location / city extracted from query text as a soft SQL ILIKE filter
  - TOP_K increased to 8 for richer context
  - Threshold lowered with smarter fallback
  - BHK and bedrooms correctly mapped to the 'bedrooms' DB column
"""

import os
import re
from django.db import connection
from .embedder import embed_query

TOP_K     = int(os.environ.get('TOP_K', 8))           # more candidates = better context
THRESHOLD = float(os.environ.get('SIMILARITY_THRESHOLD', 0.18))

# ── Indian price parsing ───────────────────────────────────────────────────────
_LAKH = 1_00_000
_CR   = 1_00_00_000


def _to_rupees(number: float, unit: str) -> float:
    unit = unit.lower().strip()
    if 'cr' in unit or 'crore' in unit:
        return number * _CR
    if 'l' in unit or 'lac' in unit or 'lakh' in unit:
        return number * _LAKH
    return number


_UPPER_PAT = re.compile(
    r'(?:under|below|less\s+than|within|up\s*to|upto|maximum|max|budget(?:\s+of)?|budget\s+is|not\s+more\s+than|no\s+more\s+than)'
    r'\s+(?:rs\.?\s*)?(\d+(?:\.\d+)?)\s*(cr(?:ore)?s?|lakh?s?|lac|l)\b',
    re.IGNORECASE
)

_LOWER_PAT = re.compile(
    r'(?<!under\s)(?<!below\s)(?<!within\s)'
    r'(?:above|more\s+than|minimum|min|at\s+least|starting\s+from|from)'
    r'\s+(?:rs\.?\s*)?(\d+(?:\.\d+)?)\s*(cr(?:ore)?s?|lakh?s?|lac|l)\b',
    re.IGNORECASE
)

_RANGE_PAT = re.compile(
    r'(\d+(?:\.\d+)?)\s*(cr(?:ore)?s?|lakh?s?|lac|l)?\s*(?:to|-)\s*'
    r'(\d+(?:\.\d+)?)\s*(cr(?:ore)?s?|lakh?s?|lac|l)\b',
    re.IGNORECASE
)

_BHK_RE = re.compile(r'(\d)\s*bhk', re.IGNORECASE)

# Common Indian cities / localities for soft location matching
_KNOWN_LOCATIONS = [
    'bangalore', 'bengaluru', 'mumbai', 'hyderabad', 'pune', 'chennai',
    'delhi', 'noida', 'gurgaon', 'gurugram', 'kolkata', 'ahmedabad',
    'surat', 'jaipur', 'lucknow', 'kochi', 'coimbatore', 'nagpur',
    'indore', 'bhopal', 'vizag', 'visakhapatnam', 'mysore', 'mysuru',
    # Common micro-markets / localities
    'whitefield', 'koramangala', 'hsr layout', 'electronic city',
    'sarjapur', 'hebbal', 'yelahanka', 'jp nagar', 'marathahalli',
    'bandra', 'andheri', 'powai', 'thane', 'kharghar', 'navi mumbai',
    'hinjewadi', 'baner', 'kharadi', 'wakad', 'hadapsar',
    'gachibowli', 'hitech city', 'kondapur', 'miyapur', 'kukatpally',
]


def _parse_query_filters(query: str) -> dict:
    """
    Extract hard budget / BHK constraints and soft location hints
    from a natural-language query.
    """
    result = {}
    q = query.lower()

    q_for_lower = re.sub(
        r'(not|no)\s+more\s+than\s+[\d.]+\s*(?:cr(?:ore)?s?|lakh?s?|lac|l)\b',
        '', q, flags=re.IGNORECASE
    )

    # ── Range first ────────────────────────────────────────────────────────────
    m = _RANGE_PAT.search(q)
    if m:
        n1, u1, n2, u2 = m.group(1), m.group(2) or m.group(4), m.group(3), m.group(4)
        result['budget_min'] = _to_rupees(float(n1), u1)
        result['budget_max'] = _to_rupees(float(n2), u2)
    else:
        m = _UPPER_PAT.search(q)
        if m:
            result['budget_max'] = _to_rupees(float(m.group(1)), m.group(2))
        m = _LOWER_PAT.search(q_for_lower)
        if m:
            result['budget_min'] = _to_rupees(float(m.group(1)), m.group(2))

    # ── BHK ────────────────────────────────────────────────────────────────────
    bhk_match = _BHK_RE.search(q)
    if bhk_match:
        result['bhk'] = int(bhk_match.group(1))

    # ── Location (soft match) ──────────────────────────────────────────────────
    for loc in _KNOWN_LOCATIONS:
        if loc in q:
            result['location'] = loc
            break

    return result


# ── Main retriever ─────────────────────────────────────────────────────────────

def retrieve(query: str, user_profile=None) -> list:
    """
    Embed the query and find the top-k most similar active properties.

    Hard SQL filters:
      - Status = active
      - Budget (max / min)
      - BHK / bedrooms

    Soft SQL filters (ILIKE — won't exclude if no match):
      - Location / city extracted from query text

    Returns:
        List of properties.models.Property objects ordered by similarity.
    """
    from properties.models import Property

    vec     = embed_query(query)
    vec_str = '[' + ','.join(str(v) for v in vec) + ']'

    query_filters = _parse_query_filters(query)

    # ── Hard filters (will exclude non-matching rows) ──────────────────────────
    hard_filters = ["p.status = 'active'"]
    params = []

    budget_max = query_filters.get('budget_max')
    budget_min = query_filters.get('budget_min')

    if budget_max is None and user_profile and user_profile.budget_max:
        budget_max = float(user_profile.budget_max)
    if budget_min is None and user_profile and user_profile.budget_min:
        budget_min = float(user_profile.budget_min)

    if budget_max is not None:
        hard_filters.append('p.price <= %s')
        params.append(budget_max)
    if budget_min is not None:
        hard_filters.append('p.price >= %s')
        params.append(budget_min)

    if query_filters.get('bhk'):
        hard_filters.append('p.bedrooms = %s')
        params.append(query_filters['bhk'])

    # ── Soft location hint (added to WHERE, falls back gracefully) ─────────────
    location = query_filters.get('location')
    if not location and user_profile and user_profile.preferred_locations:
        location = user_profile.preferred_locations[0].lower()

    def _run_query(extra_filters, extra_params):
        """Execute the vector similarity query with given filters."""
        all_filters = hard_filters + extra_filters
        where = 'WHERE ' + ' AND '.join(all_filters)
        sql = f'''
            SELECT e.property_id,
                   1 - (e.embedding <=> %s::vector) AS score
            FROM   chatbot_propertyembedding e
            JOIN   properties_property p ON p.id = e.property_id
            {where}
            ORDER BY e.embedding <=> %s::vector
            LIMIT %s
        '''
        all_params = [vec_str] + params + extra_params + [vec_str, TOP_K]
        with connection.cursor() as cur:
            cur.execute(sql, all_params)
            return cur.fetchall()

    # First pass: with location filter
    rows = []
    if location:
        loc_filter  = '(LOWER(p.locality) LIKE %s OR LOWER(p.city) LIKE %s)'
        loc_params  = [f'%{location}%', f'%{location}%']
        rows = _run_query([loc_filter], loc_params)

    # Second pass: without location (if first returned nothing)
    if not rows:
        rows = _run_query([], [])

    # ── Filter by threshold, with fallback to top-3 ───────────────────────────
    ids = [r[0] for r in rows if r[1] >= THRESHOLD]
    if not ids and rows:
        ids = [r[0] for r in rows[:3]]

    return list(
        Property.objects
        .filter(pk__in=ids, status='active')
        .prefetch_related('images', 'features', 'connectivity')
        .select_related('developer')
        .order_by('-is_featured', '-created_at')
    ) if ids else []

