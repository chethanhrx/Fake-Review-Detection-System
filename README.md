<div align="center">

```
██████╗ ███████╗██╗   ██╗██╗███████╗██╗    ██╗ ██████╗ ██╗   ██╗ █████╗ ██████╗ ██████╗
██╔══██╗██╔════╝██║   ██║██║██╔════╝██║    ██║██╔════╝ ██║   ██║██╔══██╗██╔══██╗██╔══██╗
██████╔╝█████╗  ██║   ██║██║█████╗  ██║ █╗ ██║██║  ███╗██║   ██║███████║██████╔╝██║  ██║
██╔══██╗██╔══╝  ╚██╗ ██╔╝██║██╔══╝  ██║███╗██║██║   ██║██║   ██║██╔══██║██╔══██╗██║  ██║
██║  ██║███████╗ ╚████╔╝ ██║███████╗╚███╔███╔╝╚██████╔╝╚██████╔╝██║  ██║██║  ██║██████╔╝
╚═╝  ╚═╝╚══════╝  ╚═══╝  ╚═╝╚══════╝ ╚══╝╚══╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝
```

### 🛡️ Fake Review Detection System

*Can your review pass the test?*

<br/>

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![NLP](https://img.shields.io/badge/NLP-Rule--Based-FF6B6B?style=for-the-badge&logo=buffer&logoColor=white)]()
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)](LICENSE)

<br/>

> **Developed with ❤️ by [@chethanhrx](https://github.com/chethanhrx)**

</div>

---

## 🔍 What is ReviewGuard?

**ReviewGuard** is a full-stack Django web application that uses a custom **NLP rule-based engine** to detect whether a product review is genuinely written by a human — or fabricated by a machine.

Every review gets scanned, scored, and labelled as:

| Label | Meaning |
|-------|---------|
| 🤖 **CG** | Computer Generated — Likely Fake |
| 🧑 **OR** | Original Review — Human Written |

No ML models. No external APIs. Pure linguistic intelligence.

---

## ✨ Features

- 🔐 **Dual Authentication** — Separate login flows for Users and Admins
- 📊 **Admin Dashboard** — Full visibility into all users and submitted reviews
- 🧠 **Smart Detection Engine** — 7-rule NLP scorer with confidence display up to 98%
- 📝 **Review History** — Users can track all their past submissions
- 📈 **Visual Analytics** — Powered by Chart.js
- ⚡ **Zero External Dependencies** — No ML frameworks, no API keys, no paid services

---

## 🧠 How Detection Works

The core logic lives in `reviews/detector.py`. Each review is scored **0–100** using 7 handcrafted linguistic rules:

```
Score ≥ 45  →  🤖 CG (Fake)
Score < 45  →  🧑 OR (Human)
```

| # | Rule | Signal |
|---|------|--------|
| 1 | Review has fewer than 8 words | 🔴 Fake |
| 2 | Contains generic phrases like *"highly recommend"*, *"great product"* | 🔴 Fake |
| 3 | Missing personal pronouns (*I*, *my*, *we*) | 🔴 Fake |
| 4 | Excessive `!!!` or ALL CAPS usage | 🔴 Fake |
| 5 | Suspiciously uniform sentence lengths | 🔴 Fake |
| 6 | Informal language (*lol*, *tbh*, *kinda*) | 🟢 Human |
| 7 | Specific personal details (family, time, comparisons) | 🟢 Human |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Git

---

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/chethanhrx/Fake-Review-Detection-System.git
cd Fake-Review-Detection-System
```

### 2️⃣ Create & Activate Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows
```

> Your terminal prompt will show `(venv)` when active ✅

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5️⃣ Start the Server

```bash
python manage.py runserver
```

### 6️⃣ Open in Browser

```
http://127.0.0.1:8000/
```

---

## 🔁 Returning Later?

Every time you open a new terminal, activate the venv first:

```bash
cd Fake-Review-Detection-System
source venv/bin/activate
python manage.py runserver
```

---

## 🗺️ Pages & Routes

| Page | URL |
|------|-----|
| 🏠 Home | `/` |
| ℹ️ About | `/about/` |
| ❓ How It Works | `/how-it-works/` |
| 👤 User Register | `/users/register/` |
| 🔑 User Login | `/users/login/` |
| 📊 User Dashboard | `/users/dashboard/` |
| ✍️ Submit Review | `/reviews/submit/` |
| 📋 My Reviews | `/reviews/my-reviews/` |
| 🛡️ Admin Register | `/admin-panel/register/` |
| 🔐 Admin Login | `/admin-panel/login/` |
| 📈 Admin Dashboard | `/admin-panel/dashboard/` |
| 📝 Admin Reviews | `/admin-panel/reviews/` |
| 👥 Admin Users | `/admin-panel/users/` |

---

## 🔑 Admin Access

To register as an admin, use the secret key below:

```
REVIEWGUARD-ADMIN-2024
```

> You can change this in `reviewguard/settings.py` → `ADMIN_SECRET_KEY`

---

## 📁 Project Structure

```
reviewguard/
├── manage.py
├── requirements.txt
├── db.sqlite3
├── venv/                     # Virtual environment (do not commit)
│
├── reviewguard/              # ⚙️  Project config
│   ├── settings.py
│   ├── urls.py
│   └── views.py
│
├── users/                    # 👤 User auth & dashboard
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
│
├── reviews/                  # 📝 Review submission & detection
│   ├── detector.py           # ← 🧠 Core NLP detection logic
│   ├── models.py
│   ├── urls.py
│   └── views.py
│
├── admin_panel/              # 🛡️  Admin portal
│   ├── urls.py
│   └── views.py
│
├── templates/                # 🎨 HTML templates
│   ├── base.html
│   ├── home.html
│   ├── about.html
│   ├── how_it_works.html
│   ├── users/
│   ├── reviews/
│   └── admin_panel/
│
└── static/                   # 🖼️  CSS, JS, Images
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| 🐍 Backend | Django 4.2 (Python 3.12) |
| 🗄️ Database | SQLite (development) |
| 🧠 Detection | Custom NLP Rule-Based Engine |
| 🎨 Frontend | HTML5, CSS3, JavaScript, Chart.js |
| 🔐 Auth | Django Built-in Auth System |

---

## 🚨 Common Issues & Fixes

<details>
<summary><b>❌ <code>no such table: reviews_review</code></b></summary>

You haven't applied migrations yet.

```bash
python manage.py makemigrations
python manage.py migrate
```
</details>

<details>
<summary><b>❌ <code>No module named 'django'</code></b></summary>

Your virtual environment is not activated.

```bash
source venv/bin/activate
```
</details>

<details>
<summary><b>❌ <code>ModuleNotFoundError</code> on any package</b></summary>

Install all dependencies.

```bash
pip install -r requirements.txt
```
</details>

<details>
<summary><b>❌ <code>Command 'python' not found</code></b></summary>

Use `python3` instead, or install the alias.

```bash
sudo apt install python-is-python3
```
</details>

---

## 👨‍💻 Author

<div align="center">


### [@chethanhrx](https://github.com/chethanhrx)

*Building tools that think.*

[![GitHub](https://img.shields.io/badge/GitHub-chethanhrx-181717?style=for-the-badge&logo=github)](https://github.com/chethanhrx)

</div>

---

<div align="center">

Made with ☕ and Python &nbsp;·&nbsp; Star ⭐ this repo if you found it useful!

</div>