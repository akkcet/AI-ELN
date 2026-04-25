# backend/agents/admin_request_agent.py
import re
from backend.database import get_db
from backend.models.admin_requests import AdminRequest
from datetime import datetime
import json
from backend.database import SessionLocal

ADMIN_PATTERNS = [
    r"create project (?P<name>.+)",
    r"add project (?P<name>.+)",
    r"create lookup (?P<name>.+)",
    r"add lookup (?P<name>.+)",
]

def is_admin_request(msg: str) -> bool:
    return any(re.search(p, msg.lower()) for p in ADMIN_PATTERNS)


def admin_request_agent(msg: str, user: str):
    db = SessionLocal()
    try:

        for p in ADMIN_PATTERNS:
            m = re.search(p, msg.lower())
            if m:
                payload = {"name": m.group("name").strip()}

                
                req = AdminRequest(
                    request_type="CREATE_PROJECT",
                    payload=json.dumps(payload),
                    status="NewRequest",
                    created_by=user,
                    created_at=datetime.utcnow(),
                )
                db.add(req)
                db.commit()
                db.refresh(req)
                return (
                    f"✅ Your request to create **{payload['name']}** "
                    "has been submitted for approval."
                )
    
    except Exception as e:
            db.rollback()
            raise e
    finally:
         db.close()

    #return "⚠️ Unable to understand the admin request."