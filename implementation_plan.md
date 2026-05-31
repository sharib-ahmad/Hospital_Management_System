# Implementation Plan - Clinical Vitals & Doctor Referral Workflow

This plan outlines the design and integration of a clinical vitals validation pipeline. It ensures patient vitals are recorded before consultations and provides a structured "Vitals Only Checkup" request flow for registered patients, complete with nurse approval and department-based doctor referrals.

---

## Proposed Changes

### 1. Database Schema & Models

#### [MODIFY] [appointment.py](file:///wsl.localhost/Ubuntu-26.04/home/sharib/Projects/Hospital_Managemen_System/backend/app/models/appointment.py)
* Make `doctor_id` nullable (`nullable=True`) to support standalone vitals checkup bookings that do not have an assigned doctor.
* Add `vitals_checked` column (`db.Boolean`, default=`False`) to track whether a patient's vitals have been captured for this specific appointment.
* Add `appointment_type` column (`db.String(30)`, default=`'consultation'`) to distinguish between `'consultation'` (Doctor consultation) and `'vitals_check'` (Nurse vitals screening) appointments.

---

### 2. Backend Service Layer & REST Endpoints

#### [MODIFY] [appointment_models.py](file:///wsl.localhost/Ubuntu-26.04/home/sharib/Projects/Hospital_Managemen_System/backend/app/api_models/appointment_models.py)
* Update Swagger input models to accept `appointment_type` and make `doctor_id` optional when `appointment_type` is set to `'vitals_check'`.
* Expose `vitals_checked` and `appointment_type` in the appointment response schemas.

#### [MODIFY] [appointment.py (Service)](file:///wsl.localhost/Ubuntu-26.04/home/sharib/Projects/Hospital_Managemen_System/backend/app/services/appointment.py)
* **Create Appointment**: Allow creation of `'vitals_check'` appointments without requiring a `doctor_id`. Automatically set `vitals_checked` to `False`.
* **Database Migration Hook**: We will execute a direct migration query against the local PostgreSQL instance to safely add the required columns without data loss:
  ```sql
  ALTER TABLE appointments ALTER COLUMN doctor_id DROP NOT NULL;
  ALTER TABLE appointments ADD COLUMN IF NOT EXISTS vitals_checked BOOLEAN DEFAULT FALSE;
  ALTER TABLE appointments ADD COLUMN IF NOT EXISTS appointment_type VARCHAR(30) DEFAULT 'consultation';
  ```

#### [MODIFY] [patient_vital_models.py](file:///wsl.localhost/Ubuntu-26.04/home/sharib/Projects/Hospital_Managemen_System/backend/app/api_models/patient_vital_models.py)
* Add optional input fields `appointment_id` (UUID) and `refer_to_department_id` (UUID) to the `vital_create` expectation model.

#### [MODIFY] [patient_vitals.py (Service)](file:///wsl.localhost/Ubuntu-26.04/home/sharib/Projects/Hospital_Managemen_System/backend/app/services/patient_vitals.py)
* **Link Vitals to Appointments**: When a nurse records vitals:
  * If `appointment_id` is provided, automatically set `vitals_checked = True` on that appointment.
  * If the recorded vitals are for a standalone `'vitals_check'` appointment, mark that appointment's status as `COMPLETED`.
* **Automated Doctor Referral Logic**:
  * If the nurse specifies `refer_to_department_id` (indicating the patient verbally agreed to see a doctor after their vitals check):
    1. Search for an active, available doctor assigned to the selected department.
    2. Automatically book a new `'consultation'` appointment for the patient with the selected doctor.
    3. Pre-mark the new appointment as `vitals_checked = True` and set its status to `CONFIRMED` since the vitals observation was *just* completed.

---

### 3. Frontend Portal Modules

#### [MODIFY] [UserAppointments.vue](file:///wsl.localhost/Ubuntu-26.04/home/sharib/Projects/Hospital_Managemen_System/frontend/src/views/user/UserAppointments.vue) & [UserPortal.vue](file:///wsl.localhost/Ubuntu-26.04/home/sharib/Projects/Hospital_Managemen_System/frontend/src/views/portals/UserPortal.vue)
* **Checkup Type Toggle**: Add a "Checkup Type" radio button/segmented selector in the Appointment Booking Modal:
  * **Doctor Consultation**: Standard flow (requires selecting a doctor).
  * **Vitals Checkup Only**: stand-alone screening (hides the doctor selector).
* **Booking Integration**: Send `appointment_type: 'vitals_check'` and omit `doctor_id` when booking a vitals checkup.

#### [MODIFY] [NursePortal.vue](file:///wsl.localhost/Ubuntu-26.04/home/sharib/Projects/Hospital_Managemen_System/frontend/src/views/portals/NursePortal.vue)
* **Checkup Approval Section**: Add a tab/list for nurses to view, approve, or reject pending `vitals_check` appointments.
* **Awaiting Vitals Queue**: Display a prioritized queue of active appointments (both consultations and vitals checkups) that are currently "Awaiting Vitals Check".
* **Referral Form UI**:
  * In the **Record Vitals** tab, add a **"Refer to Doctor"** toggle section.
  * If enabled, load a dropdown list of available clinical departments.
  * Submitting the vitals payload sends the `refer_to_department_id` and `appointment_id` back to the API.

#### [MODIFY] [DoctorPortal.vue](file:///wsl.localhost/Ubuntu-26.04/home/sharib/Projects/Hospital_Managemen_System/frontend/src/views/portals/DoctorPortal.vue) & [DoctorAppointments.vue](file:///wsl.localhost/Ubuntu-26.04/home/sharib/Projects/Hospital_Managemen_System/frontend/src/views/portals/DoctorAppointments.vue)
* **Consultation Readiness Badge**: Display an amber warning badge `"Awaiting Vitals"` on appointments where `vitals_checked` is `False`, and a green `"Ready for Consultation"` badge when `True`.
* **Guard Rails**: Disable the "Complete Consultation" / "Add Medical Record" buttons for patients whose vitals have not yet been recorded.
* **Vitals Display**: Embed the latest recorded patient vitals metrics directly inside the doctor's consultation panel so they are instantly visible during the clinical evaluation.

---

## Verification Plan

### Automated & Manual Testing
1. **Database Migration**: Run the PostgreSQL query and confirm the database table updates successfully with correct defaults.
2. **Vitals Only Booking**: Log in as a patient, book a "Vitals Checkup Only", and confirm it appears in the nurse's approval queue without a doctor assignment.
3. **Approval & Vital Entry**: Log in as a nurse, approve the vitals checkup, and record the patient's vitals.
4. **Offline Doctor Referral**: Test the "Refer to Doctor" toggle on vital entry. Confirm that a new doctor consultation is automatically booked and set as `Ready` (vitals pre-checked).
5. **Doctor Block/Unblock**: Verify that a doctor cannot consult a patient until the nurse has recorded vitals, and that vitals parameters are displayed on the doctor's screen.
