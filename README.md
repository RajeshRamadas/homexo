<div align="center">

# 🏛️ HOMEXO

### Premium Real Estate & Property Services Platform

**A full-stack Django web application powering a luxury real estate portal with integrated financial, legal, and home services.**

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![DRF](https://img.shields.io/badge/REST_API-DRF_3.15-DC3545?style=for-the-badge)](https://django-rest-framework.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Ready-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-F7DF1E?style=for-the-badge)](LICENSE)

</div>

---

## Overview

HOMEXO is a comprehensive real estate platform that goes beyond property listings. It combines property search, home loan comparison, legal verification, security services, NRI assistance, and a full CRM — all within a single, premium-designed web application.

---

## ✨ Features

### 🏠 Property Platform
- **Property Listings** — Buy, Rent, New Projects, Commercial with advanced filtering & sorting
- **Signature Collection** — Ultra-premium featured property showcase
- **Smart Search** — Filter by city, locality, BHK, price range, property type, furnishing
- **Interactive Floor Plans** — Tabbed 2D/3D viewer with room dimensions and price variants
- **Developer Directory** — Dynamic builder profiles with project portfolios
- **Wishlist** — AJAX-powered save/unsave with dedicated wishlist page

### 💰 Financial Services
- **Home Loan Comparison** — Live EMI calculator with 15+ bank rate comparison grid
- **Dynamic Bank Sliders** — Adjust loan amount & tenure to see real-time EMI across all banks
- **Eligibility Calculator** — Income-based loan eligibility estimation

### ⚖️ Legal Services
- **Legal Verification Orders** — Shield Starter / Pro / Complete packages
- **Case Tracking Dashboard** — Step-by-step order progress with verdict system (Green/Yellow/Red)
- **Advocate Management** — Advocate assignment, self-registration, and client-advocate messaging
- **Payment Tracking** — Payment status, proof uploads, and transaction history

### 🔒 Additional Services
- **Security Services** — CCTV, access control, and home security enquiry system
- **NRI Services** — Dedicated NRI property management, legal, and rental assistance
- **Home Services** — Plumbing, electrical, painting, cleaning, and renovation leads

### 📊 CRM & Admin
- **Enquiry Dashboard** — Full CRM pipeline (New → Contacted → Qualified → Closed)
- **Ticket System** — Activity logs, comments, priority, follow-up scheduling, agent assignment
- **Bulk Actions** — Mass assign, status change, and priority update
- **Email Notifications** — Auto-reply to leads + admin notification with rich HTML emails
- **Source Tracking** — Every enquiry records which page/form it originated from

### 🔐 Authentication
- **Email-Based Login** — Custom user model (no username field)
- **Phone OTP** — SMS-based login via Twilio
- **Social OAuth** — Google and Facebook sign-in
- **Role-Based Access** — Buyer, Seller, Agent, Admin, Customer Support, Legal Admin, Advocate

### 📰 Content
- **Blog & News** — Posts with categories, cover images, key takeaways, and reading time
- **Testimonials** — Customer reviews with ratings, displayed on homepage
- **SEO** — Sitemap, robots.txt, meta tags, semantic HTML

---

## 🏗️ Architecture

```
homexo/
├── homexo/                  # Project configuration
│   ├── settings.py          # Environment-aware settings (dev/prod)
│   ├── urls.py              # Root URL dispatcher
│   ├── api_urls.py          # REST API v1 aggregator
│   ├── sitemaps.py          # SEO sitemaps
│   └── wsgi.py              # WSGI entry point
│
├── accounts/                # Custom User model, auth, OAuth, phone OTP
├── properties/              # Listings, images, floor plans, features, developers
├── enquiries/               # Lead capture, CRM dashboard, activity logs
├── legal_services/          # Legal verification orders, steps, verdicts
├── blog/                    # Posts, categories
├── testimonials/            # Customer reviews
├── wishlist/                # Saved properties
├── pages/                   # All public-facing pages & service pages
│
├── templates/
│   ├── base.html            # Master layout (nav, footer, messages)
│   ├── pages/               # 15 service & content pages
│   ├── properties/          # List, detail, create, update
│   ├── accounts/            # Login, register, profile, OTP
│   ├── enquiries/           # CRM dashboard, ticket detail
│   ├── legal_services/      # Order tracking, advocate dashboard
│   ├── blog/                # List, detail
│   └── wishlist/            # Saved properties list
│
├── static/                  # CSS, JS, icons, images
├── media/                   # User-uploaded files (gitignored)
├── requirements.txt         # Python dependencies
├── env.example              # Environment variable reference
└── manage.py
```

---

## 🗄️ Database Schema

**7 apps · 16 models · SQLite (dev) / PostgreSQL (prod)**

| App | Models | Purpose |
|-----|--------|---------|
| **accounts** | `User`, `PhoneOTP` | Authentication, roles, preferences |
| **properties** | `Property`, `Developer`, `PropertyImage`, `PropertyFloorPlan`, `PropertyFeature`, `PropertyTag`, `ConnectivityItem` | Listings with rich media & metadata |
| **enquiries** | `Enquiry`, `EnquiryActivity` | Lead management & CRM pipeline |
| **legal_services** | `LegalOrder`, `OrderStep`, `VerdictCheck`, `OrderActivity` | Legal verification workflow |
| **blog** | `Post`, `Category` | Content management |
| **testimonials** | `Testimonial` | Customer reviews |
| **wishlist** | `WishlistItem` | Saved properties |

---

## ⚡ Quick Start

### Prerequisites

- Python 3.10+
- pip
- Git

### 1 — Clone

```bash
git clone https://github.com/RajeshRamadas/homexo.git
cd homexo
```

### 2 — Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows
```

### 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### 4 — Configure Environment

```bash
cp env.example .env
# Edit .env if needed — defaults work out of the box for local dev
```

### 5 — Migrate & Create Admin

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6 — Seed Sample Data (Optional)

```bash
python manage.py seed_data
```

Creates sample properties, agents, testimonials, and blog posts.

### 7 — Run

```bash
python manage.py runserver
```

| URL | Description |
|-----|-------------|
| https://homexo.in/ | Homepage |
| https://homexo.in/admin/ | Admin Panel |
| https://homexo.in/properties/ | Property Listings |
| https://homexo.in/services/home-loan/ | Home Loan Comparison |
| https://homexo.in/services/legal/ | Legal Services |
| https://homexo.in/services/security/ | Security Services |
| https://homexo.in/services/nri/ | NRI Services |
| https://homexo.in/developers/ | Developer Directory |
| https://homexo.in/blog/ | Blog & News |
| https://homexo.in/api/v1/ | REST API |

---

## 🔌 REST API

All API endpoints are under `/api/v1/`. Authentication via DRF Token — include `Authorization: Token <token>` in headers.

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/accounts/register/` | Register new user |
| `POST` | `/api/v1/accounts/login/` | Login, receive token |
| `POST` | `/api/v1/accounts/logout/` | Invalidate token |
| `GET/PUT` | `/api/v1/accounts/me/` | View / update profile |

### Properties

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/properties/` | List with filters |
| `POST` | `/api/v1/properties/` | Create listing |
| `GET` | `/api/v1/properties/<slug>/` | Property detail |
| `PUT` | `/api/v1/properties/<slug>/` | Update listing |
| `DELETE` | `/api/v1/properties/<slug>/` | Delete listing |
| `GET` | `/api/v1/properties/featured/` | Featured properties |
| `GET` | `/api/v1/properties/signature/` | Signature collection |

**Query Parameters:**
```
?type=buy|rent|new_project|commercial
?property_type=apartment|villa|penthouse|plot|office
?city=Bengaluru
?bhk=2bhk|3bhk|4bhk
?min_price=5000000&max_price=30000000
?search=whitefield
?ordering=price|-price|created_at|-views_count
```

### Other Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/blog/posts/` | Blog posts |
| `GET` | `/api/v1/blog/categories/` | Blog categories |
| `POST` | `/api/v1/enquiries/` | Submit enquiry |
| `GET` | `/api/v1/wishlist/` | Saved properties |
| `POST` | `/api/v1/wishlist/toggle/<id>/` | Toggle save/unsave |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Django 4.2, Python 3.12 |
| **API** | Django REST Framework 3.15 |
| **Database** | SQLite (dev) → PostgreSQL (prod) |
| **Auth** | Custom `AbstractBaseUser` + Token Auth + Google/Facebook OAuth + Phone OTP |
| **Email** | Django Email (SMTP / Console backend) |
| **Images** | Pillow |
| **CORS** | django-cors-headers |
| **Frontend** | Django Templates, Vanilla JS, Vanilla CSS |
| **Fonts** | Google Fonts — Inter, Jost, Playfair Display |
| **Icons** | Inline SVGs (zero dependencies) |
| **Server** | Gunicorn + Nginx (production) |

---

## 🚀 Production Deployment

The project is configured for **DigitalOcean Droplet** deployment with:

- **Gunicorn** — WSGI application server
- **Nginx** — Reverse proxy, SSL termination, static/media serving
- **PostgreSQL** — Production database
- **Let's Encrypt** — Free SSL certificates
- **systemd** — Process management with auto-restart

### Environment-Aware Settings

The `settings.py` reads from environment variables with safe development defaults:

```bash
# Production .env
SECRET_KEY=your-64-char-secret
DEBUG=False
ALLOWED_HOSTS=homexo.in,www.homexo.in
DB_ENGINE=django.db.backends.postgresql
DB_NAME=homexo_db
DB_USER=homexo_user
DB_PASSWORD=strong-password
```

When `DEBUG=False`, production security settings auto-activate:
- HTTPS redirect
- Secure cookies
- HSTS headers
- Content-Type sniffing protection

### Deploy

```bash
pip install gunicorn psycopg2-binary
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn homexo.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

---

## 📁 Environment Variables

See [`env.example`](env.example) for the full list. Key variables:

| Variable | Purpose | Default |
|----------|---------|---------|
| `SECRET_KEY` | Django secret | Dev placeholder |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Comma-separated domains | `*` |
| `DB_ENGINE` | Database backend | SQLite |
| `EMAIL_BACKEND` | Email delivery | Console (prints to terminal) |
| `GOOGLE_OAUTH2_KEY` | Google sign-in | — |
| `TWILIO_ACCOUNT_SID` | Phone OTP via SMS | — (prints to console in dev) |

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <sub>Built with ❤️ by Rajesh Kumar Ramadas</sub>
</div>
