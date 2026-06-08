# 🏥 Hospital Management System (HMS)

A state-of-the-art, secure, and production-grade Hospital Management System (HMS). This platform replaces manual clinical registers with an API-first digital system, facilitating seamless and real-time coordination between Patients, Doctors, Nurses, Pharmacists, and Administrative staff.

---

## 📌 Architecture Overview
The platform uses a decoupled client-server architecture:
* **Backend:** A high-performance Python (Flask) RESTful API orchestrated with **Flask-RESTX** for OpenAPI/Swagger documentation, and supported by **Celery** (with Redis) for asynchronous task scheduling and background workers.
* **Frontend:** A responsive Single Page Application (SPA) built with **Vue 3** (TypeScript + Composition API), styled using **Tailwind CSS 4**, and built on **Vite**.

---

## 🧱 Tech Stack

### 🔹 Backend
* **Core:** Python 3.12+ (managed via `uv` package manager)
* **Web & Routing:** Flask + Flask-RESTX (Swagger documentation engine)
* **Database & ORM:** Flask-SQLAlchemy (PostgreSQL / SQLite compatible)
* **Real-time Sync:** Flask-SocketIO + simple-websocket (WebSockets with HTTP Long-Polling fallback)
* **Async Processing:** Celery + Redis (Task queue & message broker)
* **Schema Validation:** Pydantic (data parsing)
* **Authentication:** PyJWT (HTTPOnly JWT authorization tokens & Blocklist tables)

### 🔹 Frontend
* **Core Framework:** Vue 3 (Composition API & Type-Safe TypeScript)
* **State Management:** Pinia
* **Build Engine:** Vite
* **Styling & Theme:** Tailwind CSS 4 (Custom design tokens, Dark/Light theme toggles)
* **Charts:** Chart.js (Visual vitals metrics tracking)
* **Linter/Formatter:** `oxfmt`

---

## 🎯 Key Features

### 1. User & Staff Management
* **Secure Auth Gateway:** Cookie-based JWT authentication using HTTPOnly cookies to prevent XSS. Includes instant session validation, token invalidation blocklists, and password recovery.
* **Role-Based Portals:** Custom portals for 5 user types:
  - **Admin Portal:** Manage departments, coordinate staff registrations, approve new doctor/nurse/pharmacist applications, check analytics, and view audit logs.
  - **Doctor Portal:** Manage patient appointments, check clinical vital trendlines, upload file-attached prescriptions, write medical records with rich text, and update consultation feedback.
  - **Nurse Portal:** Record and update real-time patient vitals (Blood Pressure, Blood Sugar, Temperature, Pulse, Respiration), and monitor patient lists.
  - **Pharmacist Portal:** Process pharmacy orders, check medicine inventories, manage order statuses, and dispatch medications.
  - **Patient Portal:** Search and purchase prescription medicines, view personal appointments, download reports, view historical vitals, and update personal profiles.

### 2. Clinical Excellence
* **Real-Time Websocket Notifications:** Instantly broadcasts in-app alerts (e.g. appointment approvals, application decisions, pharmacy dispatch updates) over `Socket.IO` connected directly to user-specific rooms.
* **HIPAA-Compliant PHI Audit Trail:** Automatic database logging of every action involving Protected Health Information (PHI) — recording the user ID, event, timestamp, client IP, and specific database change details.
* **Secure File Uploads & Downloads:** Doctors can upload prescription and lab report files (PDF/Images) directly from their portal. Files are securely served from backend storage via a JWT-authenticated custom route.
* **Vitals Trend Tracking:** Rich interactive **Chart.js** trendlines displaying multi-metric historical variations in blood pressure, pulse rate, respiration, body temperature, and blood sugar.
* **Global Command Palette:** A premium glassmorphic shortcut overlay (`Ctrl+K` / `Cmd+K`) allowing users to instantly trigger global options, switch themes, navigate portals, or log out.
* **Clinical Rich Text Editor:** Markdown formatting toolbar inside the doctor notes form, translating Markdown syntax to responsive HTML views on patient-facing layouts.
* **Viewport-Adaptive Date-Time Picker:** A calendar and time scheduler featuring dynamic client bounding box calculations to ensure it never overflows small screen viewports.

---

## 📊 Database Schema

```mermaid
erDiagram
    User ||--o| Doctor : "profile_for"
    User ||--o| Nurse : "profile_for"
    User ||--o| Pharmacist : "profile_for"
    User ||--o| Patient : "profile_for"
    User ||--o{ Appointment : "schedules/attends"
    User ||--o{ Notification : "receives"
    User ||--o{ AuditLog : "triggers"
    Department ||--o{ Doctor : "belongs_to"
    Department ||--o{ Nurse : "belongs_to"
    Patient ||--o{ Appointment : "attends"
    Patient ||--o{ PatientVital : "has_history"
    Patient ||--o{ MedicalRecord : "has_records"
    Patient ||--o{ LabReport : "has_reports"
    MedicalRecord ||--o{ Invoice : "bills"
    User ||--o{ PharmacyOrder : "orders"
    PharmacyOrder ||--o{ PharmacyOrderItem : "contains"
    Medicine ||--o{ PharmacyOrderItem : "references"

    User {
        UUID id PK
        string email
        string password_hash
        string first_name
        string last_name
        string role "admin|doctor|nurse|pharmacist|patient"
        datetime tokens_valid_after
        datetime created_at
    }

    Doctor {
        UUID id PK
        UUID user_id FK
        string department_id FK
        string specialization
        string contact_number
        string status "active|inactive"
    }

    Nurse {
        UUID id PK
        UUID user_id FK
        string department_id FK
        string contact_number
    }

    Pharmacist {
        UUID id PK
        UUID user_id FK
        string contact_number
    }

    Patient {
        UUID id PK
        UUID user_id FK
        string date_of_birth
        string gender
        string address
        string emergency_contact
    }

    PatientVital {
        UUID id PK
        UUID patient_id FK
        UUID recorded_by FK
        float systolic_bp
        float diastolic_bp
        float pulse
        float temperature
        float respiration
        float blood_sugar
        datetime recorded_at
    }

    MedicalRecord {
        UUID id PK
        UUID patient_id FK
        UUID doctor_id FK
        string diagnosis
        string notes "Markdown text"
        string file_name
        string file_path
        datetime created_at
    }

    PharmacyOrder {
        UUID id PK
        UUID user_id FK
        string status "pending|processing|dispatched|cancelled"
        float total_amount
        datetime created_at
    }

    AuditLog {
        UUID id PK
        UUID user_id FK
        string action
        string ip_address
        string details "JSON payload"
        datetime timestamp
    }
```

---

## ⚙️ Development Workflows

### 1. Onboarding Approval Loop
1. A guest registers an account.
2. They apply to join the staff as a **Doctor**, **Nurse**, or **Pharmacist** by filling out credentials and department details.
3. The application triggers an instant Socket.IO broadcast alerting Administrators.
4. The **Administrator** logs into the Admin portal, reviews the application details, and approves it.
5. The applicant's role changes to their respective staff role, generating their profile in the database, and sending them an in-app alert.

### 2. Clinical Visit Flow
1. **Nurse Log:** A patient visits the hospital. The Nurse updates the patient's vitals (blood pressure, sugar levels, etc.) in the Nurse Portal.
2. **Doctor Analysis:** The Doctor logs in, reviews the dynamic vital trendlines (Chart.js), diagnoses the patient, types prescriptions using the Markdown rich text editor, and attaches clinical scan PDFs.
3. **Audit Event:** Behind the scenes, the `AuditService` logs a HIPAA event indicating the Doctor accessed the patient's PHI history.
4. **Patient Review:** The Patient logs in, reads their medical notes, and downloads the prescription PDF.

---

## 🚀 Getting Started

### Prerequisites
* **Python 3.12+** (managed via high-performance `uv`)
* **Node.js v20+** & **npm**
* **Redis Server** (listening on `redis://localhost:6379/0`)
* **PostgreSQL** (running on `localhost:5432` with a database matching your `.env` connection URL)

---

### Installation & Run Steps

#### Step 1: Environment Configuration
Create a `.env` file under the `/backend` folder:
```ini
FLASK_APP=run.py
FLASK_ENV=development

ADMIN_EMAIL=adminsharibahmad@gmail.com
ADMIN_PASSWORD=yourpasswordhere

JWT_SECRET_KEY=yoursupersecurejwtkey
DATABASE_URL=postgresql://username:password@localhost:5432/hospital_management_system

SMTP_SERVER_HOST=localhost
SMTP_SERVER_PORT=1025
SMTP_USERNAME=HPS
SENDER_PASSWORD=HPS@321
SENDER_ADDRESS=hospital_management@donotreply.in
```

#### Step 2: Backend Setup
Open terminal in the `/backend` folder and run:
```bash
# Sync dependencies
uv sync

# Run database migrations
uv run python event_and_nullable_migration.py

# Start the Flask + Socket.IO server
uv run python run.py
```
*The API server will run at `http://localhost:5000` with interactive Swagger docs visible at `http://localhost:5000/`.*

#### Step 3: Run Celery Worker & Beat (Optional/Async tasks)
Ensure Redis is running, then start the worker and schedule scheduler inside `/backend`:
```bash
# Start background worker
uv run celery -A worker.celery worker --loglevel=info

# Start Celery Beat (cron jobs scheduler)
uv run celery -A worker.celery beat --loglevel=info
```

#### Step 4: Frontend Setup
Open terminal in the `/frontend` folder and run:
```bash
# Install packages
npm install

# Start development server
npm run dev
```
*The Vue application will launch at `http://localhost:5173`.*

---

## 🧪 Verification & Linting

### Verify Backend Compilation
Check that all Python files are syntax-free and ready for execution:
```bash
cd backend
python -m compileall app
```

### Verify Frontend Type-Safety
Run the TypeScript compiler to ensure the front-end codebase compiles without errors:
```bash
cd frontend
npm run type-check
```

---

## 🔮 Future Implementation roadmap
* **Multi-Factor Authentication (MFA):** Add TOTP-based 2FA support using authenticator apps (Google Authenticator/Authy) for clinical staff.
* **Email & SMS Alerts:** Connect Celery background worker tasks to real SMTP/Twilio channels to dispatch vital alerts, booking updates, and invoice PDFs directly to users' phones and inboxes.
* **Advanced Bed & Ward Management:** Add an interactive clinical ward grid to allocate physical hospital beds to patients upon admission.
* **Resource-Level Access Policies (ABAC):** Transition from role-based boundaries to Attribute-Based Access Control to prevent clinicians from editing records outside their department.
