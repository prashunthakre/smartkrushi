# SmartKrushi - Next-Gen AI Powered Farming Platform 🌱🚀

SmartKrushi is an end-to-end Agriculture E-Commerce & AI Advisory Portal empowering Indian farmers with real-time APMC Mandi rates, AI-driven crop and fertilizer predictions, weather forecasting, an interactive bilingual Kisan Chatbot, and direct-to-customer crop sales.

---

## 📁 Project Architecture

```
.
├── frontend/                   # Complete web application (HTML5, CSS3, JS, UI assets)
│   ├── index.html              # Landing page & APMC live marquee ticker
│   ├── farmer/                 # Farmer dashboard, AI prediction tools, trade & orders
│   ├── customer/               # Customer dashboard, crop marketplace, cart & order history
│   ├── admin/                  # Admin portal & system management
│   ├── assets/                 # Icons, fonts, custom styling, state-district datasets
│   └── js/                     # SmartKrushi Core client-side engine (smart_krushi_core.js)
├── ml/                         # 5 Machine Learning models & agricultural datasets
│   ├── crop_prediction/        # Decision tree crop prediction model & pickle
│   ├── crop_recommendation/    # Soil NPK crop recommendation script & dataset
│   ├── fertilizer_recommendation/ # Fertilizer dosage prediction engine
│   ├── rainfall_prediction/    # Historical rainfall dataset & prediction script
│   └── yield_prediction/       # Farm yield estimator & production dataset
├── smart_krushi_server.py      # Production Python server (HTTP + REST API + ML + SQLite + SMTP)
├── requirements.txt            # Python dependencies for Render / Production
├── Procfile                    # Render Web Service process definition
├── render.yaml                 # Render Blueprint configuration
├── START_SMART_KRUSHI_SERVER.bat # One-click local launcher for Windows
└── .gitignore                  # Git ignore rules
```

---

## 🚀 How to Run Locally

1. Open a terminal in this directory.
2. Run the server:
   ```bash
   python smart_krushi_server.py
   ```
3. Open your browser at:
   ```
   http://localhost:8000
   ```

---

## ☁️ How to Deploy on Render (Step-by-Step)

### Step 1: Push Code to GitHub
1. Initialize a git repository:
   ```bash
   git init
   git add .
   git commit -m "Initial commit for SmartKrushi production release"
   ```
2. Create a new repository on your GitHub account (e.g., `smartkrushi`).
3. Link and push your repository:
   ```bash
   git remote add origin https://github.com/<your-username>/smartkrushi.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Create Web Service on Render
1. Log in to [dashboard.render.com](https://dashboard.render.com/).
2. Click **New +** -> **Web Service**.
3. Connect your GitHub account and choose the `smartkrushi` repository.
4. Fill in the following settings:
   - **Name**: `smartkrushi`
   - **Language**: `Python 3`
   - **Branch**: `main`
   - **Region**: Singapore (Southeast Asia) or any region close to your users
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python smart_krushi_server.py`
   - **Instance Type**: `Free`

### Step 3: Add Environment Variables on Render
Under **Environment Variables**, add the following keys:
- `SMARTKRUSHI_SMTP_EMAIL`: `kushora.otp@gmail.com`
- `SMARTKRUSHI_SMTP_PASS`: `<your-16-character-google-app-password>`

### Step 4: Click "Deploy Web Service"
Render will automatically install the requirements, start `smart_krushi_server.py`, bind the dynamic `PORT`, and provide you with a live URL (e.g., `https://smartkrushi.onrender.com`).

