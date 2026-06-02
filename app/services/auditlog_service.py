from app.models.auditlog_model import AuditLog

class AuditLogService:
    def __init__(self, db):
        self.db = db

    def create_log(self, user_id, action, entity_type, entity_id):
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id
        )

        self.db.add(audit_log)

        return audit_log
    
    def get_logs(self):
        return (
            self.db.query(AuditLog)
            .order_by(
                AuditLog.created_at.desc()
            ).all()
        )