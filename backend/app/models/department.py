from ..extensions import db
from ..utils.time import utc_now

class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=utc_now)
    
    # Relationships
    doctors = db.relationship('Doctor', back_populates='department', lazy=True)

    def __repr__(self):
        return f"<Department {self.name}>"
