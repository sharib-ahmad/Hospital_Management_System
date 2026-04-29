# app/services/department.py
from ..extensions import db
from ..models.department import Department

class DepartmentService:
    @staticmethod
    def get_all_departments():
        return Department.query.all()

    @staticmethod
    def create_department(data):
        department = Department(
            id = data.department_id,
            name=data.name,
            description=data.description if hasattr(data, 'description') else data.get('description', None)
        )
        db.session.add(department)
        db.session.commit()
        return department

    @staticmethod
    def get_department_by_id(department_id):
        return Department.query.get(department_id)

    @staticmethod
    def update_department(department, data):
        """Update an existing department"""
        if isinstance(data, dict):
            if 'name' in data:
                department.name = data['name']
            if 'description' in data:
                department.description = data['description']
        else:
            if hasattr(data, 'name'):
                department.name = data.name
            if hasattr(data, 'description'):
                department.description = data.description
        
        db.session.commit()
        return department

    @staticmethod
    def delete_department(department):
        """Delete a department"""
        db.session.delete(department)
        db.session.commit()
