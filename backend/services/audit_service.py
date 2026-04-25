from datetime import datetime
from ..models.audit import AuditLog
#from sqlalchemy.orm import Session


def log_event(db, user: str, action: str, entity: str, entity_id: str, details: str):
    print("🔥 AUDIT EVENT ->", user, action, entity, entity_id, details, db)
    entry = AuditLog(
        user=user,
        action=action,
        entity=entity,
        entity_id=entity_id,
        details=details,
        timestamp=datetime.utcnow()
    )
    print(entry)
    db.add(entry)
    db.commit()
    db.refresh(entry)

