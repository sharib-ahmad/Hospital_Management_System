from ..extensions import db
from ..models.applications import Application
from ..models.user import User
from ..models.department import Department
from ..utils.enum import UserRole, ApplicationStatus
from ..utils.response import handle_response
from flask_jwt_extended import current_user
from ..tasks.application_tasks import process_application_approval

class ApplicationService:
    
    @staticmethod
    def get_all_applications():
        user = User.query.get(current_user.id)
        if user.role == UserRole.ADMIN:
            applications = Application.query.all()
            return handle_response(success=True, data=applications, message="Applications retrieved successfully")
        
        elif user.role == UserRole.DOCTOR or user.role == UserRole.NURSE:
            applications = Application.query.filter_by(role_applied=UserRole.PATIENT).all()
            return handle_response(success=True, data=applications, message="Patient applications retrieved successfully")

    @staticmethod
    def get_user_applications(user_id):
        applications = Application.query.filter_by(user_id=user_id).all()
        return handle_response(success=True, data=applications, message="User applications retrieved successfully")
        
        

    @staticmethod
    def create_patient_application(validated_data):
        user = User.query.get(current_user.id)
        
        # We allow multiple patient applications from the same user now.
        # But maybe we want to avoid duplicate pending applications for the same patient name?
        if validated_data.full_name:
            existing_application = Application.query.filter_by(
                user_id=user.id, 
                role_applied=UserRole.PATIENT, 
                patient_full_name=validated_data.full_name,
                status=ApplicationStatus.PENDING
            ).first()
            if existing_application:
                return handle_response(success=False, message=f"An application for {validated_data.full_name} is already pending", status_code=400)

        # Map full_name to patient_full_name, etc.
        app_data = validated_data.dict()
        app_data['patient_full_name'] = app_data.pop('full_name', None)
        app_data['patient_email'] = app_data.pop('email', None)
        app_data['patient_phone_number'] = app_data.pop('phone_number', None)
        app_data['patient_address'] = app_data.pop('address', None)
        app_data['patient_pincode'] = app_data.pop('pincode', None)
        # 'relation' is in app_data and matches Application.relation

        application = Application(
            user_id=user.id,
            role_applied=UserRole.PATIENT,
            **app_data
        )
        db.session.add(application)
        db.session.commit()
        return handle_response(success=True, data=application, message="Patient application created successfully", status_code=201)

    @staticmethod
    def create_doctor_application(validated_data):
        user = User.query.get(current_user.id)
        existing_application = Application.query.filter_by(user_id=user.id, role_applied=UserRole.DOCTOR).first()
        if existing_application and existing_application.status == ApplicationStatus.PENDING:
            return handle_response(success=False, message="You have already applied for doctor role", status_code=400)

        # Validate department
        department = Department.query.get(validated_data.department_id)
        if not department:
            return handle_response(success=False, message=f"Department with ID {validated_data.department_id} does not exist", status_code=404)

        application = Application(
            user_id=user.id,
            role_applied=UserRole.DOCTOR,
            **validated_data.dict()
        )
        db.session.add(application)
        db.session.commit()
        return handle_response(success=True, data=application, message="Doctor application created successfully", status_code=201)

    @staticmethod
    def create_nurse_application(validated_data):
        user = User.query.get(current_user.id)
        existing_application = Application.query.filter_by(user_id=user.id, role_applied=UserRole.NURSE).first()
        if existing_application and existing_application.status == ApplicationStatus.PENDING:
            return handle_response(success=False, message="You have already applied for nurse role", status_code=400)

        # Validate department
        department = Department.query.get(validated_data.department_id)
        if not department:
            return handle_response(success=False, message=f"Department with ID {validated_data.department_id} does not exist", status_code=404)

        application = Application(
            user_id=user.id,
            role_applied=UserRole.NURSE,
            **validated_data.dict()
        )
        db.session.add(application)
        db.session.commit()
        return handle_response(success=True, data=application, message="Nurse application created successfully", status_code=201)

    @staticmethod
    def approve_application(application_id):
        user = User.query.get(current_user.id)
        application = Application.query.get(application_id)
        
        if not application:
            return handle_response(success=False, message="Application not found", status_code=404)
        
        if application.status != ApplicationStatus.PENDING:
            return handle_response(success=False, message=f"Application is already {application.status.value}", status_code=400)

        # Role-based approval logic
        can_approve = False
        if application.role_applied == UserRole.DOCTOR:
            if user.role == UserRole.ADMIN:
                # Check department limit
                department = Department.query.get(application.department_id)
                if department and len(department.doctors) >= department.doctor_limit:
                    return handle_response(
                        success=False, 
                        message=f"Department {department.name} has reached its doctor limit ({department.doctor_limit})", 
                        status_code=400
                    )
                can_approve = True
        
        elif application.role_applied == UserRole.NURSE:
            if user.role in [UserRole.ADMIN, UserRole.DOCTOR]:
                # Check department limit
                department = Department.query.get(application.department_id)
                if department and len(department.nurses) >= department.nurse_limit:
                    return handle_response(
                        success=False, 
                        message=f"Department {department.name} has reached its nurse limit ({department.nurse_limit})", 
                        status_code=400
                    )
                can_approve = True
        
        elif application.role_applied == UserRole.PATIENT:
            if user.role == UserRole.DOCTOR:
                can_approve = True
        
        if not can_approve:
            return handle_response(success=False, message="You are not authorized to approve this application", status_code=403)

        application.status = ApplicationStatus.APPROVED
        db.session.commit()

        # Trigger Celery Task
        process_application_approval.delay(application.id, user.id)

        return handle_response(success=True, message="Application approved. Background processing started.")

    @staticmethod
    def reject_application(application_id, reason=None):
        user = User.query.get(current_user.id)
        application = Application.query.get(application_id)

        if not application:
            return handle_response(success=False, message="Application not found", status_code=404)

        # Use same role logic as approval for simplicity, or adjust as needed
        can_reject = False
        if application.role_applied == UserRole.DOCTOR:
            if user.role == UserRole.ADMIN:
                can_reject = True
        elif application.role_applied == UserRole.NURSE:
            if user.role in [UserRole.ADMIN, UserRole.DOCTOR]:
                can_reject = True
        elif application.role_applied == UserRole.PATIENT:
            if user.role == UserRole.DOCTOR:
                can_reject = True

        if not can_reject:
            return handle_response(success=False, message="You are not authorized to reject this application", status_code=403)

        application.status = ApplicationStatus.REJECTED
        if reason:
            application.reason = f"REJECTED: {reason}"
        db.session.commit()

        return handle_response(success=True, message="Application rejected successfully.")
