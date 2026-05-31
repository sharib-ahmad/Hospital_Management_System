from app import create_app
from app.extensions import db
from app.models.medistore import Medicine
from decimal import Decimal

def seed():
    app = create_app("development")
    with app.app_context():
        # Create all tables first
        db.create_all()
        
        # Check if medicines already exist
        if Medicine.query.first():
            print("Medicines already seeded in database.")
            return
            
        print("Seeding pharmacy medicines inventory...")
        dummy_medicines = [
            # Antibiotics
            {"name": "Amoxicillin 500mg", "description": "Broad-spectrum antibiotic used to treat bacterial infections.", "price": Decimal("14.50"), "stock": 100, "category": "Antibiotic", "manufacturer": "Sandoz"},
            {"name": "Azithromycin 250mg", "description": "Macrolide antibiotic commonly used for respiratory tract infections.", "price": Decimal("22.00"), "stock": 80, "category": "Antibiotic", "manufacturer": "Pfizer"},
            {"name": "Ciprofloxacin 500mg", "description": "Fluoroquinolone antibiotic for urinary tract and skin infections.", "price": Decimal("18.90"), "stock": 60, "category": "Antibiotic", "manufacturer": "Bayer"},
            
            # Pain Relief
            {"name": "Ibuprofen 400mg", "description": "Nonsteroidal anti-inflammatory drug (NSAID) to reduce fever and treat pain.", "price": Decimal("6.20"), "stock": 250, "category": "Pain Relief", "manufacturer": "Advil"},
            {"name": "Paracetamol 500mg", "description": "Common painkiller and antipyretic to treat mild to moderate pain.", "price": Decimal("4.50"), "stock": 300, "category": "Pain Relief", "manufacturer": "Tylenol"},
            {"name": "Naproxen 220mg", "description": "Long-acting NSAID for chronic joint pain and inflammation relief.", "price": Decimal("9.80"), "stock": 120, "category": "Pain Relief", "manufacturer": "Aleve"},
            
            # Supplements
            {"name": "Multivitamin Complex", "description": "Daily multivitamin tablet packed with essential minerals and vitamins.", "price": Decimal("12.99"), "stock": 150, "category": "Supplements", "manufacturer": "Nature Made"},
            {"name": "Vitamin C 1000mg", "description": "Ascorbic acid food supplement to support immune system functions.", "price": Decimal("8.50"), "stock": 200, "category": "Supplements", "manufacturer": "Centrum"},
            {"name": "Omega-3 Fish Oil", "description": "Supports cardiovascular, joint, brain, and eye health.", "price": Decimal("16.90"), "stock": 100, "category": "Supplements", "manufacturer": "Kirkland Signature"},
            
            # Cold & Flu
            {"name": "Dextromethorphan Syrup", "description": "Cough suppressant syrup to temporarily relieve non-productive cough.", "price": Decimal("7.50"), "stock": 140, "category": "Cold & Flu", "manufacturer": "Robitussin"},
            {"name": "Cetirizine 10mg", "description": "Non-drowsy antihistamine for seasonal allergy and hay fever relief.", "price": Decimal("5.99"), "stock": 180, "category": "Cold & Flu", "manufacturer": "Zyrtec"},
            {"name": "Pseudoephedrine 30mg", "description": "Oral nasal decongestant for temporary sinus pressure relief.", "price": Decimal("11.20"), "stock": 90, "category": "Cold & Flu", "manufacturer": "Sudafed"},
            
            # Heart Health
            {"name": "Atorvastatin 20mg", "description": "Statin medication used to prevent cardiovascular disease and lower cholesterol.", "price": Decimal("24.00"), "stock": 110, "category": "Heart Health", "manufacturer": "Lipitor"},
            {"name": "Metoprolol 50mg", "description": "Beta-blocker used to treat high blood pressure, chest pain, and heart failure.", "price": Decimal("19.50"), "stock": 95, "category": "Heart Health", "manufacturer": "Lopressor"}
        ]
        
        for item in dummy_medicines:
            med = Medicine(**item)
            db.session.add(med)
            
        db.session.commit()
        print("Successfully seeded medicines inventory!")

if __name__ == "__main__":
    seed()
