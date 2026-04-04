# Homexo — DevOps Guide

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Prerequisites](#prerequisites)
- [Local Development with Docker](#local-development-with-docker)
- [Environment Variables](#environment-variables)
- [Production Deployment](#production-deployment)
- [SSL / HTTPS with Let's Encrypt](#ssl--https-with-lets-encrypt)
- [CI/CD Pipeline](#cicd-pipeline)
- [GitHub Secrets Reference](#github-secrets-reference)
- [Useful Commands](#useful-commands)

---

## Architecture Overview

```
Internet
    │
    ▼
 Nginx (80/443)
    │  serves /static/ and /media/ directly
    │  proxies everything else
    ▼
 Gunicorn (port 8000)   ◄──── Django app
    │
    ▼
 PostgreSQL (port 5432)
```

| Service | Image | Role |
|---|---|---|
| `web` | custom (Dockerfile) | Django + Gunicorn |
| `db` | postgres:16-alpine | PostgreSQL database |
| `nginx` | nginx:1.27-alpine | Reverse proxy + static files |
| `certbot` | certbot/certbot | Auto TLS certificate renewal |

---

## Prerequisites

| Tool | Version |
|---|---|
| Docker | 24+ |
| Docker Compose | v2 (bundled with Docker Desktop / `docker compose`) |
| Python | 3.12 (for local non-Docker dev) |

---

## Local Development with Docker

```bash
# 1. Copy and edit environment variables
cp env.example .env
# Set DB_NAME, DB_USER, DB_PASSWORD, SECRET_KEY at minimum

# 2. Start services (live-reload enabled)
docker compose up --build

# 3. Open http://localhost:8000
```

The `web` container mounts the project directory, so code changes reload instantly without rebuilding.

### Useful dev commands

```bash
# Run Django management commands
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py shell

# View logs
docker compose logs -f web

# Stop everything
docker compose down

# Stop and wipe the database
docker compose down -v
```

---

## Environment Variables

Copy `env.example` to `.env` and fill in your values. Never commit `.env`.

### Required in production

| Variable | Example | Description |
|---|---|---|
| `SECRET_KEY` | `openssl rand -hex 50` | Django secret key |
| `DEBUG` | `False` | Must be `False` in prod |
| `ALLOWED_HOSTS` | `homexo.in,www.homexo.in` | Comma-separated domains |
| `DB_NAME` | `homexo_db` | PostgreSQL database name |
| `DB_USER` | `homexo` | PostgreSQL user |
| `DB_PASSWORD` | _(strong password)_ | PostgreSQL password |
| `DB_HOST` | `db` | Service name in compose |
| `DB_PORT` | `5432` | PostgreSQL port |

### Optional

| Variable | Description |
|---|---|
| `EMAIL_*` | SMTP settings for transactional email |
| `TWILIO_*` | Phone OTP via Twilio |
| `GOOGLE_OAUTH2_KEY/SECRET` | Google social login |
| `FACEBOOK_APP_ID/SECRET` | Facebook social login |
| `IMAGE_NAME` / `IMAGE_TAG` | Docker Hub image reference (default: `homexo:latest`) |

---

## Production Deployment

### 1. Prepare the VPS

```bash
# On your DigitalOcean / VPS server (Ubuntu 22.04+)
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
sudo systemctl enable --now docker

mkdir -p /opt/homexo
cd /opt/homexo
```

### 2. Upload environment file

```bash
# From your local machine
scp .env user@your-server-ip:/opt/homexo/.env
```

### 3. First deploy

```bash
# On the server
cd /opt/homexo

# Pull and start all services
docker compose -f docker-compose.prod.yml up -d --build

# Check everything is running
docker compose -f docker-compose.prod.yml ps
```

### 4. Subsequent deploys

After your CI/CD pipeline is configured, deploys happen automatically on every push to `main`. To deploy manually:

```bash
cd /opt/homexo
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d --remove-orphans
```

---

## SSL / HTTPS with Let's Encrypt

SSL is managed by Certbot. Run this **once** after DNS is pointing to your server:

```bash
cd /opt/homexo

# Issue certificate (replace with your domain)
docker compose -f docker-compose.prod.yml run --rm certbot \
  certonly --webroot -w /var/www/certbot \
  -d homexo.in -d www.homexo.in \
  --email your@email.com --agree-tos --no-eff-email

# Reload Nginx to pick up the new certificate
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

Renewal runs automatically every 12 hours via the `certbot` service.

> **Note:** Update `nginx/conf.d/homexo.conf` to match your actual domain before the first deploy.

---

## CI/CD Pipeline

Two GitHub Actions workflows are included:

### `ci.yml` — runs on every push and pull request

```
Push / PR
    │
    ├─ Lint & Test
    │     ├─ Start Postgres service
    │     ├─ Run migrations
    │     ├─ python manage.py test
    │     └─ Check production settings
    │
    └─ Build Docker Image  (push events only)
          ├─ Build with layer caching
          └─ Push to Docker Hub (tagged with branch + SHA)
```

### `deploy.yml` — runs on push to `main`

```
Push to main
    │
    ├─ Build & push image to Docker Hub (:latest)
    │
    └─ SSH into VPS
          ├─ docker compose pull
          ├─ docker compose up -d --remove-orphans
          └─ docker image prune -f
```

The deploy job targets the `production` environment in GitHub — you can add a manual approval gate there (**Settings → Environments → production → Required reviewers**).

---

## GitHub Secrets Reference

Add these in **Settings → Secrets and variables → Actions**:

| Secret | Description |
|---|---|
| `DOCKERHUB_USERNAME` | Docker Hub account username |
| `DOCKERHUB_TOKEN` | Docker Hub access token (not your password) |
| `VPS_HOST` | Server IP or hostname |
| `VPS_USER` | SSH login user (e.g. `ubuntu`, `root`) |
| `VPS_SSH_KEY` | Full content of your private SSH key (`~/.ssh/id_ed25519`) |

Generate a Docker Hub token at **hub.docker.com → Account Settings → Security → Access Tokens**.

---

## Useful Commands

```bash
# ─── Local dev ────────────────────────────────────────────────────────────────
docker compose up --build            # start dev stack
docker compose down -v               # stop and delete volumes
docker compose exec web bash         # shell into web container
docker compose exec web python manage.py migrate
docker compose exec db psql -U homexo homexo_db   # Postgres prompt

# ─── Production ───────────────────────────────────────────────────────────────
docker compose -f docker-compose.prod.yml logs -f web    # tail app logs
docker compose -f docker-compose.prod.yml logs -f nginx  # tail nginx logs
docker compose -f docker-compose.prod.yml exec web python manage.py shell

# ─── Docker maintenance ───────────────────────────────────────────────────────
docker image prune -f               # remove unused images
docker volume ls                    # list volumes
docker stats                        # live resource usage

# ─── Backup database ──────────────────────────────────────────────────────────
docker compose -f docker-compose.prod.yml exec db \
  pg_dump -U homexo homexo_db > backup_$(date +%Y%m%d).sql
```
