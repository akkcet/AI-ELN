from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from backend.database import get_db
from backend.models.admin_requests import AdminRequest


router = APIRouter(prefix="/admin-requests", tags=["AdminRequests"])

@router.get("/")
def list_requests(db: Session = Depends(get_db)):
    return db.query(AdminRequest).order_by(AdminRequest.created_at.desc()).all()


@router.post("/{request_id}/approve")
def approve_request(request_id: int, user: str, db: Session = Depends(get_db)):
    req = db.query(AdminRequest).filter(AdminRequest.id == request_id).first()
    if not req:
        raise HTTPException(404, "Request not found")

    req.status = "Approved"
    req.approved_by = user
    req.approved_at = datetime.utcnow()
    db.commit()

    return {"status": "approved"}


@router.post("/{request_id}/reject")
def reject_request(request_id: int, user: str, db: Session = Depends(get_db)):
    req = db.query(AdminRequest).filter(AdminRequest.id == request_id).first()
    if not req:
        raise HTTPException(404, "Request not found")

    req.status = "Rejected"
    db.commit()

    return {"status": "rejected"}