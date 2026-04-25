# backend/agents/workflow_agent.py
import re
from backend.database import get_db
from backend.models.admin_requests import AdminRequest
from datetime import datetime

def is_workflow_command(msg: str) -> bool:
    return any(k in msg for k in ["approve request", "reject request", "execute request"])

def workflow_agent(msg: str, user: str):
    db = get_db()

    if msg.startswith("approve request"):
        req_id = int(msg.split()[-1])
        req = db.query(AdminRequest).get(req_id)
        req.status = "Approved"
        req.approved_by = user
        db.commit()
        return f"✅ Request {req_id} approved."

    if msg.startswith("execute request"):
        req_id = int(msg.split()[-1])
        req = db.query(AdminRequest).get(req_id)
        req.status = "Execute"
        req.executed_by = user
        req.executed_at = datetime.utcnow()
        db.commit()
        return f"✅ Request {req_id} queued for execution."

    return "⚠️ Unknown workflow command."