from ..extensions import db
from ..models.appointment import Appointment
from ..models.doctor import Doctor
from ..models.patient import Patient
from ..utils.enum import UserRole, AppointmentStatus, Relationship
from ..utils.response import handle_response
from flask_jwt_extended import current_user
from datetime import datetime, timezone

class AppointmentService:
    
    @staticmethod
    def get_appointments():
        user_role = current_user.role
        
        if user_role == UserRole.ADMIN:
            appointments = Appointment.query.all()
        elif user_role == UserRole.DOCTOR:
            appointments = Appointment.query.filter_by(doctor_id=current_user.id).all()
        elif user_role == UserRole.USER:
            # Query appointments for all patient sub-profiles belonging to this user
            patients = Patient.query.filter_by(user_id=current_user.id).all()
            patient_ids = [p.id for p in patients]
            if patient_ids:
                appointments = Appointment.query.filter(Appointment.patient_id.in_(patient_ids)).all()
            else:
                appointments = []
        elif user_role == UserRole.NURSE:
            appointments = Appointment.query.all()
        else:
            return handle_response(success=False, message="Unauthorized", status_code=403)
            
        return handle_response(success=True, data=appointments, message="Appointments retrieved successfully")

    @staticmethod
    def create_appointment(validated_data):
        user_role = current_user.role
        patient_id = validated_data.get('patient_id')
        
        if user_role == UserRole.USER:
            # If patient_id is not provided, resolve to a matching subprofile or the first patient subprofile
            if not patient_id:
                patient = Patient.query.filter_by(user_id=current_user.id, relation=Relationship.SELF).first()
                if not patient:
                    patient = Patient.query.filter_by(user_id=current_user.id).first()
                if not patient:
                    return handle_response(success=False, message="No patient profile found. Please register a patient first.", status_code=400)
                patient_id = patient.id
            else:
                # Verify that the patient profile belongs to the current user
                patient = Patient.query.filter_by(id=patient_id, user_id=current_user.id).first()
                if not patient:
                    return handle_response(success=False, message="Unauthorized access to this patient profile", status_code=403)
            
            status = AppointmentStatus.PENDING

        elif user_role == UserRole.DOCTOR:
            if not patient_id:
                return handle_response(success=False, message="Patient ID is required for doctor-scheduled appointments", status_code=400)
                
            # Verify that the patient is assigned to this doctor
            patient = Patient.query.filter_by(id=patient_id, assigned_doctor_id=current_user.id).first()
            if not patient:
                return handle_response(success=False, message="Patient is not assigned to you", status_code=403)
                
            # Set doctor_id automatically to current doctor's user ID
            validated_data['doctor_id'] = current_user.id
            status = AppointmentStatus.CONFIRMED

        else:
            return handle_response(success=False, message="Only patients or doctors can book appointments", status_code=403)
            
        appointment_type = validated_data.get('appointment_type', 'consultation')
        doctor_id = validated_data.get('doctor_id')
        
        if appointment_type == 'consultation':
            if not doctor_id:
                return handle_response(success=False, message="Doctor ID is required for consultations", status_code=400)
            doctor = Doctor.query.get(doctor_id)
            if not doctor:
                return handle_response(success=False, message="Doctor not found", status_code=404)
        else:
            # Standalone vitals checkup - no doctor selected
            doctor_id = None

        # Ensure appointment_date is parsed as a timezone-naive datetime in Asia/Kolkata for storage
        date_val = validated_data['appointment_date']
        if isinstance(date_val, str):
            if date_val.endswith('Z'):
                date_val = date_val.replace('Z', '+00:00')
            try:
                parsed_date = datetime.fromisoformat(date_val)
            except ValueError:
                try:
                    parsed_date = datetime.strptime(date_val, "%Y-%m-%dT%H:%M:%S.%fZ")
                except ValueError:
                    parsed_date = datetime.strptime(date_val, "%Y-%m-%dT%H:%M:%S")
        else:
            parsed_date = date_val

        if parsed_date.tzinfo is not None:
            from zoneinfo import ZoneInfo
            kolkata_tz = ZoneInfo("Asia/Kolkata")
            parsed_date = parsed_date.astimezone(kolkata_tz).replace(tzinfo=None)

        # Validate that the selected date and slot are available
        target_date_str = parsed_date.strftime("%Y-%m-%d")
        slot_time_str = parsed_date.strftime("%H:%M")

        slots_resp_data, slots_status = AppointmentService.get_available_slots(target_date_str, appointment_type, doctor_id)
        if slots_status != 200:
            return slots_resp_data, slots_status
        
        available_slots = slots_resp_data.get('data', [])
        if slot_time_str not in available_slots:
            return handle_response(
                success=False, 
                message=f"The selected slot {slot_time_str} is not available on {target_date_str}", 
                status_code=400
            )

        appointment = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_date=parsed_date,
            reason=validated_data.get('reason', 'Scheduled Consultation' if appointment_type == 'consultation' else 'Vitals Checkup Only'),
            status=status,
            appointment_type=appointment_type,
            vitals_checked=False
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        return handle_response(success=True, data=appointment, message="Appointment booked successfully", status_code=201)

    @staticmethod
    def update_appointment_status(appointment_id, validated_data):
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return handle_response(success=False, message="Appointment not found", status_code=404)
            
        # Resolve status string to Enum if present
        if 'status' in validated_data and validated_data['status'] is not None:
            status_val = validated_data['status']
            if isinstance(status_val, str):
                matched_status = None
                for s in AppointmentStatus:
                    if s.value == status_val or s.name == status_val.upper():
                        matched_status = s
                        break
                if matched_status:
                    validated_data['status'] = matched_status
                else:
                    return handle_response(success=False, message=f"Invalid appointment status: {status_val}", status_code=400)

        # Permission check
        if current_user.role == UserRole.DOCTOR and appointment.doctor_id != current_user.id:
            return handle_response(success=False, message="Unauthorized to update this appointment", status_code=403)
            
        if current_user.role == UserRole.USER:
            # Verify the patient profile belongs to the current user
            patient = Patient.query.filter_by(id=appointment.patient_id, user_id=current_user.id).first()
            if not patient:
                return handle_response(success=False, message="Unauthorized to update this appointment", status_code=403)
            # Users can only cancel appointments
            if validated_data.get('status') != AppointmentStatus.CANCELLED:
                 return handle_response(success=False, message="Patients can only cancel appointments", status_code=403)

        if 'status' in validated_data:
            appointment.status = validated_data['status']
        if 'reason' in validated_data:
            appointment.reason = validated_data['reason']
            
        db.session.commit()
        return handle_response(success=True, data=appointment, message="Appointment updated successfully")

    @staticmethod
    def get_appointment_by_id(appointment_id):
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return handle_response(success=False, message="Appointment not found", status_code=404)
            
        # Permission check
        if current_user.role == UserRole.DOCTOR and appointment.doctor_id != current_user.id:
            return handle_response(success=False, message="Unauthorized", status_code=403)
            
        if current_user.role == UserRole.USER:
            patient = Patient.query.filter_by(id=appointment.patient_id, user_id=current_user.id).first()
            if not patient:
                return handle_response(success=False, message="Unauthorized", status_code=403)
            
        return handle_response(success=True, data=appointment, message="Appointment retrieved successfully")

    @staticmethod
    def get_available_slots(date_str, appt_type, doctor_id=None):
        if not date_str or not appt_type:
            return handle_response(success=False, message="Date and appointment_type are required", status_code=400)

        from datetime import datetime
        from zoneinfo import ZoneInfo
        import datetime as dt_module

        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return handle_response(success=False, message="Invalid date format. Use YYYY-MM-DD", status_code=400)

        kolkata_tz = ZoneInfo("Asia/Kolkata")
        now_local = datetime.now(kolkata_tz)
        current_date_local = now_local.date()
        current_time_local = now_local.time()

        # Reject past dates
        if target_date < current_date_local:
            return handle_response(success=True, message="Date is in the past", data=[])

        day_of_week = target_date.strftime("%A")

        def generate_slots(start_str, end_str):
            slots = []
            try:
                start_t = datetime.strptime(start_str, "%H:%M")
                end_t = datetime.strptime(end_str, "%H:%M")
                curr = start_t
                while curr + dt_module.timedelta(minutes=30) <= end_t:
                    slot_str = curr.strftime("%H:%M")
                    # If target date is today, filter out slots in the past
                    if target_date == current_date_local:
                        slot_time = curr.time()
                        if slot_time <= current_time_local:
                            curr += dt_module.timedelta(minutes=30)
                            continue
                    slots.append(slot_str)
                    curr += dt_module.timedelta(minutes=30)
            except ValueError:
                pass
            return slots

        if appt_type == 'consultation':
            if not doctor_id:
                return handle_response(success=False, message="Doctor ID is required for consultations", status_code=400)
            from ..models.doctor import Doctor
            doctor = Doctor.query.get(doctor_id)
            if not doctor:
                return handle_response(success=False, message="Doctor not found", status_code=404)

            availability = doctor.availability or {}
            day_intervals = availability.get(day_of_week, [])
            
            all_slots = []
            for interval in day_intervals:
                start = interval.get('start')
                end = interval.get('end')
                if start and end:
                    all_slots.extend(generate_slots(start, end))

            # Query existing appointments for this doctor on that specific date
            from ..models.appointment import Appointment
            from ..utils.enum import AppointmentStatus
            
            booked_appts = Appointment.query.filter(
                Appointment.doctor_id == doctor_id,
                db.func.date(Appointment.appointment_date) == target_date,
                Appointment.status != AppointmentStatus.CANCELLED
            ).all()

            booked_times = {appt.appointment_date.strftime("%H:%M") for appt in booked_appts}
            available_slots = [slot for slot in all_slots if slot not in booked_times]
            return handle_response(success=True, message="Slots retrieved successfully", data=available_slots)

        elif appt_type == 'vitals_check':
            from ..models.nurse import Nurse
            nurses = Nurse.query.filter_by(is_available=True).all()
            
            slots_capacity = {}
            for nurse in nurses:
                availability = nurse.availability or {}
                day_intervals = availability.get(day_of_week, [])
                nurse_slots = []
                for interval in day_intervals:
                    start = interval.get('start')
                    end = interval.get('end')
                    if start and end:
                        nurse_slots.extend(generate_slots(start, end))
                nurse_slots = list(set(nurse_slots))
                for slot in nurse_slots:
                    slots_capacity[slot] = slots_capacity.get(slot, 0) + 1

            # Query existing vitals_check appointments on target_date
            from ..models.appointment import Appointment
            from ..utils.enum import AppointmentStatus
            
            booked_appts = Appointment.query.filter(
                Appointment.appointment_type == 'vitals_check',
                db.func.date(Appointment.appointment_date) == target_date,
                Appointment.status != AppointmentStatus.CANCELLED
            ).all()

            booked_counts = {}
            for appt in booked_appts:
                time_str = appt.appointment_date.strftime("%H:%M")
                booked_counts[time_str] = booked_counts.get(time_str, 0) + 1

            available_slots = []
            for slot in sorted(slots_capacity.keys()):
                if booked_counts.get(slot, 0) < slots_capacity[slot]:
                    available_slots.append(slot)

            return handle_response(success=True, message="Slots retrieved successfully", data=available_slots)

        else:
            return handle_response(success=False, message="Invalid appointment type", status_code=400)
