# Task Tracker - Clinical Vitals & Doctor Referral Workflow

## 1. Database & Backend Models
- [x] Add `vitals_checked` and `appointment_type` to `Appointment` model
- [x] Make `doctor_id` nullable in `Appointment` model
- [x] Run migration queries on local PostgreSQL database

## 2. Backend Services & Routes
- [x] Update `AppointmentService` to support `'vitals_check'` booking (no doctor required)
- [x] Update `AppointmentModels` in `flask-restx` to reflect nullable `doctor_id` and new types
- [x] Update `PatientVitalsService` to handle `appointment_id` and `refer_to_department_id`
- [x] Implement doctor auto-referral allocation logic when department referral is requested

## 3. Frontend Development
- [x] **User Portal**: Allow booking "Vitals Checkup Only" and submit `appointment_type='vitals_check'`
- [x] **Nurse Portal**:
  - [x] Add "Vitals Checkup Requests" list with Approval/Rejection actions
  - [x] Add prioritized queue of active appointments "Awaiting Vitals Check"
  - [x] Add "Refer to Doctor" toggle and Department selector to the "Record Vitals" form
- [x] **Doctor Portal**:
  - [x] Add visual warning badges for "Awaiting Vitals Check"
  - [x] Block consultation completion unless `vitals_checked` is true
  - [x] Display recorded vital signs parameters inside the doctor's consultation modal

## 4. Verification & Clean-up
- [x] Run type-checking (`npm run type-check`) to verify compilation
- [x] Run format check (`npm run format`) using oxfmt
- [ ] Perform E2E manual flow test verification
