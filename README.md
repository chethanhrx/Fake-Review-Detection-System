# ReviewGuard — Fake Review Detection System

> Django · Python 3.12 · SQLite · NLP Rule-Based Engine

---

## 📋 Overview

**ReviewGuard** is a full-stack Django web application that detects whether a product review is:

- 🤖 **CG** — Computer Generated (Fake)
- 🧑 **OR** — Original Review (Human Written)

It uses a custom rule-based NLP engine to score reviews based on language patterns, personal pronouns, sentence structure, and more.

---

## ⚙️ Setup Guide

### Prerequisites
- Python 3.10 or higher
- pip
- Git

---

### Step 1 — Clone the Repository

```bash
git clone <your-repo-url>
cd reviewguard
```

---

### Step 2 — Create a Virtual Environment

```bash
python3 -m venv venv
```

---

### Step 3 — Activate the Virtual Environment

**Linux / macOS:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

> Your terminal prompt will change to `(venv)` when activated.

---

### Step 4 — Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Step 5 — Create Migration Files

```bash
python manage.py makemigrations
```

---

### Step 6 — Apply Migrations (Create Database Tables)

```bash
python manage.py migrate
```

---

### Step 7 — Start the Development Server

```bash
python manage.py runserver
```

---

### Step 8 — Open in Browser

```
http://127.0.0.1:8000/
```

---

## 🔁 Starting the Server Again Later

Every time you open a new terminal, activate the venv first:

```bash
cd reviewguard
source venv/bin/activate       # Linux/macOS
python manage.py runserver
```

---

## 🔑 Admin Secret Key

To register as an admin, use this secret key:

```
REVIEWGUARD-ADMIN-2024
```

You can change it in `reviewguard/settings.py` → `ADMIN_SECRET_KEY`

---

## 📄 Pages

| Page              | URL                        |
|-------------------|----------------------------|
| Home              | `/`                        |
| About             | `/about/`                  |
| How It Works      | `/how-it-works/`           |
| User Register     | `/users/register/`         |
| User Login        | `/users/login/`            |
| User Dashboard    | `/users/dashboard/`        |
| Submit Review     | `/reviews/submit/`         |
| My Reviews        | `/reviews/my-reviews/`     |
| Admin Register    | `/admin-panel/register/`   |
| Admin Login       | `/admin-panel/login/`      |
| Admin Dashboard   | `/admin-panel/dashboard/`  |
| Admin Reviews     | `/admin-panel/reviews/`    |
| Admin Users       | `/admin-panel/users/`      |

---

## 🛠️ Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Backend    | Django 4.2 (Python)                 |
| Database   | SQLite (development)                |
| Detection  | Custom NLP rule-based engine        |
| Frontend   | HTML5, CSS3, JavaScript, Chart.js   |
| Auth       | Django built-in auth system         |

---

## 📁 Project Structure

```
reviewguard/
├── manage.py
├── requirements.txt
├── db.sqlite3
├── venv/                     # Virtual environment (do not commit)
├── reviewguard/              # Project config
│   ├── settings.py
│   ├── urls.py
│   └── views.py
├── users/                    # User auth & dashboard
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── reviews/                  # Review submission & detection
│   ├── detector.py           # ← CG/OR detection logic
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── admin_panel/              # Admin portal
│   ├── urls.py
│   └── views.py
├── templates/                # HTML templates
│   ├── base.html
│   ├── home.html
│   ├── about.html
│   ├── how_it_works.html
│   ├── users/
│   ├── reviews/
│   └── admin_panel/
└── static/                   # CSS, JS, Images
```

---

## 🧠 How Detection Works

The `reviews/detector.py` scores each review from **0 to 100** using 7 rules:

| Rule | Indicator |
|------|-----------|
| Very short review (< 8 words) | → CG |
| Generic phrases ("highly recommend", "great product", etc.) | → CG |
| No personal pronouns ("I", "my", "we") | → CG |
| Excessive exclamation marks or ALL CAPS | → CG |
| Uniform sentence lengths | → CG |
| Informal words ("lol", "tbh", "kinda") | → OR |
| Specific personal details (family, time, comparisons) | → OR |

- Score **≥ 45** → Labeled **CG**
- Score **< 45** → Labeled **OR**
- Confidence shown up to **98%**

---

## 🚨 Common Issues

### `no such table: reviews_review`
You haven't run migrations yet. Fix:
```bash
python manage.py makemigrations
python manage.py migrate
```

### `No module named 'django'`
Your virtual environment is not activated. Fix:
```bash
source venv/bin/activate
```

### `ModuleNotFoundError` on any package
Install dependencies:
```bash
pip install -r requirements.txt
```
# Fake-Review-Detection-System
# Fake-Review-Detection-System
