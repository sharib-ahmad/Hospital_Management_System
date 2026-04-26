# Gemini CLI Project Mandates - Hospital Management System

## Project Overview
A comprehensive Hospital Management System (HMS) designed to replace manual registers and disconnected software. The system facilitates efficient management of patients, doctors, appointments, and treatments, ensuring data integrity and preventing scheduling conflicts.

### User Roles
- **Admins:** Manage system users (Doctors, Patients, Staff), departments, and overall hospital configuration.
- **Doctors:** Manage patient consultations, view medical history, and manage their own schedules.
- **Patients:** Book appointments, view their medical records, and track treatment progress.
- **Staff (Receptionist/Nurse):** Handle registration, billing, and preliminary patient vitals.

## Tech Stack
- **Backend:** Python (Flask), Managed via **uv**.
- **API:** Flask-RestX (Swagger/OpenAPI Documentation).
- **Database:** Flask-SQLAlchemy (ORM).
- **Validation:** Pydantic (Data schemas).
- **Frontend:** Vue 3 (Composition API), Pinia (State Management), Tailwind CSS 4, Vite, Axios.

## Infrastructure Requirements
- **Redis:** A running Redis server is required for Celery background tasks (default: `redis://localhost:6379/0`).

## Logging
- **Application Logs:** All logs (INFO and ERROR) from the Flask application are captured in the `output.txt` file in the project root.

## Coding Standards & Conventions

### Backend (Python/uv)
- **Tooling:** Always use `uv` for dependency management (`uv add`), running the app (`uv run`), and script execution.
- **API Design:** Use `flask-restx` namespaces. Every endpoint MUST be documented with models for Swagger.
- **Validation:** Use Pydantic schemas for request validation.
- **Naming:** PEP 8 compliance.

### Frontend (Vue/TypeScript)
- **Components:** `<script setup>` with TypeScript.
- **Styling:** Tailwind CSS 4 (Utility-first).
- **State:** Pinia for global/shared state.
- **Formatting:** Use `oxfmt` for formatting (defined in `package.json`).
- **Theming:** Every frontend page MUST support Light, Dark, and System Default themes using Tailwind CSS dark mode (class or media). A global theme switcher should be available.


## Operational Mandates
- **Environment:**
  - Start Backend: `uv run python run.py`
  - Start Celery Worker: `uv run celery -A worker.celery worker --loglevel=info`
- **Security:** Strict Role-Based Access Control (RBAC). Ensure PHI (Protected Health Information) is only accessible to authorized roles.
- **Testing:** New features must include tests (Pytest for backend, Vitest for frontend).
