from ..extensions import db, celery, cache
from celery import shared_task
from ..models import User, Application, Doctor, Nurse, Patient, Pharmacist
from ..utils.enum import UserRole, ApplicationStatus, Relationship
from ..utils.codes import CodeGenerator
from ..extensions import logger

@shared_task(
    name='tasks.process_application_approval',
    bind=True,
    max_retries=3,
    default_retry_delay=5
)
def process_application_approval(self, application_id, approver_id=None):
    """
    Background task to update user role and create profile when an application is approved.
    """
    try:
        application = Application.query.get(application_id)
        if not application or application.status != ApplicationStatus.APPROVED:
            logger.warning(f"Application {application_id} not found or not in approved state.")
            return

        user = User.query.get(application.user_id)
        if not user:
            logger.error(f"User {application.user_id} not found.")
            return

        # We need to invalidate the department cache if a doctor or nurse is added
        # because the department 'staff' count will change.
        department_cache_invalidated = False

        if application.role_applied == UserRole.DOCTOR:
            # Update user role
            user.role = application.role_applied
            # Create Doctor Profile
            new_profile = Doctor(
                id=user.id,
                doctor_code=CodeGenerator.generate_doctor_code(),
                department_id=application.department_id,
                specialization=application.specialization,
                experience_years=application.experience_years,
                consultation_fee=application.consultation_fee,
                license_number=application.license_number,
                shift=application.shift,
                date_of_birth=application.date_of_birth,
                gender=application.gender,
                blood_group=application.blood_group,
                emergency_contact_number=application.emergency_contact_number
            )
            db.session.add(new_profile)
            
            # Invalidate doctor list cache
            from ..controllers.doctor_controller import DoctorController
            cache.delete_memoized(DoctorController._get_doctors_internal)
            department_cache_invalidated = True

        elif application.role_applied == UserRole.NURSE:
            # Update user role
            user.role = application.role_applied
            new_profile = Nurse(
                id=user.id,
                nurse_code=CodeGenerator.generate_nurse_code(),
                department_id=application.department_id,
                experience_years=application.experience_years,
                license_number=application.license_number,
                shift=application.shift,
                date_of_birth=application.date_of_birth,
                gender=application.gender,
                blood_group=application.blood_group,
                emergency_contact_number=application.emergency_contact_number
            )
            db.session.add(new_profile)
            
            # Invalidate nurse list cache
            from ..controllers.nurse_controller import NurseController
            cache.delete_memoized(NurseController._get_nurses_internal)
            department_cache_invalidated = True

        elif application.role_applied == UserRole.PHARMACIST:
            # Update user role
            user.role = application.role_applied
            new_profile = Pharmacist(
                id=user.id,
                pharmacist_code=CodeGenerator.generate_pharmacist_code(),
                department_id=application.department_id,
                experience_years=application.experience_years,
                license_number=application.license_number,
                shift=application.shift,
                date_of_birth=application.date_of_birth,
                gender=application.gender,
                blood_group=application.blood_group,
                emergency_contact_number=application.emergency_contact_number
            )
            db.session.add(new_profile)

        elif application.role_applied == UserRole.PATIENT:
            # For patients, we do NOT change the user's role. 
            # The user remains UserRole.USER (or whatever they were).
            new_profile = Patient(
                user_id=user.id,
                relation=application.relation or Relationship.SELF,
                full_name=application.patient_full_name or user.full_name,
                email=application.patient_email or user.email,
                phone_number=application.patient_phone_number or user.phone_number,
                address=application.patient_address or user.address,
                pincode=application.patient_pincode or user.pincode,
                date_of_birth=application.date_of_birth,
                gender=application.gender,
                blood_group=application.blood_group,
                medical_history=application.medical_history,
                emergency_contact_number=application.emergency_contact_number,
                assigned_doctor_id=approver_id # Assign the doctor who approved the application
            )
            db.session.add(new_profile)

        # Expire user sessions on role change (Doctor, Nurse, Pharmacist approved)
        if application.role_applied in [UserRole.DOCTOR, UserRole.NURSE, UserRole.PHARMACIST]:
            from datetime import datetime, timezone
            user.tokens_valid_after = datetime.now(timezone.utc).replace(tzinfo=None)

        db.session.commit()
        
        # Trigger In-App Notification
        from ..services.notification import NotificationService
        NotificationService.create_notification(
            user_id=application.user_id,
            title="Application Approved",
            message=f"Your application for role {application.role_applied.value} has been approved.",
            category="application"
        )
        
        # Trigger Email send
        if application.role_applied == UserRole.PATIENT:
            from .email_tasks import send_patient_approval_email
            send_patient_approval_email.delay(application.id)
        elif application.role_applied in [UserRole.DOCTOR, UserRole.NURSE, UserRole.PHARMACIST]:
            from .email_tasks import send_staff_approval_email
            send_staff_approval_email.delay(application.id)
        
        if department_cache_invalidated:
            # Clear the department list cache to update staff counts
            from ..controllers.department_controller import DEPARTMENTS_CACHE_KEY
            cache.delete(DEPARTMENTS_CACHE_KEY)
            
        logger.info(f"Successfully processed approval for application {application_id}")

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error processing application approval: {str(e)}")
        raise e
