"""
chatbot/views.py
─────────────────
Endpoints:
  POST /api/v1/chat/                — main RAG pipeline
  POST /api/v1/chat/preferences/   — update session preferences
  GET  /api/v1/chat/history/       — fetch conversation history for a session
"""

import json
import logging
import re

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse

from .models import ChatSession, ChatMessage, UserProfile
from .rag.retriever import retrieve, _parse_query_filters, _CR, _LAKH
from .rag.prompt_builder import build_prompt
from .rag.llm_client import call_llm

logger = logging.getLogger(__name__)


# ── Price → URL bucket mapping ────────────────────────────────────────────────
_PRICE_BUCKETS = [
    (0,           50 * _LAKH,      'under50l'),
    (50 * _LAKH,  1  * _CR,        '50l-1cr'),
    (1  * _CR,    3  * _CR,        '1cr-3cr'),
    (3  * _CR,    10 * _CR,        '3cr-10cr'),
    (10 * _CR,    None,            'above10cr'),
]

def _build_search_url(query: str, user_profile=None) -> str:
    """
    Build a /properties/ search URL from filters extracted from the chat query.
    Uses the same fuzzy-corrected _parse_query_filters as the retriever so
    typos like 'whitefieldd' resolve to 'whitefield' in the URL too.
    """
    filters = _parse_query_filters(query)

    # Merge with saved profile preferences (query takes priority)
    budget_max = filters.get('budget_max')
    budget_min = filters.get('budget_min')
    bhk        = filters.get('bhk')

    # Fuzzy-corrected location from query (already resolved by _parse_query_filters)
    location = filters.get('location')

    # Fall back to saved profile if query had no location
    if not location and user_profile and user_profile.preferred_locations:
        location = user_profile.preferred_locations[0]

    if budget_max is None and user_profile and user_profile.budget_max:
        budget_max = float(user_profile.budget_max)
    if budget_min is None and user_profile and user_profile.budget_min:
        budget_min = float(user_profile.budget_min)

    params = {}

    # Pick the best matching price bucket
    price_key = None
    if budget_max is not None:
        for low, high, key in _PRICE_BUCKETS:
            if high is None or budget_max <= high:
                price_key = key
                break
    elif budget_min is not None:
        for low, high, key in _PRICE_BUCKETS:
            if budget_min >= low:
                price_key = key   # keep overwriting — get the highest matching bucket
    if price_key:
        params['price'] = price_key

    if bhk:
        params['bhk'] = f'{bhk}bhk'
    if location:
        params['location'] = location

    if not params:
        return '/properties/'

    from urllib.parse import urlencode
    return f'/properties/?{urlencode(params)}'


def _property_card(prop) -> dict:
    """Serialize a Property to the card format expected by the frontend."""
    primary_img = prop.primary_image
    return {
        'id':           prop.id,
        'title':        prop.title,
        'location':     f'{prop.locality}, {prop.city}',
        'price':        str(prop.price),
        'display_price': prop.display_price,
        'bedrooms':     prop.bedrooms,
        'bathrooms':    prop.bathrooms,
        'area_sqft':    prop.area_sqft,
        'bhk':          prop.get_bhk_display() if prop.bhk else '',
        'amenities':    ', '.join(prop.features.values_list('name', flat=True)[:8]),
        'image_url':    (primary_img.image.url if primary_img and primary_img.image else ''),
        'url':          prop.get_absolute_url(),
        'is_featured':  prop.is_featured,
        'is_signature': prop.is_signature,
        'slug':         prop.slug,
    }


def _sanitize_ai_text(text: str) -> str:
    """
    Backend safety net: strip absolute dev-server URLs and /developers/ links
    from LLM output before sending to the frontend.
    """
    if not text:
        return text
    # Convert absolute localhost / 127.0.0.1 URLs → relative paths
    text = re.sub(
        r'https?://(127\.0\.0\.1|localhost)(:\d+)?(/\S*)',
        r'\3',
        text,
    )
    # Remove markdown links pointing to /developers/ (internal admin page)
    text = re.sub(r'\[[^\]]*\]\(/developers/[^)]*\)', '', text)
    return text



@csrf_exempt
@require_POST
def chat_view(request):
    """
    Full RAG pipeline:
    1. Resolve session + user profile
    2. Retrieve relevant properties (pgvector)
    3. Build grounded prompt
    4. Call Claude
    5. Persist conversation
    6. Return { ai_text, properties, session_id }
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_message = data.get('message', '').strip()
    if not user_message:
        return JsonResponse({'error': 'message is required'}, status=400)

    # ── Lead contact details (sent from onboarding flow) ───────────────────────
    user_name  = data.get('user_name',  '').strip()
    user_phone = data.get('user_phone', '').strip()
    preference = data.get('preference', '').strip()

    # ── Session ────────────────────────────────────────────────────────────────
    session_key = data.get('session_id') or data.get('session_key')
    if not session_key:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key

    session, _ = ChatSession.objects.get_or_create(
        session_key=session_key,
        defaults={'user': request.user if request.user.is_authenticated else None},
    )

    # Persist lead details on first message (never overwrite once set)
    dirty = []
    if user_name and not session.visitor_name:
        session.visitor_name = user_name
        dirty.append('visitor_name')
    if user_phone and not session.phone:
        session.phone = user_phone
        dirty.append('phone')
    if preference and not session.preference:
        session.preference = preference
        dirty.append('preference')
    if dirty:
        session.save(update_fields=dirty)

    # ── User profile (preferences) ─────────────────────────────────────────────
    profile, _ = UserProfile.objects.get_or_create(session_key=session_key)

    # ── RAG pipeline ──────────────────────────────────────────────────────────
    try:
        properties       = retrieve(user_message, profile)
        system, messages = build_prompt(user_message, properties, session_key, profile)
        ai_text          = call_llm(system, messages)
    except Exception as e:
        logger.error(f'RAG pipeline error: {e}', exc_info=True)
        return JsonResponse({
            'ai_text':    'I\'m sorry, something went wrong on my end. Please try again!',
            'properties': [],
            'session_id': session_key,
        })

    # ── Persist ────────────────────────────────────────────────────────────────
    ChatMessage.objects.create(session=session, role='user',      content=user_message)
    ChatMessage.objects.create(session=session, role='assistant', content=ai_text)

    # ── Sanitise ai_text (strip dev-server URLs / internal links) ─────────────
    ai_text = _sanitize_ai_text(ai_text)

    # ── Respond ────────────────────────────────────────────────────────────────
    search_url = _build_search_url(user_message, profile)

    return JsonResponse({
        'ai_text':    ai_text,
        'properties': [_property_card(p) for p in properties],
        'session_id': session_key,
        'search_url': search_url,   # link to full filtered search page
    })


@csrf_exempt
@require_POST
def update_preferences_view(request):
    """Update session-level search preferences."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    session_key = data.get('session_id') or data.get('session_key', 'anonymous')
    profile, _  = UserProfile.objects.get_or_create(session_key=session_key)

    if 'budget_max' in data:
        profile.budget_max = data['budget_max']
    if 'budget_min' in data:
        profile.budget_min = data['budget_min']
    if 'preferred_locations' in data:
        profile.preferred_locations = data['preferred_locations']
    if 'property_type' in data:
        profile.property_type = data['property_type']

    profile.save()
    return JsonResponse({'success': True, 'message': 'Preferences updated'})


@require_GET
def history_view(request):
    """
    GET /api/v1/chat/history/?session_id=<id>[&limit=40]

    Returns the stored conversation history for the given session so the
    frontend can replay it into the chat window after a page reload.
    Response shape:
      {
        "messages": [
          {"role": "user"|"assistant", "content": "...", "ts": "ISO-8601"},
          ...
        ],
        "visitor_name": "...",
        "preference": "property"|"services"|""  
      }
    """
    session_key = request.GET.get('session_id', '').strip()
    if not session_key:
        return JsonResponse({'error': 'session_id is required'}, status=400)

    limit = min(int(request.GET.get('limit', 40)), 100)  # cap at 100

    try:
        session = ChatSession.objects.filter(session_key=session_key).first()
        if not session:
            return JsonResponse({'messages': [], 'visitor_name': '', 'preference': ''})

        messages = list(
            session.messages
            .order_by('created_at')
            .values('role', 'content', 'created_at')
        )
        # Return only the last `limit` messages
        messages = messages[-limit:]

        return JsonResponse({
            'messages':     [{'role': m['role'], 'content': m['content'],
                              'ts': m['created_at'].isoformat()} for m in messages],
            'visitor_name': session.visitor_name or '',
            'preference':   session.preference   or '',
        })
    except Exception as e:
        logger.error(f'history_view error: {e}', exc_info=True)
        return JsonResponse({'messages': [], 'visitor_name': '', 'preference': ''})
