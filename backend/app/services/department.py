# app/services/department.py
from ..extensions import db
from ..models.department import Department
from sqlalchemy.orm import selectinload

class DepartmentService:
    @staticmethod
    def get_all_departments():
        return Department.query.options(
            selectinload(Department.doctors),
            selectinload(Department.nurses)
        ).all()

    @staticmethod
    def create_department(data):
        department = Department(
            id = data.id,
            name = data.name,
            description = data.description,
            doctor_limit = data.doctor_limit,
            nurse_limit = data.nurse_limit
        )
        db.session.add(department)
        db.session.commit()
        
        # Trigger Google Chat notification task
        from ..tasks.email_tasks import send_department_creation_notification
        send_department_creation_notification.delay(department.id)
        
        return department

    @staticmethod
    def get_department_by_id(department_id):
        return Department.query.options(
            selectinload(Department.doctors),
            selectinload(Department.nurses)
        ).get(department_id)

    @staticmethod
    def update_department(department, data):
        """Update an existing department"""
        if isinstance(data, dict):
            if 'name' in data:
                department.name = data['name']
            if 'description' in data:
                department.description = data['description']
            if 'doctor_limit' in data:
                department.doctor_limit = data['doctor_limit']
            if 'nurse_limit' in data:
                department.nurse_limit = data['nurse_limit']
        else:
            if hasattr(data, 'name'):
                department.name = data.name
            if hasattr(data, 'description'):
                department.description = data.description
            if hasattr(data, 'doctor_limit'):
                department.doctor_limit = data.doctor_limit
            if hasattr(data, 'nurse_limit'):
                department.nurse_limit = data.nurse_limit
        
        db.session.commit()
        return department

    @staticmethod
    def delete_department(department):
        """Delete a department"""
        db.session.delete(department)
        db.session.commit()
