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
[![Transformers](https://img.shields.io/badge/Transformers-HuggingFace-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/)
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)](LICENSE)

<br/>

> **Developed with ❤️ by [@chethanhrx](https://github.com/chethanhrx)**

</div>

---

## 🔍 What is ReviewGuard?

**ReviewGuard** is a full-stack Django web application that detects whether a product review is genuinely written by a human — or fabricated by a machine.

By combining a **custom NLP rule-based engine** with a **hybrid ML integration (DistilBERT)**, ReviewGuard accurately scores and classifies reviews into:

| Label | Meaning |
|-------|---------|
| 🤖 **CG** | Computer Generated — Likely Fake |
| 🧑 **OR** | Original Review — Human Written |

---

## ✨ Features

- 🧠 **Hybrid Detection Engine** — A highly accurate 20+ signal NLP scorer combined with an optional zero-shot DistilBERT ML integration.
- 🔐 **Dual Authentication** — Separate secure login flows for end-users and administrators.
- 📊 **Admin Dashboard** — Full visibility into user activity, classification rates, and review data.
- 📝 **Review History** — Users can submit text and track all their past review analyses.
- 📈 **Visual Analytics** — Beautiful, responsive charts powered by Chart.js.
- ⚡ **Graceful Degradation** — If packages like `torch` and `transformers` are missing, the system automatically falls back to the robust offline rules-based ML simulator.

---

## 🧠 How Detection Works

The core logic lives in `reviews/detector.py`. Each review is scored using weighted linguistic heuristics mixed with ML model probabilities to assign a confidence percentage:

1. **Short/Ambiguous overrides** checks for lack of semantic context vs human shorthand (`thank u`, emojis).
2. **Feature Extraction** checks for vocabulary diversity, sentence variation, extreme ALL CAPS, superlative saturation, marketing phrasing, and contextual storytelling.
3. **Machine Learning Pipeline (Optional)** feeds the text through an onboard DistilBERT classifier. If it spots strong text hallmarks, it dynamically boosts the CG (Fake) or OR (Human) scores.

---

## 🚀 Getting Started (Step-by-Step Setup)

ReviewGuard runs locally on **Windows**, **macOS**, and **Linux**.

### Prerequisites
- [Python 3.10+](https://www.python.org/downloads/) installed.
- Git installed.

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/chethanhrx/Fake-Review-Detection-System.git
cd Fake-Review-Detection-System
```

---

### 2️⃣ Virtual Environment & Dependencies

It is **highly recommended** to use a Virtual Environment (`venv`) so you don't break your system-wide Python packages. Choose your operating system below:

#### 🪟 For Windows Users:
Open Command Prompt (`cmd`) or PowerShell inside the project folder:
```cmd
:: Create the virtual environment
python -m venv venv

:: Activate it
venv\Scripts\activate

:: Install dependencies
pip install -r requirements.txt
```

#### 🐧 For Linux (Ubuntu / Debian) Users:
On modern Linux distributions, you may need to install the `venv` package first. Open your Terminal:
```bash
# 1. Install prerequisites (if not already installed)
sudo apt update
sudo apt install python3-venv python3-pip

# 2. Create the virtual environment
python3 -m venv venv

# 3. Activate it
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

#### 🍏 For macOS Users:
Open your Terminal inside the project folder:
```bash
# 1. Create the virtual environment
python3 -m venv venv

# 2. Activate it
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

*(Note: Your terminal prompt should now show `(venv)` at the beginning of the line!)*

---

### 3️⃣ Setup Database & Run Server
Run the following commands (still inside your activated `venv`):

```bash
# Apply the database tables
python manage.py makemigrations
python manage.py migrate

# Launch the Application
python manage.py runserver
```

---

### 4️⃣ Open in Browser
Visit the following link in your local web browser:
```
http://127.0.0.1:8000/
```

---

## 🔁 Returning Later?
If you close your terminal and want to run the project again tomorrow, you **must activate the `venv` first**.

**Windows:**
```cmd
cd Fake-Review-Detection-System
venv\Scripts\activate
python manage.py runserver
```

**Linux/macOS:**
```bash
cd Fake-Review-Detection-System
source venv/bin/activate
python manage.py runserver
```

---

## 🔑 Admin Access
To test out the Admin interface, register for a new admin account via `/admin-panel/register/` and use the secret key below:

```
REVIEWGUARD-ADMIN-2024
```
*(You can change this globally in `reviewguard/settings.py` → `ADMIN_SECRET_KEY`)*

---

## 📁 Project Structure

```
reviewguard/
├── manage.py
├── requirements.txt
├── db.sqlite3
├── venv/                     # Virtual environment (ignored by Git)
│
├── reviewguard/              # ⚙️  Project config
│   ├── settings.py
│   └── urls.py
│
├── users/                    # 👤 User auth & dashboard logic
├── reviews/                  # 📝 Review submission & detection
│   └── detector.py           # ← 🧠 Hybrid NLP/ML detection engine
├── admin_panel/              # 🛡️  Admin portal
├── templates/                # 🎨 HTML templates
└── static/                   # 🖼️  CSS, JS, Images
```

---

## 🚨 Common Troubleshooting

<details>
<summary><b>❌ <code>error: externally-managed-environment</code> when running pip install</b></summary>
<br>
You forgot to activate the virtual environment! Run <code>source venv/bin/activate</code> (Linux/Mac) or <code>venv\Scripts\activate</code> (Windows) first, then try running the pip install command again.
</details>

<details>
<summary><b>❌ <code>no such table: reviews_review</code></b></summary>
<br>
You haven't built the initial database yet. Make sure to run:<br>
<code>python manage.py makemigrations</code><br>
<code>python manage.py migrate</code>
</details>

<details>
<summary><b>❌ <code>No module named 'django'</code></b></summary>
<br>
Your virtual environment is not activated. Look for `(venv)` in your prompt before running python commands.
</details>

<details>
<summary><b>❌ <code>Command 'python' not found</code> (Linux/Mac)</b></summary>
<br>
Use <code>python3</code> for all commands instead of <code>python</code>, or install the global alias (<code>sudo apt install python-is-python3</code>).
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