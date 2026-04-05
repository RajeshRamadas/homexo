# Homexo — Production Hosting Checklist

Track every step before and after going live. Check off items as you complete them.

---

## Phase 1 — Provision Infrastructure

- [ ] **VPS provisioned** (DigitalOcean, AWS EC2, Hetzner, etc.)
  - Recommended: Ubuntu 22.04 LTS, 2 vCPU / 4 GB RAM minimum
- [ ] **Docker installed on VPS**
  ```bash
  sudo apt update && sudo apt install -y docker.io docker-compose-plugin
  sudo systemctl enable --now docker
  sudo usermod -aG docker $USER   # allow running docker without sudo
  ```
- [ ] **Firewall configured** — ports 22 (SSH), 80 (HTTP), 443 (HTTPS) open
- [ ] **Domain DNS A-record** → VPS IP set for `homexo.in` and `www.homexo.in`
- [ ] **DNS propagated** — verify with `dig homexo.in` or https://dnschecker.org

---

## Phase 2 — Third-Party Credentials

### Email (SMTP)
- [ ] Choose provider: Gmail App Password / SendGrid / AWS SES / Mailgun
- [ ] Have ready:
  - `EMAIL_HOST_USER`
  - `EMAIL_HOST_PASSWORD` (use App Password for Gmail, not your account password)
  - `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`

### Twilio (Phone OTP)
- [ ] Sign up at https://twilio.com
- [ ] Get a trial / paid phone number
- [ ] Have ready:
  - `TWILIO_ACCOUNT_SID`
  - `TWILIO_AUTH_TOKEN`
  - `TWILIO_PHONE_NUMBER` (e.g. `+12015551234`)

### Google OAuth2
- [ ] Google Cloud Console → APIs & Services → Credentials → Create OAuth 2.0 Client ID (Web application)
- [ ] Add authorised redirect URI: `https://homexo.in/social-auth/complete/google-oauth2/`
- [ ] Have ready:
  - `GOOGLE_OAUTH2_KEY`
  - `GOOGLE_OAUTH2_SECRET`

### Facebook OAuth
- [ ] https://developers.facebook.com/apps → Create App → Add "Facebook Login"
- [ ] Add valid OAuth redirect URI: `https://homexo.in/social-auth/complete/facebook/`
- [ ] Have ready:
  - `FACEBOOK_APP_ID`
  - `FACEBOOK_APP_SECRET`

### Docker Hub
- [ ] hub.docker.com → Account Settings → Security → New Access Token
- [ ] Have ready:
  - Docker Hub username
  - Docker Hub access token

---

## Phase 3 — Configure Environment File on VPS

- [ ] Create `/opt/homexo/` directory on VPS: `mkdir -p /opt/homexo`
- [ ] Copy and fill `.env` on the VPS:
  ```bash
  # From local machine
  scp env.example user@your-server-ip:/opt/homexo/.env

  # Then SSH in and edit
  ssh user@your-server-ip
  nano /opt/homexo/.env
  ```
- [ ] **`.env` checklist** — every value below must be set:

  | Variable | Status | Notes |
  |---|---|---|
  | `SECRET_KEY` | ☐ | Generate: `openssl rand -hex 50` |
  | `DEBUG` | ☐ | Must be `False` |
  | `ALLOWED_HOSTS` | ☐ | `homexo.in,www.homexo.in` |
  | `DB_ENGINE` | ☐ | `django.db.backends.postgresql` |
  | `DB_NAME` | ☐ | e.g. `homexo_db` |
  | `DB_USER` | ☐ | e.g. `homexo` |
  | `DB_PASSWORD` | ☐ | Strong password |
  | `DB_HOST` | ☐ | `db` (Docker service name) |
  | `DB_PORT` | ☐ | `5432` |
  | `IMAGE_NAME` | ☐ | Your Docker Hub username/homexo |
  | `IMAGE_TAG` | ☐ | `latest` |
  | `EMAIL_BACKEND` | ☐ | `django.core.mail.backends.smtp.EmailBackend` |
  | `EMAIL_HOST_USER` | ☐ | |
  | `EMAIL_HOST_PASSWORD` | ☐ | |
  | `DEFAULT_FROM_EMAIL` | ☐ | `noreply@homexo.in` |
  | `ENQUIRY_NOTIFICATION_EMAIL` | ☐ | `enquiries@homexo.in` |
  | `TWILIO_ACCOUNT_SID` | ☐ | |
  | `TWILIO_AUTH_TOKEN` | ☐ | |
  | `TWILIO_PHONE_NUMBER` | ☐ | |
  | `GOOGLE_OAUTH2_KEY` | ☐ | |
  | `GOOGLE_OAUTH2_SECRET` | ☐ | |
  | `FACEBOOK_APP_ID` | ☐ | |
  | `FACEBOOK_APP_SECRET` | ☐ | |

---

## Phase 4 — Configure GitHub Secrets (CI/CD)

Go to GitHub repo → **Settings → Secrets and variables → Actions → New repository secret**

- [ ] `DOCKERHUB_USERNAME`
- [ ] `DOCKERHUB_TOKEN`
- [ ] `VPS_HOST` — server IP or hostname
- [ ] `VPS_USER` — SSH login user (e.g. `ubuntu`)
- [ ] `VPS_SSH_KEY` — full content of `~/.ssh/id_ed25519` (private key)

> **SSH key setup:** If no key pair exists yet —
> ```bash
> ssh-keygen -t ed25519 -C "github-actions-deploy"
> ssh-copy-id -i ~/.ssh/id_ed25519.pub user@your-server-ip
> ```
> Then paste the private key content into `VPS_SSH_KEY`.

- [ ] Create a **`production` environment** in GitHub: Settings → Environments → New environment → name it `production`
  - Optional: add yourself as a Required Reviewer for manual approval gate

---

## Phase 5 — Fix Settings Issues Before First Deploy

- [ ] **CORS production origins** — add to `homexo/settings.py`:

  In the `CORS_ALLOWED_ORIGINS` list (or read from env), add `https://homexo.in` and `https://www.homexo.in`.

- [ ] **Split dev dependencies** — move `django-extensions` and `ipython` out of `requirements.txt` into a separate `requirements-dev.txt` to keep the production Docker image lean.

---

## Phase 6 — First Deployment

```bash
# SSH into VPS
ssh user@your-server-ip
cd /opt/homexo

# Copy docker-compose.prod.yml and nginx/ folder
# (or clone the repo directly)
git clone https://github.com/your-org/homexo.git .

# Pull and start
docker compose -f docker-compose.prod.yml up -d --build

# Verify all 4 services are running
docker compose -f docker-compose.prod.yml ps
```

- [ ] All 4 services running: `db`, `web`, `nginx`, `certbot`
- [ ] `web` logs show no errors: `docker compose -f docker-compose.prod.yml logs web`
- [ ] HTTP → HTTPS redirect works (visit `http://homexo.in`)

---

## Phase 7 — SSL Certificate

> Only run after DNS is propagated and Nginx is serving HTTP on port 80.

```bash
cd /opt/homexo

docker compose -f docker-compose.prod.yml run --rm certbot \
  certonly --webroot -w /var/www/certbot \
  -d homexo.in -d www.homexo.in \
  --email your@email.com --agree-tos --no-eff-email

# Reload Nginx to load the new certificate
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

- [ ] Certificate issued successfully
- [ ] `https://homexo.in` loads with a valid lock icon
- [ ] HSTS header present: `curl -I https://homexo.in | grep Strict`

---

## Phase 8 — Post-Deploy Setup

```bash
# Create the admin superuser
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

- [ ] Superuser created
- [ ] Admin panel accessible at `https://homexo.in/admin/`
- [ ] Test enquiry form → confirm email arrives in inbox (not console)
- [ ] Test property listing creation (with image upload)
- [ ] Test Google OAuth login end-to-end
- [ ] Test SMS OTP (phone verification)
- [ ] Test blog post creation and display
- [ ] Sitemap accessible: `https://homexo.in/sitemap.xml`

---

## Phase 9 — Security Hardening (Post-Launch)

- [ ] **Restrict `/admin/`** in Nginx to your office/home IP:
  ```nginx
  location /admin/ {
      allow YOUR_OFFICE_IP;
      deny all;
      proxy_pass http://web:8000;
      ...
  }
  ```
- [ ] **Rate limit login endpoint** in Nginx:
  ```nginx
  limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

  location /accounts/login/ {
      limit_req zone=login burst=10 nodelay;
      proxy_pass http://web:8000;
  }
  ```
- [ ] **Add Redis** for shared cache across Gunicorn workers:
  - Add `redis` service to `docker-compose.prod.yml`
  - `pip install django-redis`
  - Update `CACHES` in `settings.py`
- [ ] Run `python manage.py check --deploy` and resolve any remaining warnings
- [ ] Consider S3/R2 for media storage if scaling beyond a single VPS

---

## Phase 10 — Write Tests

The CI pipeline runs `python manage.py test` but there are currently no test files. At minimum write:

- [ ] **Accounts** — registration, login, OTP flow
- [ ] **Properties** — list view, detail view, create (authenticated)
- [ ] **Enquiries** — form submission, email notification
- [ ] **Blog** — post list, post detail
- [ ] **API smoke tests** — `/api/properties/`, `/api/blog/`

Create test files as `<app>/tests.py` or in `<app>/tests/` directories.

---

## Quick Reference — Useful Commands on VPS

```bash
# Tail logs
docker compose -f docker-compose.prod.yml logs -f web
docker compose -f docker-compose.prod.yml logs -f nginx

# Django shell
docker compose -f docker-compose.prod.yml exec web python manage.py shell

# Run migrations manually
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

# Check deployment settings
docker compose -f docker-compose.prod.yml exec web \
  python manage.py check --deploy

# Renew SSL certificate manually
docker compose -f docker-compose.prod.yml exec certbot certbot renew

# Restart only the web service
docker compose -f docker-compose.prod.yml restart web
```
