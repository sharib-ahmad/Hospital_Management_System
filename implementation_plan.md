# Implementation Plan - Background Jobs, Emailing Services, and Core Application Integration

This plan outlines the design, configuration, and integration of the automated background jobs, clinical mailing services, database maintenance schedulers, and 5 core hospital management system features: Consolidated Billing, Prescription-to-Pharmacy integration, Lab Report file uploads, In-App Notifications, and Interactive Analytics.

---

## User Review Required

Please review and confirm the following design decisions and settings:

1. **SMTP Configuration**: Emails will be routed through the MailHog server running on `localhost:1025` using Jinja2 HTML templates.
2. **Scheduling Details**:
   - Daily Agenda email: **8:00 AM Asia/Kolkata (IST)**.
   - Schedulers run daily at **2:00 AM** and **2:30 AM Asia/Kolkata** for expired token and old application cleanups (records >30 days old).
3. **consolidated Billing**: A new `Invoice` model will record charges. Payment is simulated in-app via a "Pay Now" action, with print-ready billing receipts.
4. **Prescription Integration**: A substring-matching parser will map text prescriptions to active medistore medicines and let users auto-add items to their cart.
5. **Lab Reports Uploads**: File uploads are stored locally in the backend workspace at `backend/uploads/lab_reports/` and served via download endpoints.
6. **Notifications**: A navbar glassmorphic bell will pop up recent alerts and short-poll every 15 seconds to sync read status.
7. **Analytics**: Visualizations will utilize Chart.js in Doctor and Admin dashboards.

---

## Proposed Changes

### 1. Database Schema & Models

#### [NEW] [invoice.py](file:///wsl.localhost/Ubuntu-26.04/home/sharib/Projects/Hospital_Managemen_System/backend/app/models/invoice.py)
* Add `Invoice` model tracking charges:
  - `id`: UUID (Primary Key)
  - `patient_id`: UUID (Foreign Key to `patients.id`)
  - `user_id`: UUID (Foreign Key to `users.id`)
  - `appointment_id`: UUID (Foreign Key to `appointments.id`, nullable)
  - `order_id`: UUID (Foreign Key to `pharmacy_orders.id`, nullable)
  - `amount`: Numeric(10, 2)
  - `status`: Enum (`unpaid`, `paid`, `refunded`)
  - `invoice_type`: String (`consultation`, `pharmacy`)
  - `created_at`, `updated_at`

#### [NEW] [lab_report.py](file:///wsl.localhost/Ubuntu-26.04/home/sharib/Projects/Hospital_Managemen_System/backend/app/models/lab_report.py)
* Add `LabReport` model tracking uploads:
  - `id`: UUID (Primary Key)
  - `patient_id`: UUID (Foreign Key to `patients.id`)
  - `uploaded_by`: UUID (Foreign Key to `users.id`)
  - `file_name`: String(255)
  - `file_path`: String(500)
  - `title`: String(100)
  - `notes`: Text
  - `created_at`

#### [NEW] [notification.py](file:///wsl.localhost/Ubuntu-26.04/home/sharib/Projects/Hospital_Managemen_System/backend/app/models/notification.py)
* Add `Notification` model tracking user alerts:
  - `id`: Integer (Primary Key, Auto-increment)
  - `user_id`: UUID (Foreign Key to `users.id`)
  - `title`: String(100)
  - `message`: Text
  - `is_read`: Boolean (default=False)
  - `category`: String(50) (e.g. `appointment`, `billing`, `order`, `application`, `vitals`)
  - `created_at`

---

### 2. Configuration & Celery Beat Schedule

#### [MODIFY] [celeryConfig.py](file:///wsl.localhost/Ubuntu-26.04/home/sharib/Projects/Hospital_Managemen_System/backend/app/celeryConfig.py)
* Add imports for `app.tasks.email_tasks` and `app.tasks.cleanup_tasks`.
* Update Celery's `timezone` to `'Asia/Kolkata'`.
* Configure Beat schedules:
  - `send-daily-agenda`: daily at `crontab(hour=8, minute=0)`.
  - `cleanup-expired-tokens`: daily at `crontab(hour=2, minute=0)`.
  - `cleanup-old-applications`: daily at `crontab(hour=2, minute=30)`.

---

### 3. Backend Utilities & Mailer

#### [NEW] [mailer.py](file:///wsl.localhost/Ubuntu-26.04/home/sharib/Projects/Hospital_Managemen_System/backend/app/utils/mailer.py)
* Create `Mailer` using standard `smtplib` and `jinja2` rendering.
* Create email HTML templates under `backend/app/templates/emails/`:
  - `order_status.html`, `patient_approval.html`, `appointment_scheduled.html`, `doctor_daily_agenda.html`, `nurse_daily_agenda.html`, `vitals_export.html`.

---

### 4. Background Celery Tasks

#### [NEW] [email_tasks.py](file:///wsl.localhost/Ubuntu-26.04/home/sharib/Projects/Hospital_Managemen_System/backend/app/tasks/email_tasks.py)
* Asynchronous mailing tasks:
  1. `send_order_status_email(order_id)`: Sends status notification to patient.
  2. `send_patient_approval_email(application_id)`: Sends patient approval greetings.
  3. `send_appointment_email(appointment_id)`: Sends appointment details.
  4. `send_daily_agenda_emails()` (Beat task): Daily agendas to Doctors/Nurses.
  5. `send_vitals_csv_email(user_id, email)`: Compiles vital records CSV and emails user.

#### [NEW] [cleanup_tasks.py](file:///wsl.localhost/Ubuntu-26.04/home/sharib/Projects/Hospital_Managemen_System/backend/app/tasks/cleanup_tasks.py)
* Asynchronous maintenance tasks:
  1. `cleanup_expired_tokens()`: Purges blocklist rows > 30 days old.
  2. `cleanup_old_applications()`: Deletes APPROVED/REJECTED application records > 30 days old.

---

### 5. Services & Route Integrations

#### [NEW] Billing, Lab Reports, and Notification Endpoints
* **Invoices Route** (`GET /invoices`, `POST /invoices/<id>/pay`): Handles invoice listing and simulated payments.
* **Lab Reports Route** (`POST /lab-reports`, `GET /lab-reports/patient/<patient_id>`, `GET /lab-reports/<id>/file`): Multipart file upload handlers.
* **Notifications Route** (`GET /notifications`, `PUT /notifications/<id>/read`, `PUT /notifications/read-all`): Manages user notification feed.
* **Prescription Parser** (`GET /medical-records/<record_id>/parse-prescription`): Substring matches prescription text to active medicines catalog.
* **Vitals Export Routes** (`GET /vitals/my/export`, `POST /vitals/my/export-job`): Returns CSV directly or triggers background email.

#### [MODIFY] Service hooks
* Trigger invoices automatically:
  - In `create_order` (PharmacyService): Generate a pharmacy invoice.
  - In `create_appointment` (AppointmentService) and `update_appointment_status`: Generate a consultation invoice.
* Trigger alerts/notifications:
  - Record Vitals: Notify assigned Doctor.
  - Approve Patient Application: Notify User.
  - Update Order Status: Notify User.

---

### 6. Frontend Portal Views & Components

#### [MODIFY] [UserPortal.vue](file:///wsl.localhost/Ubuntu-26.04/home/sharib/Projects/Hospital_Managemen_System/frontend/src/views/portals/UserPortal.vue)
* Add a **Billing & Invoices** tab displaying unpaid invoices, payment trigger modals, and printable receipts.
* Add **Export Vitals** button to Patient cards with Download and Email options.
* Add **Order Prescribed Medicines** button next to Medical Records to match catalog medicines.

#### [MODIFY] [PatientVitalsDetailView.vue](file:///wsl.localhost/Ubuntu-26.04/home/sharib/Projects/Hospital_Managemen_System/frontend/src/views/PatientVitalsDetailView.vue)
* Add a **Lab & Clinical Reports** panel allowing PDF/Image drops and views.

#### [MODIFY] Navbar / Header
* Embed a glassmorphic **Notification Bell** popover showing unread feeds and click-to-read triggers.

#### [MODIFY] Doctor and Admin Portals
* Embed Chart.js graphical charts for department volume, revenue divisions, and fill trends.

---

## Verification Plan

### Automated & Manual Tests
1. **Email Delivery**: Verify MailHog inbox on `:8025` captures all trigger notification templates.
2. **Billing Fulfillments**: Fulfill simulated invoice checkout pay and verify receipt layout is print-clean.
3. **Prescription parser check**: Write test prescription, hit matching endpoint and verify selected cart loads correct item matches.
4. **Upload validation**: Upload mock lab reports, verify download link downloads exact file, and access is restricted to patient/doctor.
5. **Dashboard visual checks**: Review responsive Chart.js render shapes under dark/light themes.