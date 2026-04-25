from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..models.audit import AuditLog
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from ..database import SessionLocal
from fastapi.responses import FileResponse
router = APIRouter(prefix="/audit", tags=["audit"])
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
@router.get("/experiments")
def get_audit(exp_id: str, db: Session = Depends(get_db)):

    logs = db.query(AuditLog).filter(
        AuditLog.entity == "experiment",
        AuditLog.entity_id == exp_id
    ).order_by(AuditLog.timestamp.asc()).all()

    return [
        {
            "timestamp": log.timestamp.isoformat(),
            "user": log.user,
            "action": log.action,
            "details": log.details
        }
        for log in logs
    ]


@router.get("/filter")
def filter_audit(
    user: str = "",
    action: str = "",
    entity: str = "",
    entity_id: str = "",
    date_from: str = "",
    date_to: str = "",
    db: Session = Depends(get_db)
):
    #print("entry in router filter")
    """
    ✅ Returns ALL audit logs if ALL filters are empty.
    ✅ Applies filters ONLY for non-empty query params.
    ✅ Never crashes (invalid date, None, empty strings are handled safely).
    """

    query = db.query(AuditLog)

    # ---- APPLY FILTERS ONLY IF USER CLICKED THE BUTTON ----
    if user.strip():
        query = query.filter(AuditLog.user.ilike(f"%{user.strip()}%"))

    if action.strip():
        query = query.filter(AuditLog.action.ilike(f"%{action.strip()}%"))

    if entity.strip():
        query = query.filter(AuditLog.entity.ilike(f"%{entity.strip()}%"))

    if entity_id.strip():
        #print("audit also empty")
        query = query.filter(AuditLog.entity_id.ilike(f"%{entity_id.strip()}%"))
    
    # ---- SAFE DATE HANDLING ----
    try:
        if date_from.strip():
            query = query.filter(AuditLog.timestamp >= date_from)
        if date_to.strip():
            query = query.filter(AuditLog.timestamp <= date_to)
    except:
        # Ignore invalid date formats instead of crashing
        pass

    logs = query.order_by(AuditLog.timestamp.desc()).all()

    # ---- FORMAT RESPONSE FOR FRONTEND TABLE ----
    return [
        {
            "Timestamp": log.timestamp.isoformat(),
            "User": log.user,
            "Action": log.action,
            "Description": log.details,
            "Object Type": log.entity,
            "Object ID": log.entity_id,
        }
        for log in logs
    ]


@router.get("/export/pdf")
def export_audit_pdf(
    user: str | None = None,
    action: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    db: Session = Depends(get_db)
):

    # fetch filtered logs
    query = db.query(AuditLog)
    if user:
        query = query.filter(AuditLog.user.ilike(f"%{user}%"))
    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action}%"))
    if date_from:
        query = query.filter(AuditLog.timestamp >= date_from)
    if date_to:
        query = query.filter(AuditLog.timestamp <= date_to)

    logs = query.order_by(AuditLog.timestamp.asc()).all()

    # generate PDF
    filename = "audit_export.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    y = 750
    c.setFont("Helvetica", 10)

    for log in logs:
        text = f"{log.timestamp} | {log.user} | {log.action} | {log.entity} | {log.details}"
        c.drawString(30, y, text)
        y -= 15
        if y < 50:
            c.showPage()
            y = 750

    c.save()
    return FileResponse(filename, media_type="application/pdf", filename=filename)
