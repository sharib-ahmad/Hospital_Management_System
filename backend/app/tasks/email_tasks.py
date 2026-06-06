from ..extensions import db, celery
from celery import shared_task
from ..models import User, Application, Doctor, Nurse, Patient, Appointment, PharmacyOrder
from ..utils.mailer import Mailer
from datetime import datetime, time
import tempfile
import os
from zoneinfo import ZoneInfo
from decimal import Decimal

@shared_task(name='app.tasks.email_tasks.send_order_status_email')
def send_order_status_email(order_id):
    """
    Sends pharmacy order status update email.
    """
    order = PharmacyOrder.query.get(order_id)
    if not order:
        return f"Order {order_id} not found."
    
    # Context setup
    items_list = []
    for item in order.items:
        items_list.append({
            'name': item.medicine.name if item.medicine else 'Unknown Medicine',
            'quantity': item.quantity,
            'price': float(item.price)
        })
        
    context = {
        'user_name': order.user.full_name if order.user else 'Customer',
        'order_id': str(order.id),
        'order_date': order.order_date.strftime('%Y-%m-%d %H:%M:%S'),
        'shipping_address': order.shipping_address,
        'phone_number': order.phone_number,
        'status': order.status,
        'items': items_list,
        'total_price': float(order.total_price)
    }
    
    Mailer.send_email(
        to_email=order.user.email,
        subject=f"MediFlow Store - Order #{str(order.id)[:8]} Updated to {order.status.value}",
        template_name="order_status.html",
        context=context
    )
    return f"Order status email sent to {order.user.email}."

@shared_task(name='app.tasks.email_tasks.send_patient_approval_email')
def send_patient_approval_email(application_id):
    """
    Sends patient registration approval email.
    """
    application = Application.query.get(application_id)
    if not application:
        return f"Application {application_id} not found."
        
    user = User.query.get(application.user_id)
    if not user:
        return f"User {application.user_id} not found."
        
    # Find doctor name if assigned
    doctor_name = None
    if application.assigned_doctor_id:
        doc = Doctor.query.get(application.assigned_doctor_id)
        if doc and doc.user:
            doctor_name = doc.user.full_name
            
    context = {
        'user_name': user.full_name,
        'patient_name': application.patient_full_name or user.full_name,
        'relation': application.relation,
        'doctor_name': doctor_name
    }
    
    # Target email is user's registration email
    Mailer.send_email(
        to_email=user.email,
        subject="MediFlow - Patient Profile Approved",
        template_name="patient_approval.html",
        context=context
    )
    return f"Patient approval email sent to {user.email}."

@shared_task(name='app.tasks.email_tasks.send_appointment_email')
def send_appointment_email(appointment_id):
    """
    Sends appointment details confirmation email to user.
    """
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return f"Appointment {appointment_id} not found."
        
    # Send email to patient subprofile email or user email
    to_email = appointment.patient.email or appointment.patient.user.email
    if not to_email:
        return f"No email found for appointment {appointment_id}."
        
    context = {
        'patient_name': appointment.patient.full_name,
        'doctor_name': appointment.doctor_name,
        'specialization': appointment.doctor_specialization,
        'appointment_date': appointment.appointment_date.strftime('%Y-%m-%d %H:%M'),
        'appointment_type': appointment.appointment_type,
        'consultation_fee': float(appointment.consultation_fee),
        'reason': appointment.reason
    }
    
    status_label = appointment.status.value.upper() if hasattr(appointment.status, 'value') else str(appointment.status).upper()
    Mailer.send_email(
        to_email=to_email,
        subject=f"MediFlow - Appointment {status_label}: {context['appointment_date']}",
        template_name="appointment_scheduled.html",
        context=context
    )
    return f"Appointment status email sent to {to_email}."

@shared_task(name='app.tasks.email_tasks.send_daily_agenda_emails')
def send_daily_agenda_emails():
    """
    Daily 8:00 AM Agenda emails for active doctors and nurses.
    """
    kolkata_tz = ZoneInfo("Asia/Kolkata")
    now_local = datetime.now(kolkata_tz)
    today_date = now_local.date()
    
    start_of_today = datetime.combine(today_date, time.min)
    end_of_today = datetime.combine(today_date, time.max)
    
    # 1. Email all Doctors their agenda
    doctors = Doctor.query.all()
    doctors_sent = 0
    for doc in doctors:
        if not doc.user or not doc.user.email:
            continue
            
        # Get doctor's confirmed appointments for today
        appts = Appointment.query.filter(
            Appointment.doctor_id == doc.id,
            Appointment.appointment_date.between(start_of_today, end_of_today),
            Appointment.status.in_(['confirmed', 'completed']) # confirmed or completed
        ).order_by(Appointment.appointment_date.asc()).all()
        
        # Format appointment list
        appt_list = []
        for a in appts:
            appt_list.append({
                'time': a.appointment_date.strftime('%H:%M'),
                'patient_name': a.patient.full_name,
                'vitals_checked': a.vitals_checked,
                'reason': a.reason
            })
            
        context = {
            'doctor_name': doc.user.full_name,
            'date': today_date.strftime('%Y-%m-%d'),
            'appointments': appt_list
        }
        
        Mailer.send_email(
            to_email=doc.user.email,
            subject=f"MediFlow - Today's Consultation Agenda ({context['date']})",
            template_name="doctor_daily_agenda.html",
            context=context
        )
        doctors_sent += 1
        
    # 2. Email all Nurses their department agenda
    nurses = Nurse.query.all()
    nurses_sent = 0
    for nurse in nurses:
        if not nurse.user or not nurse.user.email or not nurse.department:
            continue
            
        # Get all appointments in nurse's department today
        # Wait, we match appointments where doctor belongs to the same department
        # Or standalone vitals checks where patient was assigned to this department or standalone vitals checks in general
        # Let's filter appointments for today where doctor's department_id is nurse's department_id OR standalone checkups
        # To make it clean, find all doctor ids in the department
        dept_doctor_ids = [d.id for d in nurse.department.doctors]
        
        appts = Appointment.query.filter(
            Appointment.appointment_date.between(start_of_today, end_of_today),
            Appointment.status.in_(['pending', 'confirmed', 'completed']),
            (Appointment.doctor_id.in_(dept_doctor_ids)) | (Appointment.appointment_type == 'vitals_check')
        ).order_by(Appointment.appointment_date.asc()).all()
        
        appt_list = []
        for a in appts:
            appt_list.append({
                'time': a.appointment_date.strftime('%H:%M'),
                'patient_name': a.patient.full_name,
                'doctor_name': a.doctor_name,
                'appointment_type': a.appointment_type,
                'vitals_checked': a.vitals_checked
            })
            
        context = {
            'nurse_name': nurse.user.full_name,
            'department_name': nurse.department.name,
            'date': today_date.strftime('%Y-%m-%d'),
            'appointments': appt_list
        }
        
        Mailer.send_email(
            to_email=nurse.user.email,
            subject=f"MediFlow - Today's Department Agenda ({context['date']})",
            template_name="nurse_daily_agenda.html",
            context=context
        )
        nurses_sent += 1
        
    return f"Daily agendas sent to {doctors_sent} doctors and {nurses_sent} nurses."

@shared_task(name='app.tasks.email_tasks.send_vitals_csv_email')
def send_vitals_csv_email(user_id, email):
    """
    Asynchronous task to generate vitals CSV and email it to the user.
    """
    user = User.query.get(user_id)
    if not user:
        return f"User {user_id} not found."
        
    from ..services.patient_vitals import PatientVitalsService
    
    csv_string = PatientVitalsService.generate_vitals_csv_string(user_id)
    
    # Save CSV string to a temporary file
    temp_dir = tempfile.gettempdir()
    temp_file_path = os.path.join(temp_dir, f"patient_vitals_{user_id}.csv")
    
    try:
        with open(temp_file_path, "w", newline="", encoding="utf-8") as f:
            f.write(csv_string)
            
        context = {
            'user_name': user.full_name,
            'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        Mailer.send_email(
            to_email=email,
            subject="MediFlow - Patient Vitals Export Ready",
            template_name="vitals_export.html",
            context=context,
            attachment_path=temp_file_path,
            attachment_name="my_patients_vitals.csv"
        )
    finally:
        # Perform cleanup of the temp file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            
    return f"Vitals CSV email sent to {email}."
