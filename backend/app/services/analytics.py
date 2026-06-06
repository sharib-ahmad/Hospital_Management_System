from ..extensions import db
from ..models.invoice import Invoice
from ..models.appointment import Appointment
from ..models.medical_record import MedicalRecord
from ..models.doctor import Doctor
from ..models.department import Department
from ..models.patient import Patient
from ..utils.enum import UserRole, AppointmentStatus
from ..utils.response import handle_response
from flask_jwt_extended import current_user
from sqlalchemy import func
from datetime import datetime, timedelta
import calendar

class AnalyticsService:
    @staticmethod
    def get_admin_analytics():
        """
        Calculates hospital-wide administrative analytics.
        """
        if current_user.role != UserRole.ADMIN:
            return handle_response(success=False, message="Unauthorized", status_code=403)
            
        # 1. Revenue: consultations vs pharmacy
        revenue_data = db.session.query(
            Invoice.invoice_type,
            func.sum(Invoice.amount)
        ).filter(Invoice.status == 'paid').group_by(Invoice.invoice_type).all()
        
        revenue = {'consultation': 0.0, 'pharmacy': 0.0}
        for rtype, rsum in revenue_data:
            if rtype in revenue:
                revenue[rtype] = float(rsum or 0.0)
                
        # 2. Patient volume per department
        # Count appointments grouped by doctor's department
        dept_volume = db.session.query(
            Department.name,
            func.count(Appointment.id)
        ).join(Doctor, Doctor.id == Appointment.doctor_id)\
         .join(Department, Department.id == Doctor.department_id)\
         .group_by(Department.name).all()
         
        departments = []
        patient_counts = []
        for dname, dcount in dept_volume:
            departments.append(dname)
            patient_counts.append(dcount)
            
        # Fallback if empty
        if not departments:
            departments = ['Cardiology', 'Pediatrics', 'General Medicine']
            patient_counts = [0, 0, 0]
            
        return handle_response(success=True, data={
            'revenue': revenue,
            'department_volume': {
                'labels': departments,
                'data': patient_counts
            }
        }, message="Admin analytics retrieved successfully")

    @staticmethod
    def get_doctor_analytics():
        """
        Calculates personal clinical analytics for the logged-in doctor.
        """
        if current_user.role != UserRole.DOCTOR:
            return handle_response(success=False, message="Unauthorized", status_code=403)
            
        doctor_id = current_user.id
        
        # 1. Consultation Trends (last 6 months)
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        trends = db.session.query(
            func.extract('month', Appointment.appointment_date).label('month'),
            func.count(Appointment.id)
        ).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date >= six_months_ago,
            Appointment.status == AppointmentStatus.COMPLETED
        ).group_by('month').all()
        
        month_labels = []
        appt_counts = []
        
        # Format labels
        for month_num, count in trends:
            month_name = calendar.month_abbr[int(month_num)]
            month_labels.append(month_name)
            appt_counts.append(count)
            
        if not month_labels:
            month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
            appt_counts = [0, 0, 0, 0, 0, 0]
            
        # 2. Top Diagnoses
        diagnoses = db.session.query(
            MedicalRecord.diagnosis,
            func.count(MedicalRecord.id).label('cnt')
        ).filter(MedicalRecord.doctor_id == doctor_id)\
         .group_by(MedicalRecord.diagnosis)\
         .order_by(func.count(MedicalRecord.id).desc())\
         .limit(5).all()
         
        diag_labels = []
        diag_counts = []
        for diag, cnt in diagnoses:
            # truncate long text
            short_diag = (diag[:20] + '...') if len(diag) > 20 else diag
            diag_labels.append(short_diag)
            diag_counts.append(cnt)
            
        if not diag_labels:
            diag_labels = ['Healthy', 'Hypertension', 'Diabetes', 'Common Cold', 'Fever']
            diag_counts = [0, 0, 0, 0, 0]
            
        # 3. Slot fill rate
        # Completed vs Confirmed vs Cancelled
        status_counts = db.session.query(
            Appointment.status,
            func.count(Appointment.id)
        ).filter(Appointment.doctor_id == doctor_id).group_by(Appointment.status).all()
        
        fill_rate = {'completed': 0, 'confirmed': 0, 'cancelled': 0, 'pending': 0}
        for status, count in status_counts:
            val = status.value if hasattr(status, 'value') else str(status)
            if val in fill_rate:
                fill_rate[val] = count
                
        return handle_response(success=True, data={
            'consultation_trends': {
                'labels': month_labels,
                'data': appt_counts
            },
            'diagnosis_distribution': {
                'labels': diag_labels,
                'data': diag_counts
            },
            'fill_rate': fill_rate
        }, message="Doctor analytics retrieved successfully")
