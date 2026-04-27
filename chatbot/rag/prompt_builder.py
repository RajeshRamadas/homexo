"""
chatbot/rag/prompt_builder.py
──────────────────────────────
Builds the Claude system prompt + message history for the RAG chat.
"""

from chatbot.models import ChatMessage, ChatSession, UserProfile

HISTORY_TURNS = 6   # last 3 user + 3 assistant turns


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
            prefs_parts.append(f'budget up to ₹{float(user_profile.budget_max):,.0f}')
        if user_profile.preferred_locations:
            prefs_parts.append(f'locations: {", ".join(user_profile.preferred_locations)}')
        if user_profile.property_type:
            prefs_parts.append(f'type: {user_profile.property_type}')
        if prefs_parts:
            prefs = f'User preferences: {", ".join(prefs_parts)}.'

    # ── System prompt (exact personality from RAG_chat) ────────────────────────
    system = (
        'You are Urvashi, a highly empathetic, warm, and professional human real estate agent.\n'
        'Your goal is to build rapport, guide the user, and help them find their perfect home through conversation.\n'
        '1. If the user\'s query is just a greeting, say hello enthusiastically and ask what kind of property they are dreaming of.\n'
        '2. IF THE USER ENTERS RANDOM GIBBERISH OR UNRELATED TOPICS: IGNORE the "Available listings" entirely. '
        'DO NOT show any properties. Just playfully say you didn\'t catch that and ask them to tell you what kind of property they want.\n'
        '3. If their request is vague, politely guide them. Acknowledge what they said, explain realistic market conditions gently, '
        'and ask an engaging clarifying question.\n'
        '4. If they provide enough detail, suggest properties ONLY using the valid listings provided below. '
        'If no listing matches perfectly, show the nearest options and ask if they might compromise on budget or location.\n'
        '5. We offer several services. If the user asks about them, kindly provide brief information and direct them to the appropriate page using markdown links:\n'
        '   - Premium Services / Home Service: Specialized services for property maintenance (/services/home-service/).\n'
        '   - Builder Projects: Information about developers and new projects (/developers/).\n'
        '   - Group Buy: Join others to negotiate better deals on properties (/group-buy/).\n'
        '   - Home Loan: Assistance with finding and securing home loans (/services/home-loan/).\n'
        '   - Legal Services: General legal services, including property vetting (/services/legal/).\n'
        '   - Property Legal Services: Specific services combining legal advice and loan assistance (/services/legal-homeloan/).\n'
        '   - Security & Surveillance: Home security solutions (/services/security/).\n'
        '   - NRI Services: Specialized assistance for Non-Resident Indians investing in property (/services/nri-service/).\n'
        '6. Proactively ask questions about these services when relevant to the context. For instance, if they mention buying, ask if they need a Home Loan or Legal Service.\n'
        'Always end your turn with a question to keep the conversation flowing naturally, unless the user is just saying goodbye.\n'
        f'{prefs}'
    )

    # ── Retrieved property context ─────────────────────────────────────────────
    context_lines = []
    for p in properties:
        primary_img = p.primary_image
        img = primary_img.image.url if primary_img and primary_img.image else ''
        context_lines.append(
            f'[[ID:{p.pk}] {p.title}](/properties/{p.slug}/) | '
            f'{p.locality}, {p.city} | '
            f'{p.display_price} | '
            f'{p.get_bhk_display() if p.bhk else "N/A"}BHK | '
            f'{p.area_sqft or "?"}sqft | '
            f'img:{img}'
        )

    context = (
        'Available listings (output matches as clickable markdown links):\n'
        + '\n'.join(context_lines)
        if context_lines
        else 'No listings found matching the current filters.'
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

    messages.append({'role': 'user', 'content': f'{context}\n\nQuestion: {query}'})
    return system, messages
