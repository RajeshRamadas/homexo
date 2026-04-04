import re

with open('/home/rajesh/Documents/GitHub/homexo/templates/pages/legal.html', 'r', encoding='utf-8') as f:
    template = f.read()

# Replace specific CSS values for Security Theme (Navy Blue instead of Teal)
# Original Legal Theme:
# --teal: #1a5c52; --teal-light: #d0e9e5;
# Replaced with Navy:
theme_css = """
  .lg-page {
    --ink: #0f0e0c; --cream: #f7f4ee; --warm: #e8e2d6;
    --gold: #c9a84c; --gold-light: #e8d49a;
    --rust: #b5470c; --rust-light: #f0d4c4;
    --teal: #1c3d5a; --teal-light: #d6e2f0; /* Navy for security */
    --muted: #7a766e;
    --border-lg: rgba(15,14,12,0.12);
    --border-warm: rgba(201,168,76,0.3);
    font-family: 'DM Sans', sans-serif; color: var(--ink);
  }
"""

template = re.sub(r'\.lg-page\s*\{[^}]+\}', theme_css.strip(), template)

# Replace "Property Legal Verification Bangalore" to "Security & Surveillance Bangalore"
template = template.replace('Property Legal Verification Bangalore — Fixed Fee, Live Tracking | HOMEXO', 'Security & Surveillance — 24/7 Monitoring, Installation | HOMEXO')
template = template.replace("India's most transparent property legal verification service. Fixed fees, real-time status tracking, and a 1-page Go/No-Go verdict. Bangalore. From ₹4,999.", "End-to-end security infrastructure for residential and commercial properties — from CCTV installation to 24/7 remote monitoring and smart access control.")

# Change navigation
template = template.replace('<a href="#lg-video-call">Video Consultation</a>', '<a href="#lg-video-call">Physical Guardian</a>')

# Hero text
template = template.replace('Property Legal Verification &middot; Bangalore', 'Security & Surveillance &middot; Pan India')
template = template.replace('Buy your home<br>with <em>complete</em><br>confidence', 'Protect your property.<br><em>Day & night,</em><br>seamlessly.')
template = template.replace("India's most transparent property legal verification service. Fixed fees, real-time status tracking, and a 1-page Go/No-Go verdict &mdash; not a 20-page legal brief.", "End-to-end security infrastructure for residential and commercial properties — from CCTV installation to 24/7 remote monitoring and smart access control.")

template = template.replace('<div class="lg-trust-item"><span class="lg-trust-num">&#8377;300Cr+</span><span class="lg-trust-label">Bad investments prevented</span></div>', '<div class="lg-trust-item"><span class="lg-trust-num">100%</span><span class="lg-trust-label">Satisfaction Guaranteed</span></div>')
template = template.replace('<div class="lg-trust-item"><span class="lg-trust-num">5&ndash;7 days</span><span class="lg-trust-label">Full verification turnaround</span></div>', '<div class="lg-trust-item"><span class="lg-trust-num">24/7</span><span class="lg-trust-label">Live Monitoring</span></div>')
template = template.replace('<div class="lg-trust-item"><span class="lg-trust-num">Fixed fee</span><span class="lg-trust-label">No hidden charges, ever</span></div>', '<div class="lg-trust-item"><span class="lg-trust-num">48 hrs</span><span class="lg-trust-label">Installation Turnaround</span></div>')

# Hero Right Dash Card
old_dash = '<div class="dash-hdr">.*?<div class="dash-verdict">.*?</div>\\s*</div>'
new_dash = """
        <div class="dash-hdr">
          <span class="dash-hdr-title">Live System Status</span>
          <span class="dash-hdr-order">#HXS-LOBBY</span>
        </div>
        <div class="dash-prop">
          <div class="dash-prop-lbl">Cameras Online</div>
          <div class="dash-prop-name">8 / 8 Active Streams</div>
          <div class="dash-prop-addr">All zones secure &middot; Recording</div>
        </div>
        <div class="dash-steps">
          <div class="dash-step">
            <div class="step-dot step-done">&#10003;</div>
            <div class="step-info"><div class="step-name">Main Gate</div><div class="step-detail">Motion Detected - 2 mins ago</div></div>
          </div>
          <div class="dash-step">
            <div class="step-dot step-done">&#10003;</div>
            <div class="step-info"><div class="step-name">Rear Entrance</div><div class="step-detail">Clear</div></div>
          </div>
          <div class="dash-step">
            <div class="step-dot step-active">&rarr;</div>
            <div class="step-info"><div class="step-name">Lobby</div><div class="step-detail active-msg">Live Feed Active</div></div>
          </div>
          <div class="dash-step">
            <div class="step-dot step-done">&#10003;</div>
            <div class="step-info"><div class="step-name">Parking</div><div class="step-detail">Clear</div></div>
          </div>
        </div>
        <div class="dash-verdict">
          <div class="vd-dot">&#128994;</div>
          <div><div class="vd-text">System Normal</div><div class="vd-sub">Storage: 63% Used &middot; Battery Backup 100%</div></div>
        </div>
"""
template = re.sub(r'<div class="dash-hdr">.*?</style>', lambda m: 'FOO', template, flags=re.DOTALL) # wait regex dotall is tricky in python without re module flags explicitly.

with open('/home/rajesh/Documents/GitHub/homexo/templates/pages/security.html', 'w', encoding='utf-8') as f:
    f.write(template)

