# gunicorn.conf.py — Homexo Production Gunicorn Configuration
# All tunables are driven by environment variables so you can upgrade plans
# by changing .env and restarting — no image rebuild needed.
#
# $8/mo  plan (1 GB RAM): GUNICORN_WORKERS=1 GUNICORN_THREADS=2
# $16/mo plan (2 GB RAM): GUNICORN_WORKERS=2 GUNICORN_THREADS=4
# $32/mo plan (4 GB RAM): GUNICORN_WORKERS=3 GUNICORN_THREADS=4  (+ enable chatbot)

import os

# ── Binding ───────────────────────────────────────────────────────────────────
bind = "0.0.0.0:8000"

# ── Workers ───────────────────────────────────────────────────────────────────
workers     = int(os.environ.get("GUNICORN_WORKERS", "1"))
threads     = int(os.environ.get("GUNICORN_THREADS", "2"))
worker_class = "gthread"

# ── Timeouts ──────────────────────────────────────────────────────────────────
timeout      = int(os.environ.get("GUNICORN_TIMEOUT", "120"))
keepalive    = 5

# ── Memory management ─────────────────────────────────────────────────────────
# Recycle workers after N requests to prevent memory leaks.
max_requests        = int(os.environ.get("GUNICORN_MAX_REQUESTS", "500"))
max_requests_jitter = 50

# ── Logging ───────────────────────────────────────────────────────────────────
accesslog = "-"   # stdout → picked up by Docker logs
errorlog  = "-"   # stderr → picked up by Docker logs
loglevel  = os.environ.get("GUNICORN_LOG_LEVEL", "info")
