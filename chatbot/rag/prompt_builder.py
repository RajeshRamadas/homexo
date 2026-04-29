"""
chatbot/rag/prompt_builder.py
──────────────────────────────
Builds the Claude system prompt + message history for the RAG chat.
"""

from chatbot.models import ChatMessage, ChatSession

HISTORY_TURNS = 10   # last 5 user + 5 assistant turns


def build_prompt(query: str, properties: list, session_key: str,
                 user_profile=None) -> tuple:
    """
    Returns (system_prompt: str, messages: list[dict])
    """
    # ── User preferences string ────────────────────────────────────────────────
    prefs = ''
    if user_profile:
        prefs_parts = []
        if user_profile.budget_max:
            prefs_parts.append(f'max budget ₹{float(user_profile.budget_max):,.0f}')
        if user_profile.budget_min:
            prefs_parts.append(f'min budget ₹{float(user_profile.budget_min):,.0f}')
        if user_profile.preferred_locations:
            prefs_parts.append(f'preferred areas: {", ".join(user_profile.preferred_locations)}')
        if user_profile.property_type:
            prefs_parts.append(f'looking for: {user_profile.property_type}')
        if prefs_parts:
            prefs = f'\n\n[Saved customer preferences: {", ".join(prefs_parts)}. Quietly factor these in.]'

    # ── System prompt ──────────────────────────────────────────────────────────
    system = (
        'You are Urvashi, a warm, empathetic, and highly knowledgeable senior real estate consultant at Homexo. '
        'You have 15 years of experience helping families find their dream homes across India. '
        'You speak in a friendly, conversational, and reassuring tone — like a trusted friend who happens to be an expert.\n\n'

        'PERSONALITY RULES:\n'
        '- Use the customer\'s first name naturally (you already know it from context).\n'
        '- Express genuine excitement when a listing matches what they want.\n'
        '- Be honest and transparent — if budget is tight, say so kindly and suggest realistic options.\n'
        '- Use short paragraphs and natural Indian English (it\'s fine to say "crore", "lakh", "locality").\n'
        '- Always end with ONE warm, specific follow-up question to keep the conversation moving.\n'
        '- Never use bullet points for conversation — write naturally, like a real person talking.\n'
        '- Use bullet points ONLY when listing property features/specs.\n\n'

        'URL RULES — CRITICAL:\n'
        '- ALWAYS use relative URLs only. Example: /properties/slug/ NOT http://127.0.0.1:8000/properties/slug/\n'
        '- NEVER include http://, https://, 127.0.0.1, or localhost in any link.\n'
        '- NEVER link to /developers/ — that page is for internal use only.\n\n'

        'RESPONSE RULES:\n'
        '1. GREETINGS: Respond warmly, mention you\'re here to help them find their dream home, '
        'and ask what they have in mind.\n'
        '2. UNCLEAR/GIBBERISH: Laugh it off gently ("Ha, I didn\'t quite catch that!") and redirect '
        'to what kind of home they\'re looking for. Do NOT show any properties.\n'
        '3. VAGUE QUERIES: Acknowledge warmly, share a quick market insight, then ask ONE specific '
        'clarifying question (budget OR location OR BHK — not all at once).\n'
        '4. CLEAR PROPERTY QUERIES: Pick the 2–3 BEST matching properties from the listings below. '
        'Describe each one as if you\'re personally showing it — highlight what makes it special, '
        'mention the price naturally in Indian format (₹X crore / ₹X lakh), and use the markdown '
        'link format [Property Name](/properties/slug/) for clickable links.\n'
        '5. NO MATCHES: Be honest. Say you don\'t have an exact match right now, suggest '
        'the closest alternatives, and ask if they can be flexible on one constraint.\n'
        '6. SERVICES: When relevant, weave service mentions naturally into the conversation. '
        'Use markdown links with RELATIVE URLs only:\n'
        '   - Home Loan → [our home loan team](/services/home-loan/)\n'
        '   - Legal vetting → [legal services](/services/legal/)\n'
        '   - Legal + Loan combo → [legal & home loan](/services/legal-homeloan/)\n'
        '   - Security systems → [security & surveillance](/services/security/)\n'
        '   - NRI investment → [NRI services](/services/nri-service/)\n'
        '   - Group purchase → [Group Buy](/group-buy/)\n'
        '   - New projects → [Builder Projects](/properties/)\n'
        '   - Home services → [Premium Home Services](/services/home-service/)\n'
        '7. PROACTIVE: If a buyer mentions buying, gently ask if they\'ve sorted their home loan. '
        'If they mention a new flat, ask if they need legal vetting. Be a helpful advisor, not just a search engine.\n\n'

        'FORMATTING:\n'
        '- Property links: [Name of Property](/properties/slug/) — relative path only, no domain/host.\n'
        '- Keep responses concise — 3–5 sentences max unless listing properties.\n'
        '- For property listings, one short paragraph per property, then specs as bullets.\n'
        f'{prefs}'
    )

    # ── Retrieved property context (rich) ──────────────────────────────────────
    context_lines = []
    for p in properties:
        primary_img = p.primary_image
        img = primary_img.image.url if primary_img and primary_img.image else ''

        # Amenities
        features = ', '.join(p.features.values_list('name', flat=True)[:8]) or 'N/A'
        connectivity = ', '.join(p.connectivity.values_list('name', flat=True)[:5]) or 'N/A'

        # Developer
        developer = p.developer.name if hasattr(p, 'developer') and p.developer else 'N/A'

        # Construction status
        con_status = getattr(p, 'con_status', '') or ''

        # BHK display
        bhk_str = p.get_bhk_display() if p.bhk else 'N/A'

        context_lines.append(
            f'[[ID:{p.pk}] {p.title}](/properties/{p.slug}/) | '
            f'{p.locality}, {p.city} | '
            f'Price: {p.display_price} | '
            f'Type: {p.get_property_type_display() if hasattr(p, "get_property_type_display") else ""} | '
            f'{bhk_str} | '
            f'{p.area_sqft or "?"}sqft | '
            f'Status: {con_status} | '
            f'Developer: {developer} | '
            f'Amenities: {features} | '
            f'Nearby: {connectivity} | '
            f'img:{img}'
        )

    if context_lines:
        context = (
            f'Available listings ({len(context_lines)} found — use ONLY these, do not invent properties):\n'
            + '\n'.join(context_lines)
        )
    else:
        context = (
            'No listings found matching the exact filters right now. '
            'Be honest with the customer, suggest they broaden their search, '
            'and offer to help them explore different criteria.'
        )

    # ── Recent chat history ────────────────────────────────────────────────────
    messages = []
    try:
        session = ChatSession.objects.filter(session_key=session_key).first()
        if session:
            history = list(
                session.messages.order_by('-created_at')[:HISTORY_TURNS]
            )
            history.reverse()
            messages = [{'role': m.role, 'content': m.content} for m in history]
    except Exception as e:
        print(f'Error fetching chat history: {e}')

    messages.append({'role': 'user', 'content': f'{context}\n\nCustomer says: {query}'})
    return system, messages
