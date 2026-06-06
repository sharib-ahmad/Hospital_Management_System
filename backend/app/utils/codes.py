import secrets
import string
from datetime import datetime

class CodeGenerator:
    """
    Utility class for generating industry-standard professional identifiers.
    Format: PREFIX-YYMM-RANDOM (e.g., DOC-2404-A7B)
    """
    
    @staticmethod
    def _generate(prefix: str, length: int = 3) -> str:
        # YYMM date component
        date_str = datetime.now().strftime("%y%m")
        # Cryptographically strong random suffix
        alphabet = string.ascii_uppercase + string.digits
        suffix = ''.join(secrets.choice(alphabet) for _ in range(length))
        return f"{prefix}-{date_str}-{suffix}"

    @classmethod
    def generate_doctor_code(cls) -> str:
        return cls._generate("DOC")

    @classmethod
    def generate_nurse_code(cls) -> str:
        return cls._generate("NUR")

    @classmethod
    def generate_pharmacist_code(cls) -> str:
        return cls._generate("PHM")
