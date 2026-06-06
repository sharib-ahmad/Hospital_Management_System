# app/services/pharmacist.py
from ..extensions import db
from ..models.pharmacist import Pharmacist
from ..models.department import Department

class PharmacistService:
    @staticmethod
    def get_all_pharmacists():
        return Pharmacist.query.all()

    @staticmethod
    def get_pharmacist_by_id(pharmacist_id):
        return Pharmacist.query.get(pharmacist_id)

    @staticmethod
    def get_pharmacist_by_code(pharmacist_code):
        return Pharmacist.query.filter_by(pharmacist_code=pharmacist_code).first()

    @staticmethod
    def update_pharmacist(pharmacist_code, data):
        pharmacist = Pharmacist.query.filter_by(pharmacist_code=pharmacist_code).first()
        if not pharmacist:
            return None

        for key, value in data.dict(exclude_unset=True).items():
            if hasattr(pharmacist, key) and value is not None:
                setattr(pharmacist, key, value)
        
        db.session.commit()
        return pharmacist

    @staticmethod
    def get_pharmacists_by_department(department_id):
        return Pharmacist.query.filter_by(department_id=department_id).all()
