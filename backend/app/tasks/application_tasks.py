from ..extensions import db, celery, cache
from celery import shared_task
from ..models import User, Application, Doctor, Nurse, Patient
from ..utils.enum import UserRole, ApplicationStatus
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

        # Update user role
        user.role = application.role_applied

        if application.role_applied == UserRole.DOCTOR:
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

        elif application.role_applied == UserRole.NURSE:
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

        elif application.role_applied == UserRole.PATIENT:
            new_profile = Patient(
                id=user.id,
                date_of_birth=application.date_of_birth,
                gender=application.gender,
                blood_group=application.blood_group,
                medical_history=application.medical_history,
                emergency_contact_number=application.emergency_contact_number,
                assigned_doctor_id=approver_id # Assign the doctor who approved the application
            )
            db.session.add(new_profile)

        db.session.commit()
        logger.info(f"Successfully processed approval for application {application_id}")

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error processing application approval: {str(e)}")
        raise e
