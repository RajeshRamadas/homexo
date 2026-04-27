/**
 * Homexo — Urvashi Chat Widget
 * Ported from RAG_chat/property_search/frontend/chat.js
 * Adapted to use /api/v1/chat/ endpoint and Homexo's property URLs.
 */

// ── Session management ────────────────────────────────────────────────────────
const SESSION_ID = (() => {
    let id = sessionStorage.getItem('urvashi_session_id');
    if (!id) {
        id = crypto.randomUUID();
        sessionStorage.setItem('urvashi_session_id', id);
    }
    return id;
})();

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
async function sendMessage() {
    const text = messageInput.value.trim();
    if (!text) return;

    appendMessage('user', text);
    messageInput.value = '';
    sendBtn.disabled = true;

    // Typing indicator
    const typingId = appendTypingIndicator();

    try {
        const response = await fetch('/api/v1/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ message: text, session_id: SESSION_ID }),
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
    return bubble;
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

// ── Inline property cards ─────────────────────────────────────────────────────
function renderInlinePropertyCards(bubble, cards) {
    if (!cards || cards.length === 0) return;

    const container = document.createElement('div');
    container.className = 'urvashi-cards-container';

    cards.forEach(p => {
        const card = document.createElement('div');
        card.className = 'urvashi-property-card';
        const img = p.image_url || 'https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=600&q=80';
        const price = p.display_price || ('₹' + Number(p.price).toLocaleString('en-IN'));
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

    bubble.appendChild(container);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

// ── Search Link CTA ───────────────────────────────────────────────────────────
function renderSearchLink(bubble, url, cardCount) {
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
    bubble.appendChild(wrapper);
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
    appendMessage('assistant',
        '👋 Hi! I\'m Urvashi, your personal property consultant at Homexo.\n\n' +
        'I can help you find your dream home in Bangalore. Tell me:\n' +
        '• What area are you looking in?\n' +
        '• What\'s your budget?\n' +
        '• How many BHKs do you need?\n\n' +
        'Let\'s find your perfect home! 🏡'
    );
});
