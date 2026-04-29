"""
chatbot/rag/retriever.py
─────────────────────────
pgvector cosine similarity search with natural-language budget, BHK,
and location parsing.

KEY FIX (2026-04-29):
  psycopg2 + pgvector returns 0 rows when %s::vector is bound *alongside*
  integer/float params in the same positional query. Fixed by using a
  subquery that binds vec_str exactly ONCE in SELECT, letting the outer
  query do ORDER + LIMIT with no additional vector binding.

Other improvements:
  - bangalore ↔ bengaluru alias (DB stores 'Bengaluru')
  - BHK is now a soft filter with 4-tier progressive fallback
  - Location fuzzy matching handles typos
"""

import difflib
import os
import re
from django.db import connection
from .embedder import embed_query

TOP_K     = int(os.environ.get('TOP_K', 8))
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
    # Major cities — include both spellings of Bangalore/Bengaluru
    'bangalore', 'bengaluru', 'mumbai', 'hyderabad', 'pune', 'chennai',
    'delhi', 'noida', 'gurgaon', 'gurugram', 'kolkata', 'ahmedabad',
    'surat', 'jaipur', 'lucknow', 'kochi', 'coimbatore', 'nagpur',
    'indore', 'bhopal', 'vizag', 'visakhapatnam', 'mysore', 'mysuru',
    # Bangalore micro-markets
    'whitefield', 'koramangala', 'hsr layout', 'electronic city',
    'sarjapur', 'hebbal', 'yelahanka', 'jp nagar', 'marathahalli',
    'indiranagar', 'jayanagar', 'banashankari', 'btm layout', 'bellandur',
    'domlur', 'old airport road', 'rajarajeshwari nagar', 'nagarbhavi',
    'sadashivanagar', 'devanahalli', 'outer ring road', 'sarjapur road',
    # Mumbai
    'bandra', 'andheri', 'powai', 'thane', 'kharghar', 'navi mumbai',
    'malad', 'goregaon', 'kandivali', 'borivali', 'dahisar', 'mira road',
    # Pune
    'hinjewadi', 'baner', 'kharadi', 'wakad', 'hadapsar', 'viman nagar',
    'aundh', 'pimple saudagar', 'nibm', 'magarpatta',
    # Hyderabad
    'gachibowli', 'hitech city', 'kondapur', 'miyapur', 'kukatpally',
    'madhapur', 'manikonda', 'nallagandla', 'kokapet',
]

# bangalore ↔ bengaluru: both spellings must match the DB's 'Bengaluru'
_CITY_ALIASES = {
    'bangalore': ['bangalore', 'bengaluru'],
    'bengaluru': ['bangalore', 'bengaluru'],
}


def _fuzzy_match_location(query: str) -> str | None:
    """
    Two-tier location detection:
    1. Exact substring match (handles correct spelling and multi-word)
    2. Per-word fuzzy match using difflib (handles typos)

    Returns the corrected canonical location name, or None.
    """
    q_lower = query.lower()

    # Tier 1: exact substring
    for loc in _KNOWN_LOCATIONS:
        if loc in q_lower:
            return loc

    # Tier 2: fuzzy per-word match
    words = re.findall(r'[a-z]+', q_lower)

    for word in words:
        if len(word) < 4:
            continue
        matches = difflib.get_close_matches(word, _KNOWN_LOCATIONS, n=1, cutoff=0.82)
        if matches:
            return matches[0]

    for i in range(len(words) - 1):
        phrase = f'{words[i]} {words[i+1]}'
        matches = difflib.get_close_matches(phrase, _KNOWN_LOCATIONS, n=1, cutoff=0.80)
        if matches:
            return matches[0]

    return None


def _parse_query_filters(query: str) -> dict:
    """
    Extract budget / BHK / location constraints from a natural-language query.
    """
    result = {}
    q = query.lower()

    q_for_lower = re.sub(
        r'(not|no)\s+more\s+than\s+[\d.]+\s*(?:cr(?:ore)?s?|lakh?s?|lac|l)\b',
        '', q, flags=re.IGNORECASE
    )

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

    bhk_match = _BHK_RE.search(q)
    if bhk_match:
        result['bhk'] = int(bhk_match.group(1))

    loc = _fuzzy_match_location(query)
    if loc:
        result['location'] = loc

    return result


# ── Main retriever ─────────────────────────────────────────────────────────────

def retrieve(query: str, user_profile=None) -> list:
    """
    Embed the query and find the top-k most similar active properties.

    Hard SQL filters  : status=active, price budget
    Soft SQL filters  : location/city (bangalore↔bengaluru aliased), BHK
    Fallback strategy : loc+bhk → bhk-only → loc-only → no soft filters

    KEY FIX: psycopg2 + pgvector returns 0 rows when %s::vector is bound
    alongside integer/float params in the same positional query. Fixed by
    using a subquery that binds vec_str exactly ONCE in the SELECT clause.
    """
    from properties.models import Property

    vec     = embed_query(query)
    vec_str = '[' + ','.join(str(v) for v in vec) + ']'

    query_filters = _parse_query_filters(query)

    # ── Hard budget filters (price must be within range) ─────────────────────
    hard_filters  = ["p.status = 'active'"]
    budget_params = []   # only price params — no integers that confuse pgvector

    budget_max = query_filters.get('budget_max')
    budget_min = query_filters.get('budget_min')

    if budget_max is None and user_profile and user_profile.budget_max:
        budget_max = float(user_profile.budget_max)
    if budget_min is None and user_profile and user_profile.budget_min:
        budget_min = float(user_profile.budget_min)

    if budget_max is not None:
        hard_filters.append('p.price <= %s')
        budget_params.append(budget_max)
    if budget_min is not None:
        hard_filters.append('p.price >= %s')
        budget_params.append(budget_min)

    # ── Soft filters ─────────────────────────────────────────────────────────
    bhk      = query_filters.get('bhk')
    location = query_filters.get('location')

    if not location and user_profile and user_profile.preferred_locations:
        location = user_profile.preferred_locations[0].lower()

    # Expand to alias variants (bangalore ↔ bengaluru)
    loc_variants = _CITY_ALIASES.get(location, [location]) if location else []

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _build_loc_clause(variants):
        """Build an OR clause for locality/city ILIKE matching."""
        if not variants:
            return None, []
        parts, p = [], []
        for v in variants:
            parts.append('(LOWER(p.locality) LIKE %s OR LOWER(p.city) LIKE %s)')
            p += [f'%{v}%', f'%{v}%']
        return '(' + ' OR '.join(parts) + ')', p

    def _run_query(extra_filters, extra_params):
        """
        Run vector similarity query.

        Binds vec_str ONCE (in subquery SELECT) — avoids psycopg2+pgvector
        zero-row bug that occurs when vector params are mixed with integer params.

        Param layout: [vec_str, *budget_params, *extra_params, TOP_K]
        """
        all_filters  = hard_filters + extra_filters
        where_clause = 'WHERE ' + ' AND '.join(all_filters)

        sql = f'''
            SELECT sub.property_id, sub.score
            FROM (
                SELECT e.property_id,
                       (1 - (e.embedding <=> %s::vector)) AS score
                FROM   chatbot_propertyembedding e
                JOIN   properties_property p ON p.id = e.property_id
                {where_clause}
            ) sub
            ORDER BY sub.score DESC
            LIMIT %s
        '''
        # vec_str is the first param (subquery), budget/extra params go to WHERE,
        # TOP_K is the last param (LIMIT). No second vector binding needed.
        all_params = [vec_str] + budget_params + extra_params + [TOP_K]
        with connection.cursor() as cur:
            cur.execute(sql, all_params)
            return cur.fetchall()

    def _attempt(with_loc, with_bhk):
        extra_f, extra_p = [], []
        loc_clause, lp = _build_loc_clause(loc_variants)
        if with_loc and loc_clause:
            extra_f.append(loc_clause)
            extra_p += lp
        if with_bhk and bhk:
            extra_f.append('p.bedrooms = %s')
            extra_p.append(bhk)
        return _run_query(extra_f, extra_p)

    # ── 4-tier progressive fallback ───────────────────────────────────────────
    rows = []

    if location and bhk:
        rows = _attempt(with_loc=True, with_bhk=True)

    if not rows and bhk:
        rows = _attempt(with_loc=False, with_bhk=True)

    if not rows and location:
        rows = _attempt(with_loc=True, with_bhk=False)

    if not rows:
        rows = _attempt(with_loc=False, with_bhk=False)

    # ── Threshold filter with top-3 fallback ─────────────────────────────────
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
