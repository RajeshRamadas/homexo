/**
 * Homexo — Urvashi Chat Widget
 * Ported from RAG_chat/property_search/frontend/chat.js
 * Adapted to use /api/v1/chat/ endpoint and Homexo's property URLs.
 */

// ── Session management ────────────────────────────────────────────────────────
const SESSION_ID = (() => {
    let id = localStorage.getItem('urvashi_session_id');
    if (!id) {
        id = crypto.randomUUID();
        localStorage.setItem('urvashi_session_id', id);
    }
    return id;
})();

// ── Onboarding state machine ──────────────────────────────────────────────────
// States: 'name' → 'phone' → 'preference' → 'chat'
let onboardingState = localStorage.getItem('urvashi_onboarding_done') === 'true'
    ? 'chat'
    : 'name';

const userProfile = {
    name:       localStorage.getItem('urvashi_user_name')  || '',
    phone:      localStorage.getItem('urvashi_user_phone') || '',
    preference: localStorage.getItem('urvashi_preference') || '',
};

// ── DOM refs ──────────────────────────────────────────────────────────────────
const chatbotContainer = document.getElementById('urvashi-container');
const chatWindow       = document.getElementById('urvashi-chat-window');
const messageInput     = document.getElementById('urvashi-input');
const sendBtn          = document.getElementById('urvashi-send-btn');

// ── Event listeners ────────────────────────────────────────────────────────────
if (sendBtn)     sendBtn.addEventListener('click', sendMessage);
if (messageInput) messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// ── Send message ───────────────────────────────────────────────────────────────
async function sendMessage(forceText) {
    // forceText is passed by quick-reply chips to bypass the textarea
    const text = (forceText || messageInput.value).trim();
    if (!text) return;

    // Route through onboarding only when user is typing (not a chip)
    if (!forceText && onboardingState !== 'chat') {
        handleOnboardingInput(text);
        return;
    }

    messageInput.value = '';
    sendBtn.disabled = true;
    appendMessage('user', text);

    // Typing indicator
    const typingId = appendTypingIndicator();

    try {
        const response = await fetch('/api/v1/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                message: text,
                session_id: SESSION_ID,
                user_name: userProfile.name,
                user_phone: userProfile.phone,
                preference: userProfile.preference,
            }),
        });

        removeTypingIndicator(typingId);

        if (!response.ok) {
            const err = await response.json();
            appendMessage('assistant', `Sorry, something went wrong: ${err.error || 'unknown error'}`);
            return;
        }

        const data = await response.json();

        // Append assistant response and capture the bubble element
        const assistantBubble = appendMessage('assistant', data.ai_text);

        // Render inline property cards
        renderInlinePropertyCards(assistantBubble, data.properties);

        // Render "search all" link if there are results or a non-generic search URL
        if (data.search_url && (data.properties.length > 0 || data.search_url !== '/properties/')) {
            renderSearchLink(assistantBubble, data.search_url, data.properties.length);
        }

    } catch (error) {
        removeTypingIndicator(typingId);
        console.error('Urvashi error:', error);
        appendMessage('assistant', 'Sorry, I couldn\'t connect. Please try again!');
    } finally {
        sendBtn.disabled = false;
        messageInput.focus();
    }
}

// ── Onboarding input handler ──────────────────────────────────────────────────
function handleOnboardingInput(text) {
    appendMessage('user', text);
    messageInput.value = '';

    if (onboardingState === 'name') {
        userProfile.name = text;
        localStorage.setItem('urvashi_user_name', text);
        onboardingState = 'phone';
        setTimeout(() => {
            appendMessage('assistant',
                `Nice to meet you, ${text}! 😊 Could you please share your phone number (with country code) so we can reach you? 📞\n\nFor example: +91 98765 43210 for India, +1 202 555 0123 for USA.`
            );
        }, 400);

    } else if (onboardingState === 'phone') {
        // Basic phone validation (at least 7 digits)
        const digits = text.replace(/\D/g, '');
        if (digits.length < 7) {
            appendMessage('assistant', 'Please enter a valid phone number so we can reach you. 📞');
            return;
        }
        userProfile.phone = text;
        localStorage.setItem('urvashi_user_phone', text);
        onboardingState = 'preference';
        setTimeout(() => {
            const bubble = appendMessage('assistant',
                `Perfect! Thank you, ${userProfile.name}. 🙏\n\nWhat are you looking for today?`
            );
            renderPreferenceButtons(bubble);
        }, 400);

    } else if (onboardingState === 'preference') {
        // Free-typed preference (fallback if buttons not clicked)
        finishOnboarding(text);
    }
}

// ── Preference quick-reply buttons ────────────────────────────────────────────
function renderPreferenceButtons(bubble) {
    const wrap = document.createElement('div');
    wrap.style.cssText = 'display:flex;gap:8px;flex-wrap:wrap;margin-top:10px;';

    const options = [
        { label: '🏠 Property',  value: 'property' },
        { label: '🛠️ Services',  value: 'services' },
    ];

    options.forEach(opt => {
        const btn = document.createElement('button');
        btn.textContent = opt.label;
        btn.style.cssText = [
            'padding:8px 18px', 'border-radius:20px',
            'border:1.5px solid #0D2B4E', 'background:transparent',
            'color:#0D2B4E', 'font-size:13px', 'font-weight:600',
            'cursor:pointer', 'transition:all 0.2s',
        ].join(';');
        btn.addEventListener('mouseenter', () => { btn.style.background = '#0D2B4E'; btn.style.color = '#fff'; });
        btn.addEventListener('mouseleave', () => { btn.style.background = 'transparent'; btn.style.color = '#0D2B4E'; });
        btn.addEventListener('click', () => {
            // Disable all buttons after selection
            wrap.querySelectorAll('button').forEach(b => b.disabled = true);
            btn.style.background = '#0D2B4E';
            btn.style.color = '#fff';
            appendMessage('user', opt.label);
            finishOnboarding(opt.value);
        });
        wrap.appendChild(btn);
    });

    bubble.appendChild(wrap);
    chatWindow.scrollTop = chatWindow.scrollHeight;

    // Also update input placeholder to nudge free-typing
    messageInput.placeholder = 'Or type your preference…';
}

// ── Complete onboarding and enter chat mode ────────────────────────────────────
function finishOnboarding(preference) {
    userProfile.preference = preference;
    localStorage.setItem('urvashi_preference', preference);
    localStorage.setItem('urvashi_onboarding_done', 'true');
    onboardingState = 'chat';
    messageInput.placeholder = 'Ask me anything…';

    // Reveal the topic switch bar now that onboarding is done
    showTopicBar();

    if (preference === 'property' || preference.toLowerCase().includes('prop')) {
        setTimeout(() => {
            appendMessage('assistant', 'Great! Let\'s find you the perfect property. 🏡\nWhat are you looking for?');
            appendQuickReplies([
                '🏙️ Properties in Bangalore',
                '🏙️ Properties in Mumbai',
                '🏙️ Properties in Hyderabad',
                '🏙️ Properties in Pune',
                '💰 Budget under ₹50 Lakhs',
                '💰 Budget under ₹1 Crore',
                '🏠 2 BHK Apartments',
                '🏠 3 BHK Apartments',
                '🏁 New Launched Projects',
                '🔖 Upcoming Projects',
            ]);
        }, 400);
    } else {
        setTimeout(() => {
            appendMessage('assistant', 'Wonderful! Which service can I help you with today? 🛠️');
            appendQuickReplies([
                '🏦 Home Loan',
                '⚖️ Legal Services',
                '🔐 Security & Surveillance',
                '👥 Group Buy',
                '🌍 NRI Services',
                '🏗️ Builder Projects',
            ]);
        }, 400);
    }
}

// ── Quick-reply chips ──────────────────────────────────────────────────────────────
function appendQuickReplies(chips) {
    // Remove any existing quick-reply rows first
    document.querySelectorAll('.urvashi-quick-replies').forEach(el => el.remove());

    const row = document.createElement('div');
    row.className = 'urvashi-quick-replies';

    chips.forEach(label => {
        const btn = document.createElement('button');
        btn.className = 'urvashi-qr-chip';
        btn.textContent = label;
        btn.addEventListener('click', () => {
            // Remove all chips (single use)
            document.querySelectorAll('.urvashi-quick-replies').forEach(el => el.remove());
            // Send text directly — bypasses textarea entirely
            sendMessage(label);
        });
        row.appendChild(btn);
    });

    chatWindow.appendChild(row);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

// ── Append message ─────────────────────────────────────────────────────────────
function appendMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `urvashi-message ${role}`;

    const bubble = document.createElement('div');
    bubble.className = 'urvashi-bubble';

    // Add Urvashi avatar for assistant messages
    if (role === 'assistant') {
        const avatar = document.createElement('img');
        avatar.src = '/static/images/urvashi.png';
        avatar.className = 'urvashi-msg-avatar';
        avatar.alt = 'Urvashi';
        messageDiv.appendChild(avatar);
    }

    // Parse newlines and basic markdown links
    content.split('\n').forEach(line => {
        if (line.trim() === '') {
            bubble.appendChild(document.createElement('br'));
            return;
        }
        const p = document.createElement('p');
        let html = escapeHtml(line);
        html = html.replace(
            /\[([^\]]+)\]\(([^)]+)\)/g,
            '<a href="$2" target="_blank" style="color:#2563eb;text-decoration:underline;font-weight:500">$1</a>'
        );
        p.innerHTML = html;
        bubble.appendChild(p);
    });

    messageDiv.appendChild(bubble);
    chatWindow.appendChild(messageDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    return messageDiv;
}

// ── Typing indicator ───────────────────────────────────────────────────────────
function appendTypingIndicator() {
    const id = 'typing-' + Date.now();
    const div = document.createElement('div');
    div.id = id;
    div.className = 'urvashi-message assistant';
    div.innerHTML = `
        <img src="/static/images/urvashi.png" class="urvashi-msg-avatar" alt="Urvashi">
        <div class="urvashi-bubble urvashi-typing">
            <span></span><span></span><span></span>
        </div>`;
    chatWindow.appendChild(div);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    return id;
}

function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

// ── Inline property cards ──────────────────────────────────────────────────────
function renderInlinePropertyCards(messageDiv, cards) {
    console.log('[Urvashi] renderInlinePropertyCards called, cards:', cards ? cards.length : 'null');
    if (!cards || cards.length === 0) return;

    const container = document.createElement('div');
    container.className = 'urvashi-cards-container';

    cards.forEach(p => {
        const card = document.createElement('div');
        card.className = 'urvashi-property-card';
        const img = p.image_url || 'https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=600&q=80';
        const price = p.display_price || ('\u20b9' + Number(p.price).toLocaleString('en-IN'));
        card.innerHTML = `
            <img src="${img}" alt="${escapeHtml(p.title)}" 
                 onerror="this.src='https://via.placeholder.com/300x200?text=No+Image'">
            <div class="urvashi-card-body">
                <h4>${escapeHtml(p.title)}</h4>
                <span class="urvashi-price">${escapeHtml(price)}</span>
                <span class="urvashi-location">📍 ${escapeHtml(p.location)}</span>
                <div class="urvashi-card-btns">
                    <a href="${p.url}" target="_blank" class="urvashi-btn">View Details</a>
                </div>
            </div>`;
        container.appendChild(card);
    });

    // Append directly to chatWindow as full-width row (not inside flex message)
    chatWindow.appendChild(container);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

// ── Search Link CTA ───────────────────────────────────────────────────────────
function renderSearchLink(messageDiv, url, cardCount) {
    const wrapper = document.createElement('div');
    wrapper.style.cssText = 'margin-top:12px;padding-top:10px;border-top:1px dashed #e5e7eb;text-align:center;';

    const label = cardCount > 0
        ? 'See all matching properties →'
        : 'Browse full property search →';

    const link = document.createElement('a');
    link.href      = url;
    link.target    = '_blank';
    link.rel       = 'noopener';
    link.innerText = label;
    link.style.cssText = [
        'font-size:12px', 'font-weight:600', 'color:#0D2B4E',
        'text-decoration:none', 'letter-spacing:0.3px',
        'padding:6px 16px', 'border:1px solid #0D2B4E',
        'border-radius:20px', 'display:inline-block', 'transition:all 0.2s',
    ].join(';');
    link.addEventListener('mouseenter', () => { link.style.background = '#0D2B4E'; link.style.color = '#fff'; });
    link.addEventListener('mouseleave', () => { link.style.background = 'transparent'; link.style.color = '#0D2B4E'; });

    wrapper.appendChild(link);
    chatWindow.appendChild(wrapper);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

// ── Toggle chatbot widget ─────────────────────────────────────────────────────
function toggleUrvashi() {
    chatbotContainer.classList.toggle('urvashi-hidden');
    if (!chatbotContainer.classList.contains('urvashi-hidden')) {
        chatWindow.scrollTop = chatWindow.scrollHeight;
        messageInput.focus();
    }
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function escapeHtml(text) {
    if (!text) return '';
    return String(text).replace(/[&<>"']/g, m => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
    }[m]));
}

function getCookie(name) {
    const match = document.cookie.match(new RegExp('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)'));
    return match ? match[2] : '';
}

// ── Welcome message on load ───────────────────────────────────────────────────
window.addEventListener('load', () => {
    if (onboardingState === 'chat') {
        // Returning user — skip onboarding, show topic bar immediately
        appendMessage('assistant',
            `👋 Welcome back, ${userProfile.name || 'there'}! How can I help you today? 😊`
        );
        showTopicBar();
    } else {
        // Fresh session — start onboarding
        messageInput.placeholder = 'Type your name…';
        appendMessage('assistant',
            '👋 Hello! Welcome to Homexo. I\'m Urvashi, your dedicated property consultant. 🏡\n\n' +
            'It\'s wonderful to have you here! May I kindly know your good name?'
        );
    }
});

// ── Show/hide topic bar ───────────────────────────────────────────────────────
function showTopicBar() {
    const bar = document.getElementById('urvashi-topic-bar');
    if (bar) bar.style.display = 'flex';
    updateTopicChips();
}

// ── Topic chip highlight (uses CSS classes) ───────────────────────────────────
function updateTopicChips() {
    const pref    = localStorage.getItem('urvashi_preference') || '';
    const btnProp = document.getElementById('topic-btn-property');
    const btnSvc  = document.getElementById('topic-btn-services');
    if (!btnProp || !btnSvc) return;

    btnProp.classList.toggle('active', pref === 'property');
    btnSvc.classList.toggle('active',  pref === 'services');
}

// ── Switch topic (Property ↔ Services) ────────────────────────────────────────
window.switchTopic = function(newPreference) {
    const current = localStorage.getItem('urvashi_preference') || '';
    if (current === newPreference) return;   // already on this topic

    userProfile.preference = newPreference;
    localStorage.setItem('urvashi_preference', newPreference);
    updateTopicChips();

    // Remove any lingering quick-reply chips
    document.querySelectorAll('.urvashi-quick-replies').forEach(el => el.remove());

    const label = newPreference === 'property' ? '🏠 Property' : '🛠️ Services';
    appendMessage('user', `Switch to ${label}`);

    if (newPreference === 'property') {
        setTimeout(() => {
            appendMessage('assistant', 'Of course! What kind of property are you looking for? 🏡');
            appendQuickReplies([
                '🏙️ Properties in Bangalore',
                '🏙️ Properties in Mumbai',
                '🏙️ Properties in Hyderabad',
                '🏙️ Properties in Pune',
                '💰 Budget under ₹50 Lakhs',
                '💰 Budget under ₹1 Crore',
                '🏠 2 BHK Apartments',
                '🏠 3 BHK Apartments',
                '🏁 New Launched Projects',
                '🔖 Upcoming Projects',
            ]);
        }, 400);
    } else {
        setTimeout(() => {
            appendMessage('assistant', 'Sure! Which service can I help you with? 🛠️');
            appendQuickReplies([
                '🏦 Home Loan',
                '⚖️ Legal Services',
                '🔐 Security & Surveillance',
                '👥 Group Buy',
                '🌍 NRI Services',
                '🏗️ Builder Projects',
            ]);
        }, 400);
    }
};
