# 🏥 Hospital Management System (HMS)

## 📌 Overview

A comprehensive, **modern full-stack Hospital Management System** designed to replace manual registers with an efficient, API-first digital solution. The system facilitates seamless coordination between patients, doctors, and administrative staff, ensuring data integrity and real-time scheduling.

> 🚀 **Status:** Active Development (Core features implemented)

---

## 🧱 Tech Stack

### 🔹 Backend (API-First)
* **Framework:** Python (Flask)
* **API Engine:** Flask-RESTX (Swagger/OpenAPI Documentation)
* **Database/ORM:** Flask-SQLAlchemy (PostgreSQL compatible)
* **Validation:** Pydantic & Marshmallow
* **Environment:** Managed via **uv** (high-performance Python packager)
* **Async Tasks:** Celery + Redis (Background processing)

### 🔹 Frontend (Premium UI)
* **Framework:** Vue 3 (Composition API + TypeScript)
* **State Management:** Pinia
* **Styling:** Tailwind CSS 4 (Utility-first, Glassmorphism, Dark Mode)
* **Build Tool:** Vite
* **Formatting:** `oxfmt`

---

## 📂 Project Structure

```text
├── backend/                # Flask API Root
│   ├── app/
│   │   ├── api_models/    # Swagger/RESTX models
│   │   ├── controllers/   # Business logic orchestration
│   │   ├── models/        # SQLAlchemy Database models
│   │   ├── routes/        # API Endpoints
│   │   ├── services/      # Core business logic
│   │   └── tasks/         # Celery background jobs
│   └── manage.sh           # Backend utility scripts
└── frontend/               # Vue 3 SPA Root
    ├── src/
    │   ├── components/    # Reusable UI elements
    │   ├── layouts/       # Dashboard & Auth layouts
    │   ├── stores/        # Pinia state (Auth, Notifications)
    │   └── views/         # Page components (Portals, Management)
```

---

## 🎯 Key Features Implemented

* 🔐 **Robust Authentication:** JWT-based secure auth with role-based access control (RBAC).
* 👨‍⚕️ **Doctor Portal:** Specialized dashboard for appointment management and schedule tracking.
* 🧑‍🤝‍🧑 **Patient Management:** Profile creation, clinical history, and application tracking.
* 📋 **Role Application System:** Multi-step onboarding for Doctors, Nurses, and Patients with administrative review.
* 📊 **Admin Dashboard:** Comprehensive statistics, user management, and department configuration.
* 🌓 **Dynamic Theming:** Support for Light, Dark, and System modes with a premium emerald design language.
* 📱 **Fully Responsive:** Mobile-first design ensuring usability across all device sizes.

---

## 🚀 Getting Started

### Prerequisites
* Python 3.12+ (managed via `uv`)
* Node.js & npm/pnpm
* Redis (for background tasks)

### Backend Setup
```bash
cd backend
uv sync
uv run python run.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## ⚙️ Development Status

* [x] Project architecture & RBAC
* [x] Database Schema & ORM
* [x] JWT Authentication & Secure Cookies
* [x] Advanced Application Management (Filters, Stats)
* [x] Doctor Appointment Portal
* [x] Responsive Dashboard UI
* [ ] Advanced Medical Records (In Progress)
* [ ] Billing & Invoicing (Planned)
* [ ] Real-time Notifications (Planned)

---

## 📄 License

This project is built for educational and portfolio purposes, showcasing modern software engineering practices.
