import re

with open('/home/rajesh/Documents/GitHub/homexo/templates/pages/legal.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. CSS Theme Adjustments
text = text.replace('--teal: #1a5c52;', '--teal: #1c3d5a;')
text = text.replace('--teal-light: #d0e9e5;', '--teal-light: #dbe4ec;')
text = text.replace('background:#1a5c52;', 'background:#1c3d5a;')
text = text.replace('color:#1a5c52;', 'color:#1c3d5a;')
text = text.replace('rgba(26,92,82,', 'rgba(28,61,90,')

# 2. Page Meta
text = text.replace('Property Legal Verification Bangalore — Fixed Fee, Live Tracking | HOMEXO', 'Security & Surveillance — Complete Protection | HOMEXO')
text = text.replace("India's most transparent property legal verification service. Fixed fees, real-time status tracking, and a 1-page Go/No-Go verdict. Bangalore. From ₹4,999.", "End-to-end security infrastructure for residential and commercial properties — from CCTV installation to 24/7 remote monitoring and smart access control.")

# 3. Subnav
text = text.replace('<a href="#lg-video-call">Video Consultation</a>', '<a href="#lg-video-call">Physical Guardian</a>')

# 4. Hero Left
text = text.replace('Property Legal Verification &middot; Bangalore', 'Security & Surveillance &middot; Pan India')
text = text.replace('Buy your home<br>with <em>complete</em><br>confidence', 'Protect your property.<br><em>Day & night,</em><br>seamlessly.')
text = text.replace("India's most transparent property legal verification service. Fixed fees, real-time status tracking, and a 1-page Go/No-Go verdict &mdash; not a 20-page legal brief.", "End-to-end security infrastructure for residential and commercial properties — from CCTV installation to 24/7 remote monitoring and smart access control.")
text = text.replace('href="{% url \'legal_services:dashboard\' %}"', 'href="#" style="display:none;"')
text = text.replace('<div class="lg-trust-item"><span class="lg-trust-num">&#8377;300Cr+</span><span class="lg-trust-label">Bad investments prevented</span></div>', '<div class="lg-trust-item"><span class="lg-trust-num">100%</span><span class="lg-trust-label">Satisfaction Guaranteed</span></div>')
text = text.replace('<div class="lg-trust-item"><span class="lg-trust-num">5&ndash;7 days</span><span class="lg-trust-label">Full verification turnaround</span></div>', '<div class="lg-trust-item"><span class="lg-trust-num">24/7</span><span class="lg-trust-label">Live Monitoring</span></div>')
text = text.replace('<div class="lg-trust-item"><span class="lg-trust-num">Fixed fee</span><span class="lg-trust-label">No hidden charges, ever</span></div>', '<div class="lg-trust-item"><span class="lg-trust-num">48 hrs</span><span class="lg-trust-label">Installation Turnaround</span></div>')

# 5. Hero Right (Dashboard) -> Replaced with Security Feed mock
old_dash = r'<div class="dash-card">.*?</div>\s*</div>\s*</div>\s*<!-- PACKAGES -->'
new_dash = """<div class="dash-card">
        <div class="dash-hdr">
          <span class="dash-hdr-title">Live system status</span>
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
            <div class="step-dot step-active">&bull;</div>
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
      </div>
    </div>
  </div>
  <!-- PACKAGES -->"""
text = re.sub(old_dash, new_dash, text, flags=re.DOTALL)

# 6. Packages
old_packages = r'<!-- PACKAGES -->.*?<!-- VIDEO CALL ADD-ON -->'
new_packages = """<!-- PACKAGES -->
  <div id="lg-packages" class="lg-packages">
    <div class="lg-section-label"><span class="lg-s-label">Pricing plans</span><span class="lg-s-line"></span></div>
    <h2 class="lg-heading">Transparent pricing.<br><em style="color:var(--gold-light);">Complete protection.</em></h2>
    <p class="lg-sub-text" style="color:rgba(247,244,238,0.5);">No hidden costs. All packages include free site survey, installation, and app setup.</p>
    <div class="pkg-grid">
      <div class="pkg-card fade-up">
        <div class="pkg-tier">Starter</div>
        <div class="pkg-name">Essential Shield</div>
        <div class="pkg-price"><sup>&#8377;</sup>18,999</div>
        <div class="pkg-timeline">&#9201; 48-hour installation</div>
        <ul class="pkg-features">
          <li><span class="feat-yes">&#10003;</span> 4 Full-HD CCTV cameras</li>
          <li><span class="feat-yes">&#10003;</span> 4-channel DVR with 1TB HDD</li>
          <li><span class="feat-yes">&#10003;</span> Mobile app remote viewing</li>
          <li><span class="feat-yes">&#10003;</span> Motion detection alerts</li>
          <li><span class="feat-yes">&#10003;</span> 1-year on-site warranty</li>
          <li><span class="feat-no">&ndash;</span> Remote Monitoring</li>
          <li><span class="feat-no">&ndash;</span> Video door phone</li>
        </ul>
        <a href="#lg-cta" class="pkg-cta pkg-cta-outline">Get started &rarr;</a>
      </div>
      <div class="pkg-card featured fade-up">
        <div class="pkg-badge">Most popular</div>
        <div class="pkg-tier">Professional</div>
        <div class="pkg-name">Guardian Pro</div>
        <div class="pkg-price"><sup>&#8377;</sup>42,999</div>
        <div class="pkg-timeline">&#9201; Detailed system layout & config</div>
        <ul class="pkg-features">
          <li><span class="feat-yes">&#10003;</span> 8 Full-HD IP cameras with night vision</li>
          <li><span class="feat-yes">&#10003;</span> 8-channel NVR with 2TB HDD + cloud</li>
          <li><span class="feat-yes">&#10003;</span> AI-based person & vehicle detection</li>
          <li><span class="feat-yes">&#10003;</span> Video door phone (2 indoor units)</li>
          <li><span class="feat-yes">&#10003;</span> Smart access control for main door</li>
          <li><span class="feat-yes">&#10003;</span> 24/7 remote monitoring (6 mo)</li>
          <li><span class="feat-yes">&#10003;</span> 2-year comprehensive warranty</li>
        </ul>
        <a href="#lg-cta" class="pkg-cta pkg-cta-gold">Get started &rarr;</a>
      </div>
      <div class="pkg-card fade-up">
        <div class="pkg-tier">Enterprise</div>
        <div class="pkg-name">Fort Knox</div>
        <div class="pkg-price"><span style="font-size:32px;">Custom</span></div>
        <div class="pkg-timeline">&#9201; Bespoke scope</div>
        <ul class="pkg-features">
          <li><span class="feat-yes">&#10003;</span> 4K PTZ + panoramic camera array</li>
          <li><span class="feat-yes">&#10003;</span> Perimeter fence intrusion detection</li>
          <li><span class="feat-yes">&#10003;</span> Facial recognition access control</li>
          <li><span class="feat-yes">&#10003;</span> Dedicated 24/7 monitoring + disp.</li>
          <li><span class="feat-yes">&#10003;</span> Fire & smoke detector integration</li>
          <li><span class="feat-yes">&#10003;</span> Seamless smart-home integration</li>
          <li><span class="feat-yes">&#10003;</span> 3-year AMC included</li>
        </ul>
        <a href="#lg-cta" class="pkg-cta pkg-cta-outline">Request Quote &rarr;</a>
      </div>
    </div>
  </div>
  
  <!-- VIDEO CALL ADD-ON -->"""
text = re.sub(old_packages, new_packages, text, flags=re.DOTALL)

# 7. Video Call Add-on replaced by Physical Guardian
old_video = r'<!-- VIDEO CALL ADD-ON -->.*?<!-- PROCESS -->'
new_video = """<!-- VIDEO CALL ADD-ON -->
  <div id="lg-video-call" class="lg-video-call" style="background:var(--cream);">
    <div class="lg-section-label"><span class="lg-s-label">New Service</span><span class="lg-s-line"></span></div>
    <h2 class="lg-heading">No Camera Needed. <em style="color:var(--gold);">Real People.</em><br>Real Protection.</h2>
    <p class="lg-sub-text" style="margin-bottom:52px;">Some properties can't have cameras — or the owner prefers not to. Our Physical Property Guardian service deploys trained on-ground personnel to visit, inspect, and report on your property.</p>

    <div class="video-grid">
      <div class="video-card">
        <div style="position:absolute; top:-60px; right:-60px; width:200px; height:200px; background:radial-gradient(circle, rgba(201,168,76,0.12) 0%, transparent 70%); border-radius:50%;"></div>
        <div style="position:relative; z-index:2;">
          <div style="display:inline-flex; align-items:center; gap:8px; background:rgba(201,168,76,0.12); border:1px solid rgba(201,168,76,0.25); border-radius:99px; padding:6px 14px; margin-bottom:24px;">
            <span style="font-size:16px;">&#128110;&#8205;&#9794;&#65039;</span>
            <span style="font-family:'DM Mono',monospace; font-size:10px; letter-spacing:0.1em; text-transform:uppercase; color:var(--gold);">Physical Guardian</span>
          </div>
          <div style="font-family:'Playfair Display',serif; font-size:32px; font-weight:700; color:var(--cream); margin-bottom:6px;">₹2,499 <span style="font-size:18px; font-weight:300; color:rgba(247,244,238,0.5);">/ month</span></div>
          <div style="font-family:'DM Mono',monospace; font-size:11px; color:var(--gold); margin-bottom:28px;">No hardware needed</div>
          <ul style="list-style:none; display:flex; flex-direction:column; gap:12px; margin-bottom:32px;">
            <li style="display:flex; align-items:flex-start; gap:10px; font-size:14px; color:rgba(247,244,238,0.75);">
              <span style="color:#4abd9e; flex-shrink:0; margin-top:1px;">✓</span> Trained officer visits your property in person
            </li>
            <li style="display:flex; align-items:flex-start; gap:10px; font-size:14px; color:rgba(247,244,238,0.75);">
              <span style="color:#4abd9e; flex-shrink:0; margin-top:1px;">✓</span> Flexible schedule — daily, weekly, or custom
            </li>
            <li style="display:flex; align-items:flex-start; gap:10px; font-size:14px; color:rgba(247,244,238,0.75);">
              <span style="color:#4abd9e; flex-shrink:0; margin-top:1px;">✓</span> Timestamped photo + video log after every visit
            </li>
          </ul>
          <div style="display:flex; gap:12px; flex-wrap:wrap;">
            <a href="#lg-cta"
              style="flex:1; min-width:140px; display:inline-flex; align-items:center; justify-content:center; gap:8px; padding:14px 20px; background:var(--gold); color:var(--ink); font-size:14px; font-weight:600; border-radius:8px; text-decoration:none; transition:all 0.2s;">
              Enquire Now
            </a>
          </div>
        </div>
      </div>
      <div style="display:flex; flex-direction:column; gap:20px;">
        <div style="background:var(--teal-light); border:1px solid rgba(26,92,82,0.15); border-radius:16px; padding:28px;">
          <div style="font-size:14px; font-weight:600; color:var(--teal); margin-bottom:16px;">📋 Who is this for?</div>
          <ul style="list-style:none; display:flex; flex-direction:column; gap:10px;">
            <li style="display:flex; gap:10px; font-size:13px; color:var(--muted);"><span style="color:var(--teal); font-weight:600; flex-shrink:0;">→</span> NRIs & frequent travellers</li>
            <li style="display:flex; gap:10px; font-size:13px; color:var(--muted);"><span style="color:var(--teal); font-weight:600; flex-shrink:0;">→</span> Plot & land owners vulnerable to encroachment</li>
            <li style="display:flex; gap:10px; font-size:13px; color:var(--muted);"><span style="color:var(--teal); font-weight:600; flex-shrink:0;">→</span> Second home or farmhouse owners</li>
            <li style="display:flex; gap:10px; font-size:13px; color:var(--muted);"><span style="color:var(--teal); font-weight:600; flex-shrink:0;">→</span> Landlords with vacant flats between tenants</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
  <!-- PROCESS -->"""
text = re.sub(old_video, new_video, text, flags=re.DOTALL)

# 8. Process
old_process = r'<!-- PROCESS -->.*?<!-- SERVICES -->'
new_process = """<!-- PROCESS -->
  <div id="lg-process" class="lg-process">
    <div class="lg-section-label"><span class="lg-s-label">How it works</span><span class="lg-s-line"></span></div>
    <h2 class="lg-heading">From Survey to<br><em>Active Protection</em></h2>
    <p class="lg-sub-text">A structured four-step process ensures your property is covered with zero guesswork and minimal disruption.</p>
    <div class="process-grid">
      <div class="proc-steps">
        <div class="proc-step fade-up">
          <div class="proc-num">01</div>
          <div class="proc-content">
            <div class="proc-state">SURVEY</div>
            <div class="proc-title">Free Site Survey</div>
            <div class="proc-desc">Our security consultant visits your property, maps entry points, identifies blind spots, and assesses environmental factors like lighting and layout.</div>
          </div>
        </div>
        <div class="proc-step fade-up">
          <div class="proc-num">02</div>
          <div class="proc-content">
            <div class="proc-title">Custom Design</div>
            <div class="proc-desc">We deliver a detailed security plan — camera placement diagrams, hardware specs, cabling routes, and a transparent itemised quotation.</div>
          </div>
        </div>
        <div class="proc-step fade-up">
          <div class="proc-num">03</div>
          <div class="proc-content">
            <div class="proc-title">Professional Installation</div>
            <div class="proc-desc">Certified technicians install all hardware typically within 48 hours. We handle end-to-end configuration including NVR setup, app pairing, and user training.</div>
          </div>
        </div>
        <div class="proc-step fade-up">
          <div class="proc-num">04</div>
          <div class="proc-content">
            <div class="proc-title">Monitoring & AMC</div>
            <div class="proc-desc">Choose round-the-clock monitoring or self-monitoring. Our Annual Maintenance Contracts cover preventive servicing, remote diagnostics, and priority support.</div>
          </div>
        </div>
      </div>
      <div class="proc-visual">
        <div class="verdict-display">
          <div class="verdict-head">
            <span>Security Setup</span>
            <span class="verdict-stamp">Certified Installers</span>
          </div>
          <div class="verdict-main">
            <div class="big-dot" style="font-size:24px;">&#128249;</div>
            <div>
              <div class="verdict-title-big">Armed & Secure</div>
              <div class="verdict-sub-big">Professional Installation Complete</div>
            </div>
          </div>
          <div class="verdict-checks">
            <div class="v-check"><div class="v-check-dot dot-g"></div>Cameras Calibrated</div>
            <div class="v-check"><div class="v-check-dot dot-g"></div>NVR Configured</div>
            <div class="v-check"><div class="v-check-dot dot-g"></div>App Paired</div>
            <div class="v-check"><div class="v-check-dot dot-g"></div>Motion Zones Set</div>
            <div class="v-check"><div class="v-check-dot dot-g"></div>Alerts Tested</div>
            <div class="v-check"><div class="v-check-dot dot-g"></div>Power Backup Check</div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <!-- SERVICES -->"""
text = re.sub(old_process, new_process, text, flags=re.DOTALL)

# 9. Services
old_services = r'<!-- SERVICES -->.*?<!-- WHY HOMEXO -->'
new_services = """<!-- SERVICES -->
  <div id="lg-services" class="lg-services">
    <div class="lg-section-label"><span class="lg-s-label">What we offer</span><span class="lg-s-line"></span></div>
    <h2 class="lg-heading">Comprehensive<br><em>Security Services</em></h2>
    <p class="lg-sub-text">Every property is different. We design, supply, install, and maintain a layered security ecosystem tailored to your needs.</p>
    <div class="services-grid">
      <div class="svc-cell fade-up">
        <div class="svc-num">01</div>
        <div class="svc-icon">&#128249;</div>
        <div class="svc-name">CCTV & IP Camera Installation</div>
        <div class="svc-body">Full-HD, 4K, and PTZ cameras for indoor and outdoor coverage. Night vision, weatherproof options with DVR/NVR setup and app-based remote viewing.</div>
      </div>
      <div class="svc-cell fade-up">
        <div class="svc-num">02</div>
        <div class="svc-icon">&#128187;</div>
        <div class="svc-name">24/7 Remote Monitoring</div>
        <div class="svc-body">Round-the-clock monitoring from our operations centre. Real-time alerts on motion, perimeter breach, or unusual activity — delivered to your phone instantly.</div>
      </div>
      <div class="svc-cell fade-up">
        <div class="svc-num">03</div>
        <div class="svc-icon">&#128274;</div>
        <div class="svc-name">Access Control & Video Door Phone</div>
        <div class="svc-body">Biometric, RFID, and PIN-based entry for gates, lifts, and server rooms — combined with HD video intercom, two-way audio, and remote door unlock.</div>
      </div>
      <div class="svc-cell fade-up">
        <div class="svc-num">04</div>
        <div class="svc-icon">&#128680;</div>
        <div class="svc-name">Burglar & Intruder Alarm</div>
        <div class="svc-body">PIR sensors, magnetic contacts, glass-break detectors, and siren units on a central panel. Police-linkable with instant SMS and call alerts.</div>
      </div>
      <div class="svc-cell fade-up">
        <div class="svc-num">05</div>
        <div class="svc-icon">&#128203;</div>
        <div class="svc-name">Security Audit & Consulting</div>
        <div class="svc-body">A certified expert surveys your site, maps blind spots, and delivers a written risk report with prioritised recommendations — before you invest in hardware.</div>
      </div>
      <div class="svc-cell fade-up">
        <div class="svc-num">06</div>
        <div class="svc-icon">&#128110;&#8205;&#9794;&#65039;</div>
        <div class="svc-name">Physical Property Guardian</div>
        <div class="svc-body">No cameras required. Our trained field officers physically visit your plot, flat, or home on a schedule — inspect, photograph, and report directly to you.</div>
      </div>
    </div>
  </div>
  <!-- WHY HOMEXO -->"""
text = re.sub(old_services, new_services, text, flags=re.DOTALL)

# 10. Why Homexo
old_why = r'<!-- WHY HOMEXO -->.*?<!-- TESTIMONIALS -->'
new_why = """<!-- WHY HOMEXO -->
  <div id="lg-why" class="lg-why">
    <div class="lg-section-label"><span class="lg-s-label">Why Homexo Security</span><span class="lg-s-line"></span></div>
    <h2 class="lg-heading">Your Property Deserves<br><em>Better Than Average</em></h2>
    <div class="why-grid">
      <div class="why-list">
        <div class="why-item fade-up">
          <div class="why-icon">&#9201;</div>
          <div><div class="why-title">48-Hour Installation</div><div class="why-desc">From confirmed booking to a fully operational system — our certified technicians typically complete any residential installation within 48 hours.</div></div>
        </div>
        <div class="why-item fade-up">
          <div class="why-icon">&#128110;&#8205;&#9792;&#65039;</div>
          <div><div class="why-title">Certified & Vetted Technicians</div><div class="why-desc">Every installation team member is background-checked, manufacturer-certified, and covered under our liability insurance.</div></div>
        </div>
        <div class="why-item fade-up">
          <div class="why-icon">&#129302;</div>
          <div><div class="why-title">Real-Time AI Monitoring</div><div class="why-desc">Our AI detection engine cuts false alarms by up to 90%, so when you get a notification, it actually means something.</div></div>
        </div>
        <div class="why-item fade-up">
          <div class="why-icon">&#128172;</div>
          <div><div class="why-title">Dedicated Support</div><div class="why-desc">Every client gets a direct WhatsApp support line. Issues resolved within 4 hours for AMC clients.</div></div>
        </div>
      </div>
      <div class="comp-wrap fade-up">
        <div class="comp-title">Homexo vs Local Vendors</div>
        <table class="comp-table">
          <thead>
            <tr><th>Feature</th><th>Local Vendor</th><th>Homexo Security</th></tr>
          </thead>
          <tbody>
            <tr><td>Transparent Pricing</td><td class="cell-no">&#10007; Hidden Costs</td><td class="cell-yes" style="color:#4abd9e;font-weight:500;">&#10003; Itemised Quotes</td></tr>
            <tr><td>Equipment Quality</td><td class="cell-no">Unbranded/Cheap</td><td class="cell-yes" style="color:#4abd9e;font-weight:500;">Top Tier Brands</td></tr>
            <tr><td>AI Event Detection</td><td class="cell-no">&#10007; Basic Motion</td><td class="cell-yes" style="color:#4abd9e;font-weight:500;">&#10003; Smart AI</td></tr>
            <tr><td>Response Time</td><td class="cell-no">Days/Weeks</td><td class="cell-yes" style="color:#4abd9e;font-weight:500;">&lt; 4 Hours (AMC)</td></tr>
            <tr><td>Remote Monitoring</td><td class="cell-no">&#10007; None</td><td class="cell-yes" style="color:#4abd9e;font-weight:500;">&#10003; 24/7 Operations Center</td></tr>
            <tr class="hl-row"><td>Vetted Technicians</td><td>&#10007; No</td><td>&#10003; Fully Verified</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
  <!-- TESTIMONIALS -->"""
text = re.sub(old_why, new_why, text, flags=re.DOTALL)

# 11. Testimonials
old_testi = r'<!-- TESTIMONIALS -->.*?<!-- GET STARTED FORM -->'
new_testi = """<!-- TESTIMONIALS -->
  <div class="lg-testimonials">
    <div class="lg-section-label"><span class="lg-s-label">Client stories</span><span class="lg-s-line"></span></div>
    <h2 class="lg-heading">Trusted by Property Owners<br><em>Across India</em></h2>
    <div class="testi-grid">
      <div class="testi-card fade-up">
        <div class="testi-quote">&ldquo;</div>
        <p class="testi-text">We had two break-in attempts at our warehouse before HOMEXO set up the surveillance system. Since installation 14 months ago — zero incidents. The AI alerts are razor-sharp.</p>
        <div class="testi-author">
          <div class="testi-avatar" style="background:var(--teal-light);color:var(--teal);">RK</div>
          <div><div class="testi-name">Rajesh Kulkarni</div><div class="testi-detail">Commercial Property &middot; Peenya</div></div>
        </div>
      </div>
      <div class="testi-card fade-up">
        <div class="testi-quote">&ldquo;</div>
        <p class="testi-text">I'm an NRI and was worried about my Pune flat. HOMEXO installed cameras and set up remote monitoring. I can literally check my flat from London with one tap. Professional service.</p>
        <div class="testi-author">
          <div class="testi-avatar" style="background:var(--rust-light);color:var(--rust);">SM</div>
          <div><div class="testi-name">Sunita Menon</div><div class="testi-detail">Residential Flat &middot; Baner</div></div>
        </div>
      </div>
      <div class="testi-card fade-up">
        <div class="testi-quote">&ldquo;</div>
        <p class="testi-text">The Guardian Pro package was perfect for our villa. The video door phone means we never have to open the gate without seeing who's there. The biometric lock for the kids' room is an added bonus.</p>
        <div class="testi-author">
          <div class="testi-avatar" style="background:#faeeda;color:#854f0b;">AP</div>
          <div><div class="testi-name">Amit Prasad</div><div class="testi-detail">Independent Villa &middot; Sarjapur</div></div>
        </div>
      </div>
    </div>
  </div>
  <!-- GET STARTED FORM -->"""
text = re.sub(old_testi, new_testi, text, flags=re.DOTALL)

# 12. GET STARTED FORM
text = text.replace('Your home is the biggest<br><em style="color:var(--gold-light);">purchase of your life</em>', 'Protect what matters most,<br><em style="color:var(--gold-light);">starting with a free survey</em>')
text = text.replace('Don&rsquo;t let a legal gap cost you everything. Get a complete verification from &#8377;4,999 &mdash; and buy with complete confidence.', 'Our security consultant will visit your property at no cost. Get a detailed assessment and an itemized quotation.')
text = text.replace('value="legal"', 'value="security"')
text = text.replace('Request Legal Callback &rarr;', 'Request Free Site Survey &rarr;')
text = text.replace('Need a Final <em>Legal</em><br>Go / No-Go Check?', 'Need a free<br><em>Site</em> Survey?')
text = text.replace('Share your property details and our legal team will call you with the right verification package and timeline.', 'Share your property details and our expert team will visit you at no cost to offer the best security solution.')
text = text.replace('Legal Service Needed', 'Security Service Needed')
text = text.replace('Title &amp; Document Verification', 'CCTV Installation')
text = text.replace('Sale Agreement Drafting', 'Access Control & Alarms')
text = text.replace('Khata / Post-Purchase Support', 'Physical Property Guardian')
text = text.replace('<option value="Video Consultation">Video Consultation</option>', '<option value="Security Audit">Security Audit</option>')
text = text.replace('Request Legal Consultation &rarr;', 'Request Free Survey &rarr;')
# remove the hidden service_detail override inside lg-cta
text = text.replace('<input type="hidden" name="service_detail" value="Legal CTA Section">', '<input type="hidden" name="service_detail" value="Security CTA Section">')
text = text.replace('<div class="cta-bg-text">LEGAL</div>', '<div class="cta-bg-text">SECURITY</div>')

with open('/home/rajesh/Documents/GitHub/homexo/templates/pages/security.html', 'w', encoding='utf-8') as f:
    f.write(text)

