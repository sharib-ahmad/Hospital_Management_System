# Task Tracker - Background Jobs, Emailing, and Core Integrations

## 1. Database & Models
- [x] Create `Invoice` model in `backend/app/models/invoice.py`
- [x] Create `LabReport` model in `backend/app/models/lab_report.py`
- [x] Create `Notification` model in `backend/app/models/notification.py`
- [x] Register new models in `backend/app/models/__init__.py`

## 2. Configuration & Email Subsystem
- [x] Update `backend/app/celeryConfig.py` with timezone 'Asia/Kolkata' and import paths
- [x] Implement `Mailer` utility in `backend/app/utils/mailer.py`
- [x] Create HTML Jinja2 email templates in `backend/app/templates/emails/`
  - [x] `order_status.html`
  - [x] `patient_approval.html`
  - [x] `appointment_scheduled.html`
  - [x] `doctor_daily_agenda.html`
  - [x] `nurse_daily_agenda.html`
  - [x] `vitals_export.html`

## 3. Background Celery Tasks
- [x] Implement Celery email tasks in `backend/app/tasks/email_tasks.py`
- [x] Implement Celery cleanup tasks in `backend/app/tasks/cleanup_tasks.py`

## 4. Services & API Routes
- [x] Add `generate_vitals_csv_string` in `backend/app/services/patient_vitals.py`
- [x] Add export endpoints to `backend/app/routes/patient_vitals.py` and controller
- [x] Implement Prescription parser service and route
- [x] Implement Invoices service, controller, and routes (with payment simulator)
- [x] Implement Lab Reports service, controller, and upload/download routes
- [x] Implement Notification feeds routes and Mark as Read triggers
- [x] Add Invoice creation and Notification triggers inside:
  - [x] `PharmacyService` (order billing)
  - [x] `AppointmentService` (consultation billing)
  - [x] `PatientVitalsService` (nurse check alerts)
  - [x] `ApplicationService` (approval notifications)

## 5. Frontend Portal Upgrades
- [ ] Implement Notification Bell component in Dashboard layout header
- [ ] Integrate Vitals Export options (Download / Email) in `UserPortal.vue`
- [ ] Add **Billing & Invoices** tab with simulation pay & receipts inside `UserPortal.vue`
- [ ] Add **Order Prescribed Medicines** button and modal inside `UserPortal.vue`
- [ ] Add **Lab & Clinical Reports** file drop-zone inside `PatientVitalsDetailView.vue`
- [ ] Add interactive Chart.js dashboards inside Doctor & Admin portals

## 6. Verification
- [ ] Verify MailHog captures all trigger templates
- [ ] E2E check of billing, prescription parsing, report uploads, notifications, and analytics
- [ ] Run type check (`npm run type-check`) and format code (`npm run format`)
