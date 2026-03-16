<div align="center">

```
  ╱╲
 ╱  ╲
╱____╲  HOMEXO
```

# HOMEXO — Luxury Real Estate Portal

**A full-stack Django web application for a luxury real estate platform.**  
Built with Django 4.2, Django REST Framework, and a bespoke navy-and-sky design system.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2-green?style=flat-square&logo=django)](https://djangoproject.com)
[![DRF](https://img.shields.io/badge/DRF-3.15-red?style=flat-square)](https://django-rest-framework.org)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

</div>

---

## 📸 Features

| Feature | Details |
|---|---|
| 🏠 **Property Listings** | Buy, Rent, New Projects, Commercial with advanced filtering |
| 💎 **Signature Collection** | Ultra-premium featured property showcase |
| 🔍 **Smart Search** | Filter by location, type, BHK, price range, sort options |
| 👤 **Authentication** | Custom email-based User model with roles (Buyer / Seller / Agent / Admin) |
| 🤝 **Agent Profiles** | RERA-verified agent pages with listings and contact |
| 💾 **Wishlist** | AJAX-powered save/unsave properties |
| 📩 **Enquiry CRM** | Lead capture form with email notification and status pipeline |
| 📰 **Blog & News** | Post management with categories, cover images, related posts |
| 🧮 **EMI Calculator** | Live slider-based home loan calculator with canvas pie chart |
| 🔌 **REST API** | Full DRF API with token authentication for all core resources |
| ⚙️ **Admin Panel** | Rich Django admin with image thumbnails, inline editors, list_editable |
| 🌱 **Seed Data** | One command seeds 10 properties, 3 agents, testimonials, blog posts |

---

## 🗂️ Project Structure

```
homexo/
├── homexo/                  # Project config
│   ├── settings.py          # All settings (DB, DRF, CORS, email, auth)
│   ├── urls.py              # Root URL dispatcher
│   ├── api_urls.py          # /api/v1/ aggregator
│   └── wsgi.py
│
├── accounts/                # Custom User model, auth views & API
├── properties/              # Core listing models, views, API, admin
├── agents/                  # Agent profiles linked to User
├── enquiries/               # Lead capture + CRM status pipeline
├── blog/                    # Posts, categories, news carousel
├── testimonials/            # Client reviews
├── wishlist/                # Saved properties (AJAX toggle)
├── pages/                   # Home, About, FAQ, EMI Calculator
│   └── management/
│       └── commands/
│           └── seed_data.py # 🌱 Sample data generator
│
├── templates/               # All HTML templates
│   ├── base.html            # Master layout (nav, footer, messages)
│   ├── pages/               # home.html, emi_calculator.html
│   ├── properties/          # list, detail, create, update, delete
│   ├── agents/              # list, detail
│   ├── blog/                # list, detail
│   ├── accounts/            # login, register, profile
│   ├── enquiries/           # form, success
│   └── wishlist/            # list
│
├── static/
│   └── css/homexo.css       # Supplemental styles
│
├── requirements.txt
├── .env.example             # Environment variable reference
├── .gitignore
└── manage.py
```

---

## ⚡ Quick Start

### 1 — Clone & Unzip

```bash
unzip homexo_django_project.zip
cd homexo
```

### 2 — Create Virtual Environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### 4 — Configure Environment

```bash
cp env.example .env
# Edit .env with your settings (optional for local dev — defaults work out of the box)
```

### 5 — Run Migrations

```bash
python manage.py makemigrations accounts properties agents enquiries blog testimonials wishlist
python manage.py migrate
```

### 6 — Seed Sample Data

```bash
python manage.py seed_data
```

This creates:
- 1 superuser (`admin@homexo.in` / `admin123`)
- 3 verified agents with profiles
- 10 property listings (mix of buy/rent/commercial/signature)
- 7 property tags (Pool, Gym, Clubhouse, etc.)
- 3 client testimonials
- 3 blog posts under Market Reports

### 7 — Run the Server

```bash
python manage.py runserver
```

| URL | Description |
|---|---|
| `http://127.0.0.1:8000/` | Homepage |
| `http://127.0.0.1:8000/admin/` | Admin Panel |
| `http://127.0.0.1:8000/api/v1/` | REST API root |

---

## 🔌 REST API Reference

All API endpoints are under `/api/v1/`. Token authentication is used — include `Authorization: Token <token>` in the header after login.

### Auth

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/api/v1/accounts/register/` | Register a new user | Public |
| `POST` | `/api/v1/accounts/login/` | Login, receive token | Public |
| `POST` | `/api/v1/accounts/logout/` | Invalidate token | Required |
| `GET/PUT` | `/api/v1/accounts/me/` | View / update own profile | Required |

### Properties

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/api/v1/properties/` | List with filters | Public |
| `POST` | `/api/v1/properties/` | Create listing | Required |
| `GET` | `/api/v1/properties/<slug>/` | Property detail | Public |
| `PUT` | `/api/v1/properties/<slug>/` | Update listing | Owner |
| `DELETE` | `/api/v1/properties/<slug>/` | Delete listing | Owner |
| `GET` | `/api/v1/properties/featured/` | Featured properties | Public |
| `GET` | `/api/v1/properties/signature/` | Signature collection | Public |
| `GET` | `/api/v1/properties/my_listings/` | My own listings | Required |

**Query Parameters:**
```
?type=buy|rent|new_project|commercial
?property_type=apartment|villa|penthouse|plot|office
?city=Bengaluru
?bhk=1bhk|2bhk|3bhk|4bhk
?min_price=5000000
?max_price=30000000
?search=whitefield
?ordering=price|-price|created_at|-views_count
?page=2
```

### Other Endpoints

```
GET   /api/v1/agents/                  List all agents
GET   /api/v1/agents/<id>/             Agent detail
GET   /api/v1/blog/posts/              Blog posts
GET   /api/v1/blog/posts/<slug>/       Post detail
GET   /api/v1/blog/categories/         Blog categories
POST  /api/v1/enquiries/               Submit enquiry
GET   /api/v1/wishlist/                Saved properties
POST  /api/v1/wishlist/toggle/<id>/    Toggle save/unsave
```

---

## 🗃️ Data Models

### Property

```python
listing_type    # buy | rent | new_project | commercial
property_type   # apartment | villa | penthouse | plot | office | shop | warehouse
price           # DecimalField — display_price property auto-formats to ₹Cr / ₹L
is_featured     # Appears in homepage carousel
is_signature    # Ultra-premium collection
status          # active | sold | rented | pending | draft | inactive
```

### User (Custom)

```python
email           # Primary identifier (instead of username)
role            # buyer | seller | agent | admin
is_verified     # Email verification flag
```

### Enquiry (CRM)

```python
status          # new → contacted → qualified → closed | lost
enquiry_type    # buy | rent | sell | home_loan | general
```

---

## 🏗️ Apps Overview

| App | Key Models | Key Views |
|---|---|---|
| `accounts` | `User` | register, login, logout, profile, profile_update |
| `properties` | `Property`, `PropertyImage`, `PropertyFeature`, `PropertyTag` | list, detail, create, update, delete |
| `agents` | `Agent` | list, detail |
| `enquiries` | `Enquiry` | create, success |
| `blog` | `Post`, `Category` | list, detail |
| `testimonials` | `Testimonial` | (used in homepage context) |
| `wishlist` | `WishlistItem` | list, toggle (AJAX), remove |
| `pages` | — | home, about, faq, area_guides, market_reports, emi_calculator |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 4.2 |
| API | Django REST Framework 3.15 |
| Auth | Custom `AbstractBaseUser` + DRF Token Auth |
| Database | SQLite (dev) → PostgreSQL (production) |
| Images | Pillow |
| CORS | django-cors-headers |
| Frontend | Django Templates + vanilla JS |
| Fonts | Google Fonts — Cormorant Garamond, DM Sans |

---

## 🚀 Production Checklist

Before deploying to production:

- [ ] Set `DEBUG=False` in `.env`
- [ ] Set a strong `SECRET_KEY`
- [ ] Set `ALLOWED_HOSTS` to your domain
- [ ] Switch `DATABASES` to PostgreSQL
- [ ] Configure SMTP email settings
- [ ] Run `python manage.py collectstatic`
- [ ] Set up media file storage (AWS S3 recommended)
- [ ] Enable HTTPS / SSL
- [ ] Set `CORS_ALLOW_ALL_ORIGINS=False` and whitelist your frontend domain
- [ ] Use Gunicorn + Nginx in production

```bash
# Install production extras
pip install gunicorn psycopg2-binary django-storages boto3

# Collect static
python manage.py collectstatic --noinput

# Start with Gunicorn
gunicorn homexo.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

---

## 👤 Default Credentials

> ⚠️ **Change these immediately after setup.**

| Role | Email | Password |
|---|---|---|
| Admin | `admin@homexo.in` | `admin123` |
| Agent 1 | `priya@homexo.in` | `agent123` |
| Agent 2 | `rahul@homexo.in` | `agent123` |
| Agent 3 | `ananya@homexo.in` | `agent123` |

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- UI Design: Inspired by the **HOMEXO** luxury real estate HTML template
- Fonts: [Cormorant Garamond](https://fonts.google.com/specimen/Cormorant+Garamond) & [DM Sans](https://fonts.google.com/specimen/DM+Sans) via Google Fonts
- Icons: Inline SVGs (no external icon library dependency)

---

<div align="center">
  <sub>Built with ❤️ for the HOMEXO luxury real estate portal.</sub>
</div>
