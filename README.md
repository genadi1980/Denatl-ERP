# Radev Clinic Web Portal & Gated Dental ERP (100% Cloud-Native & Local Offline)

Welcome to the official, production-ready source code repository of the **Radev Clinic Dental Suite**. This project houses a beautiful, high-performance patient-facing marketing website integrated seamlessly with a secure, offline-first/cloud-ready **Dental ERP** administrative dashboard. 

---

## 1. Architectural Topology & System Overview

The system is engineered as a decoupled, multi-tier web application capable of running **100% locally and offline** (using local SQLite databases and local AI models) or **100% cloud-hosted** (using Vercel, Render, and cloud-managed Supabase Postgres/Auth).

```
                      +-----------------------------------------------------------+
                      |                      FRONTEND (SPA)                       |
                      |            Vite + React + Tailwind CSS + Vercel           |
                      |                                                           |
                      |     +--------------------+      +--------------------+    |
                      |     |   PUBLIC CLINIC    |      |    INTERNAL ERP    |    |
                      |     |  (Landing Page)    | ===> |     DASHBOARD      |    |
                      |     |  (Google Calendar) |      | (Staff Password Gate)   |
                      |     +--------------------+      +--------------------+    |
                      +------------------+-----------------------+----------------+
                                         |                       |
                                         | HTTPS REST            | Local/Cloud APIs
                                         v                       v
                      +------------------+-----------------------+----------------+
                      |                       BACKEND (API)                       |
                      |          FastAPI + SQLAlchemy + Docker + Render           |
                      |                                                           |
                      |   +--------------------+     +------------------------+   |
                      |   |  BACKGROUND TASK   |     |    REST API SERVICES   |   |
                      |   |   (Thread Pool)    |     |  (Products, Inventory, |   |
                      |   | (Playwright Engine)|     |       AI Reports)      |   |
                      |   +---------+----------+     +-----------+------------+   |
                      +-------------|----------------------------|----------------+
                                    | PostgreSQL Writes          | Direct Queries
                                    +--------------+-------------+
                                                   |
                                                   v
                      +----------------------------+------------------------------+
                      |                   DATABASE & CORES                       |
                      |                                                           |
                      |  +------------------------+    +-----------------------+  |
                      |  |     SUPABASE CLOUD     |    |    LOCAL SQLITE       |  |
                      |  | (PostgreSQL, Pools-6543)| OR |  (dental_tracker.db)  |  |
                      |  +------------------------+    +-----------------------+  |
                      |                                                           |
                      |  +------------------------+    +-----------------------+  |
                      |  |   GOOGLE GEMINI API    |    |   LOCAL OFFLINE OLLAMA|  |
                      |  | (Classic GenerativeAI) | OR | (qwen2.5:1.5b Model)  |  |
                      |  +------------------------+    +-----------------------+  |
                      +-----------------------------------------------------------+
```

---

## 2. Module Interconnectivity & Data Flow

### A. Authentication & Staff Authorization Gate
* To protect sensitive administrative capabilities (stock editing, scraper triggers, AI insights) without cloud dependencies, a **Lightweight Client-Side Password Gate** is enforced.
* Staff authenticate via the `/login` route using the preconfigured clinic access key: **`radevdent2026`**.
* Once authenticated, a secure local session is established (`localStorage`), granting the browser full access to `/erp` and passing the mock token to the backend.

### B. Product Inventory & Stock Management
1. The frontend (`Erp.jsx`) loads the catalog via `GET /products`.
2. When a staff member alters stock values (via the interactive stepper modal), the frontend fires `PUT /products/{product_id}/inventory`.
3. The backend validates the request, updates the local SQLite/Supabase Postgres tables, and instantly returns the new data block.

### C. Live Web Scraper Sync (Playwright Core)
1. Triggered via `POST /scraper/run` (or the "СТАРТИРАЙ СКРЕЙПЪР" dashboard button).
2. FastAPI delegates the task natively to its internal **`BackgroundTasks` thread pool** (safely preventing container timeout blockages).
3. The scraper spawns Playwright headless Chromium instances to search **Dentstore.bg**, **Patricia.bg**, and **Belvezar.com** for: `"everX"`, `"G-aenial"`, `"G-Premio"`, and `"C-Pilot"`.
4. Extracted promotional and standard prices are cleaned, parsed into exact Decimals, and committed directly to the database.

### D. AI Promotion Synthesis (Dual-Engine Fallback)
1. Triggered via `GET /promotions/analyze?provider=gemini` (or "AI ЦЕНОВИ АНАЛИЗ" dashboard button).
2. **Primary (Google Gemini Cloud):** The backend builds a unified prompt representing current discounts $\ge 15\%$, calculates exact potential savings in Python, and calls Google Gemini API using the secure **`google-generativeai` REST SDK** (which is immune to local gcloud OAuth conflicts).
3. **Secondary (Ollama Local Offline):** If Gemini fails or is unconfigured, the system automatically redirects to **Local Ollama** connecting on `127.0.0.1:11434` to run the **`qwen2.5:1.5b`** model completely offline with zero credentials required!
4. **Self-Healing Fallback UI:** If both engines are unconfigured or down, the backend gracefully catches the error and returns a beautiful inline Bulgarian user guide instructing staff on how to activate their keys, keeping the app 100% stable and crash-free.

---

## 3. Technology Stack Specifications

### Frontend Single Page Application (SPA)
* **Vite + React 18:** Providing rapid development server boot speeds and optimal production builds.
* **Tailwind CSS:** Fully styled with Radev Clinic's luxury-clinical color palette:
  * Primary Navy: `#0B2545`
  * Secondary Slate Blue: `#134074`
  * Golden Accent: `#C5A880`
  * Clinical Soft Ice: `#F4F7F6`
* **React Router DOM:** Managing seamless hash-routing (`#/`, `#/login`, `#/erp`) to ensure error-free routing on static-hosting servers.
* **Lucide React:** Premium vector outlines and active icons.

### Backend REST API Service
* **FastAPI:** High-performance, asynchronous Python ASGI web framework.
* **SQLAlchemy ORM:** Providing dynamic SQL generation supporting SQLite and PostgreSQL engines out of the box.
* **psycopg2-binary:** Enterprise-grade PostgreSQL adapter for Supabase cloud transactions.
* **python-jose:** Lightweight JWT decoding for staff tokens.

---

## 4. Environment Variables Configuration

The application reads configurations dynamically from `.env` files. Ensure these are set up correctly on your local disk.

### A. Local Backend Configurations (`.env` in main root folder)
Create a file named **`.env`** in the main `Denatl-ERP/` root directory:
```env
# 1. Database Connection (Choose LOCAL SQLite or CLOUD Supabase Postgres)
# Local SQLite Address:
DATABASE_URL=sqlite:///./dental_tracker.db
# Cloud Supabase Address (IPv4 Pooler Optimized):
# DATABASE_URL=postgresql://postgres:[password]@db.qerqlnhutwztvhcfwfmi.supabase.co:6543/postgres?sslmode=require

# 2. Google Gemini Serverless AI API Key (Get yours for free at aistudio.google.com)
GEMINI_API_KEY=AIzaSy...

# 3. Local Offline Ollama Fallback Settings
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_MODEL=qwen2.5:1.5b
OLLAMA_API_PATH=/v1/chat/completions
OLLAMA_TIMEOUT_SECONDS=120
OLLAMA_MAX_RETRIES=2
```

### B. Frontend SPA Configurations (`frontend/.env`)
Create a file named **`.env`** inside the `frontend/` directory:
```env
# Point to your local FastAPI server (or your Render/Railway hosted server url)
VITE_API_BASE_URL=http://localhost:8000
```

---

## 5. Local Setup & Execution Guide

Follow these simple steps to run the complete medical portal locally on your Windows computer:

### Step 1: Clone & Initialize Dependencies
```powershell
# Navigate into the project folder
cd C:\Users\Genadi\Documents\Programing\Projects\Denatl-ERP

# Activate the virtual environment
.venv\Scripts\Activate.ps1

# Install required python packages
.venv\Scripts\pip install -r requirements.txt
```

### Step 2: Launch the Backend API Server
```powershell
.venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
* The API documentation will be active at **`http://localhost:8000/docs`**.

### Step 3: Run the Local Web Scraper Sync
To populate your newly created `dental_tracker.db` SQLite database file with initial products and live pricing:
```powershell
.venv\Scripts\python -c "from app.services.scraper_service import run_dental_scraper_task; run_dental_scraper_task()"
```

### Step 4: Run the Local Offline Ollama Model
Ensure you have Ollama installed and the model downloaded:
```powershell
# Pull the optimized Qwen 2.5 1.5B model locally (takes only 900MB)
ollama pull qwen2.5:1.5b
```

### Step 5: Launch the React Frontend
Open a second terminal, navigate to the `frontend/` folder, and start Vite:
```powershell
cd frontend
npm run dev
```
* Open **`http://localhost:5173`** in your browser.
* Use the secure staff password **`radevdent2026`** to enter the administrative portal.

---

## 6. Cloud Deployment Instructions

### A. Deploy Frontend to Vercel (100% Free)
Our frontend is configured with HashRouter, making Vercel deployments instantaneous and error-free:
```powershell
cd frontend
npx vercel --prod --yes
```

### B. Deploy Backend to Render (100% Free via Docker)
Our repository contains a pre-configured **`Dockerfile`** that installs all linux system dependencies and Playwright Chromium browsers automatically.
1. Sign up at **[render.com](https://render.com)**.
2. Select **New -> Web Service** and link your GitHub repository.
3. Select **Language: `Docker`**.
4. In the **Environment Variables (Advanced)** settings, add:
   * `DATABASE_URL` = Your Supabase Postgres pooler connection string.
   * `GEMINI_API_KEY` = Your Google Gemini key starting with `AIzaSy`.
5. Deploy! Render will build the container and provide a live URL (e.g. `https://your-app.onrender.com`).
6. Update `VITE_API_BASE_URL` in `frontend/.env` to this new Render URL, recompile with `npm run build`, and redeploy to Vercel!
