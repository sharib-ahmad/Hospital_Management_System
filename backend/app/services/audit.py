from ..extensions import db
from ..models.audit_log import AuditLog
from flask import request
import json

class AuditService:
    @staticmethod
    def log_action(user_id, action, details=None):
        """
        Creates an audit log entry for user actions (accessing or modifying PHI).
        """
        ip_addr = None
        try:
            if request:
                ip_addr = request.headers.get('X-Forwarded-For', request.remote_addr)
                if ip_addr and ',' in ip_addr:
                    ip_addr = ip_addr.split(',')[0].strip()
        except RuntimeError:
            pass

        details_str = None
        if details:
            try:
                details_str = json.dumps(details)
            except Exception:
                details_str = str(details)

        try:
            audit = AuditLog(
                user_id=user_id,
                action=action,
                ip_address=ip_addr,
                details=details_str
            )
            db.session.add(audit)
            db.session.commit()
            return audit
        except Exception as e:
            db.session.rollback()
            from ..extensions import logger
            logger.error(f"Audit log writing failed: {str(e)}")
            return None
