# 🏥 Hospital Management System (HMS)

## 📌 Overview

A full-stack Hospital Management System (HMS) designed to replace manual registers with an API-first digital solution. The system facilitates coordination between patients, doctors, nurses, and administrative staff, ensuring data integrity, patient vital tracking, clinical history logs, and schedule management.

> 🚀 **Status:** Core features fully implemented. Production ready.

---

## 🧱 Tech Stack

### 🔹 Backend (API-First)
* **Framework:** Python (Flask)
* **API Engine:** Flask-RESTX (Swagger/OpenAPI Documentation)
* **Database/ORM:** Flask-SQLAlchemy (PostgreSQL compatible)
* **Validation:** Pydantic (Data schemas)
* **Environment:** Managed via **uv** (high-performance Python packaging and runtime tool)
* **Caching:** Flask-Caching with Redis integration
* **Async Tasks:** Celery + Redis (Background processing)

### 🔹 Frontend (Modern UI)
* **Framework:** Vue 3 (Composition API + TypeScript)
* **State Management:** Pinia
* **Styling:** Tailwind CSS 4 (Utility-first, dark mode toggles, adaptive layouts)
* **Build Tool:** Vite
* **Formatting:** `oxfmt`

---

## 📂 Project Structure

```text
├── backend/                # Flask API Root
│   ├── app/
│   │   ├── api_models/    # Swagger/RESTX validation models
│   │   ├── controllers/   # Route handler orchestration
│   │   ├── models/        # SQLAlchemy Database models
│   │   ├── routes/        # API Namespace controllers
│   │   ├── services/      # Business logic implementation
│   │   └── tasks/         # Celery background jobs
│   └── manage.sh           # Operations control script
└── frontend/               # Vue 3 SPA Root
    ├── src/
    │   ├── components/    # Reusable form inputs and layouts
    │   ├── layouts/       # Dashboard and authentication frames
    │   ├── stores/        # Pinia state stores (auth, alerts)
    │   └── views/         # Role-specific portals and views
```

---

## 🎯 Key Features Implemented

* 🔐 **Secure JWT Auth:** Cookie-based HTTPOnly JSON Web Token authentication with role-based access control (RBAC).
* 👨‍⚕️ **Doctor Portal:** Consultation tracking, medical history logging, profile editing, and patient appointments.
* 🩺 **Clinical Medical Records:** Database logging for diagnoses, treatment prescriptions, and private doctor notes.
* 👩‍⚕️ **Nurse Portal & Vitals Tracking:** Dedicated module for nurses to record and monitor real-time patient vitals (systolic/diastolic blood pressure, blood sugar, pulse rate, temperature, and respiration).
* 📅 **Dynamic Date-Time Picker:** Custom-built teleported calendar, time selector, and datetime-local picker with dynamic client bounding calculations that center on short viewports to prevent taskbar overflow.
* 🕒 **Timezone Alignment:** Complete system synchronization to the `Asia/Kolkata` timezone for all appointment scheduling, vitals records, and updates.
* 🔑 **Password Recovery Pipeline:** Secure recovery flow inside the authentication interface.
* 📊 **Admin Dashboard:** Central panel for statistics, user management, application approvals, and department configurations.
* 🌓 **Dynamic Themes:** Toggle support for Light, Dark, and System default modes with an emerald-themed styling.

---

## 🚀 Getting Started

### Prerequisites
* Python 3.12+ (managed via `uv`)
* Node.js & npm
* Redis Server (default: `redis://localhost:6379/0`)

### Backend Setup
```bash
cd backend
uv sync
uv run python run.py
```

### Celery Worker Setup
```bash
cd backend
uv run celery -A worker.celery worker --loglevel=info
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## ⚙️ Development Status

* [x] Project Architecture & RBAC System
* [x] Database Schema & ORM Model bindings
* [x] JWT Authentication & Cookie Security
* [x] Advanced Application Management & Onboarding
* [x] Timezone-Aligned Scheduler (Asia/Kolkata)
* [x] Clinical Medical Records & Vital logs
* [x] Nurse, Doctor, User, and Admin Portals
* [x] Viewport-Adaptive Date-Time picker
* [x] Password Reset Recovery
* [ ] Billing & Invoicing (Planned)
* [ ] Real-time Notifications (Planned)

---

## 📄 License

This project is built for educational and portfolio purposes, showcasing modern software engineering practices.
