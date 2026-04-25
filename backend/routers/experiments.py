import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime
import uuid

from fastapi import UploadFile, File
import os
import shutil
from backend.services.audit_service import log_event
from ..database import SessionLocal
from ..models.experiment import Experiment
from ..models.version import ExperimentVersion
from ..models.signature import ExperimentSignature
from ..schemas.experiment_schema import ExperimentCreateRequest


router = APIRouter(prefix="/experiments", tags=["experiments"])


# ------------------------
# DB Dependency
# ------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def generate_id():
    year = datetime.now().strftime("%y")  # 2-digit year
    unique_part = uuid.uuid4().hex[:6].upper()
    return f"EXP-{year}-{unique_part}"

# ------------------------
# CREATE EXPERIMENT
# ------------------------
@router.post("/")
def create_experiment(
    payload: ExperimentCreateRequest,
    db: Session = Depends(get_db),
):
    
    exp = Experiment(
        experiment_id= generate_id(),
        #title=payload.title,
        author=payload.author,
        #project_id=payload.project_id,
        #category_id=payload.category_id,
        status="NEW",
        updated_at=datetime.utcnow(),
    )

    db.add(exp)
    db.commit()
    db.refresh(exp)
    log_event(db=db,user=exp.author,action="CREATE",entity="experiment",                       
            entity_id=exp.experiment_id,details="Experiment created." )
    #audit_event(db, exp.author, "CREATE", "Experiment", exp.experiment_id)

    return {"experiment_id": exp.experiment_id}


# ------------------------
# LIST / SEARCH EXPERIMENTS  ✅ ONE ENDPOINT
# ------------------------
@router.get("/")
def list_or_search_experiments(
    q: str | None = None,
    user: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Experiment)
    print("list_or_search_experiments is executed")
    if q:
        query = query.filter(
            or_(
                Experiment.experiment_id.ilike(f"%{q}%"),
                #Experiment.title.ilike(f"%{q}%"),
            )
        )

    if user:
        query = query.filter(Experiment.author == user)

    rows = query.order_by(Experiment.updated_at.desc()).all()

    return [
        {
            "experiment_id": r.experiment_id,
            "title": r.title,
            "status": r.status,
            "created_at": r.created_at,
            "author": r.author,
            "project_id": r.project_id
        }
        for r in rows
    ]
##SAVE EXPERIMENT

@router.post("/{exp_id}/update")
def update_experiment(
    exp_id: str,
    payload: dict,
    db: Session = Depends(get_db),
):
    exp = db.query(Experiment).filter(
        Experiment.experiment_id == exp_id
    ).first()

    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")

    if exp.status not in ["NEW", "REJECTED"]:
        raise HTTPException(status_code=400, detail="Experiment is locked")

    sections = payload.get("sections")
    if sections is None:
        raise HTTPException(status_code=400, detail="No sections provided")

    # ✅ Persist updated document
    exp.sections = json.dumps(sections)
    exp.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(exp)
    print("Experiment updated and saved to DB", exp.sections)
    log_event(db=db,user=exp.author,action="UPDATE",entity="experiment",                       
            entity_id=exp_id,details="Experiment sections updated." )

    return {"status": "saved"}

# ------------------------
# GET EXPERIMENT DETAILS  ✅ SINGLE CANONICAL ROUTE
# -----------------------
@router.get("/{exp_id}")
def get_experiment(exp_id: str, db: Session = Depends(get_db)):
    exp = db.query(Experiment).filter(
        Experiment.experiment_id == exp_id
    ).first()
    print("get_experiment is executed")
    if exp is None:
        raise HTTPException(status_code=404, detail="Experiment not found")

    versions = (
        db.query(ExperimentVersion)
        .filter(ExperimentVersion.experiment_id == exp_id)
        .order_by(ExperimentVersion.version.asc())
        .all()
    )
    
    try:
        sections = json.loads(exp.sections) if exp.sections else []
    except Exception:
        sections = []
    print("get experiment details: ",sections)
    return {
        "experiment_id": exp.experiment_id,
        "title": exp.title,
        "author": exp.author,
        "status": exp.status,
        "sections": sections,
        "date_started": exp.created_at,
        "versions": [
            {
                "version": v.version,
                "saved_at": v.saved_at.isoformat(),
                "saved_by": v.saved_by,
                "hash": v.hash_value,
            }
            for v in versions
        ],
    }
# ------------------------
# INSERT SECTIONS
# ------------------------

@router.post("/{exp_id}/sections")
def add_section(
    exp_id: str,
    section_type: str,
    db: Session = Depends(get_db)
):
    exp = db.query(Experiment).filter(Experiment.experiment_id == exp_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    if exp.status not in ["NEW", "REJECTED"]:
        raise HTTPException(status_code=400, detail="Experiment is locked")

    sections = json.loads(exp.sections or "[]")
    new_section = {
        "id": str(uuid.uuid4()),
        "type": section_type,
        "content": "",
        "position": len(sections)   # ✅ order is insertion order
    }
    print(new_section)
    sections.append(new_section)
    exp.sections = json.dumps(sections)
    exp.updated_at = datetime.utcnow()
    db.add(exp)
    db.commit()
    db.refresh(exp)
    
    log_event(db=db,user=exp.author,action="SECTION_ADD",
        entity="experiment",entity_id=exp_id,details=f"Added section '{section_type}'"
    )

    return new_section

#patch a specific section content

@router.patch("/{exp_id}/sections/{section_id}")
def update_section(
    exp_id: str,
    section_id: str,
    payload: dict,
    db: Session = Depends(get_db)
):
    exp = db.query(Experiment).filter(
        Experiment.experiment_id == exp_id
    ).first()

    
    if not exp:
            raise HTTPException(status_code=404, detail="Experiment not found")

    sections = json.loads(exp.sections or "[]")

    for section in sections:
        if section["id"] == section_id:

            # ✅ Update label if present
            if "label" in payload and payload["label"] is not None:
                section["label"] = payload["label"]

            # ✅ Update content if present
            if "content" in payload and payload["content"] is not None:
                section["content"] = payload["content"]

            # ✅ ✅ ✅ THIS IS WHERE REACTION GOES
            if "reaction" in payload and payload["reaction"] is not None:
                section["reaction"] = payload["reaction"]

            break
    else:
        raise HTTPException(status_code=404, detail="Section not found")


    exp.sections = json.dumps(sections)
    exp.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(exp)
    log_event(db=db,user=exp.author,action="SECTION_UPDATE",
        entity="experiment",entity_id=exp_id,details=f"Updated section '{section_id}'"
    )
    return {"status": "saved"}

# ------------------------
# DELETE/REMOVE SECTIONS
# ------------------------
@router.delete("/{exp_id}/sections/{section_id}")
def delete_section(
    exp_id: str,
    section_id: str,
    db: Session = Depends(get_db),
    ):
    exp = db.query(Experiment).filter(
        Experiment.experiment_id == exp_id
    ).first()

    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")

    if exp.status not in ["NEW", "REJECTED"]:
        raise HTTPException(status_code=400, detail="Experiment is locked")

    sections = json.loads(exp.sections or "[]")

    new_sections = [s for s in sections if s["id"] != section_id]

    if len(new_sections) == len(sections):
        raise HTTPException(status_code=404, detail="Section not found")

    exp.sections = json.dumps(new_sections)
    exp.updated_at = datetime.utcnow()

    db.commit()
    
    log_event(
        db=db,
        user=exp.author,
        action="SECTION DELETE",
        entity="experiment",
        entity_id=exp_id,
        details=f"Section deleted {section_id}"
    )

    return {"status": "deleted"}

# ------------------------
# REORDER SECTIONS
# ------------------------
@router.post("/{exp_id}/sections/{section_id}/move")
def move_section(
    exp_id: str,
    section_id: str,
    direction: str,
    db: Session = Depends(get_db),
):
    exp = db.query(Experiment).filter(
        Experiment.experiment_id == exp_id
    ).first()

    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")

    if exp.status not in ["NEW", "REJECTED"]:
        raise HTTPException(status_code=400, detail="Experiment is locked")

    sections = json.loads(exp.sections or "[]")

    idx = next((i for i, s in enumerate(sections) if s["id"] == section_id), None)

    if idx is None:
        raise HTTPException(status_code=404, detail="Section not found")

    if direction == "up" and idx > 0:
        sections[idx], sections[idx - 1] = sections[idx - 1], sections[idx]

    elif direction == "down" and idx < len(sections) - 1:
        sections[idx], sections[idx + 1] = sections[idx + 1], sections[idx]

    else:
        return {"status": "noop"}

    exp.sections = json.dumps(sections)
    exp.updated_at = datetime.utcnow()

    db.commit()

    return {"status": "moved"}
# ------------------------
# FILE ATTACHMENT
# ------------------------

UPLOAD_FOLDER = "backend/uploads"

@router.post("/{exp_id}/upload")
async def upload_file(
    exp_id: str,
    section_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    exp = db.query(Experiment).filter(
        Experiment.experiment_id == exp_id
    ).first()

    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")

    if exp.status not in ["NEW", "REJECTED"]:
        raise HTTPException(status_code=400, detail="Experiment is locked")

    # Prepare target folder
    folder_path = os.path.join(UPLOAD_FOLDER, exp_id)
    os.makedirs(folder_path, exist_ok=True)

    # Save file
    file_path = os.path.join(folder_path, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Update section JSON
    import json
    sections = json.loads(exp.sections or "[]")

    for sec in sections:
        if sec["id"] == section_id:
            if "files" not in sec:
                sec["files"] = []
            sec["files"].append({
                "file_name": file.filename,
                "file_path": file_path.replace("backend/", "")
            })

    exp.sections = json.dumps(sections)
    db.commit()
    db.refresh(exp)
    
    log_event(
        db=db,
        user=exp.author,
        action="FILE_UPLOAD",
        entity="experiment",
        entity_id=exp_id,
        details=f"Uploaded file '{file.filename}' in section {section_id}"
    )

    return {"status": "uploaded", "file_name": file.filename}


# ------------------------
# WORKFLOW ACTIONS
# ------------------------
@router.post("/{exp_id}/submit")
def submit_experiment(exp_id: str,password: str, db: Session = Depends(get_db)):
    exp = db.query(Experiment).filter_by(experiment_id=exp_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")

    #if exp.status != "NEW":
     #   raise HTTPException(status_code=400, detail="Only NEW experiments can be submitted")
        
    if not password:
            raise HTTPException(status_code=401, detail="Password required")

    exp.status = "SUBMITTED"
    exp.updated_at = datetime.utcnow()
    
    sig = ExperimentSignature(
            experiment_id=exp_id,
            signed_by=exp.author,
            action="SUBMIT",
        )
    db.add(sig)
    db.commit()
    
    log_event(
        db=db,
        user=exp.author,
        action="SUBMIT",
        entity="experiment",
        entity_id=exp_id,
        details="Experiment submitted for review"
    )

    
    return {"status": "SUBMITTED"}


@router.post("/{exp_id}/approve")
def approve_experiment(exp_id: str, password: str, db: Session = Depends(get_db)):
    exp = db.query(Experiment).filter_by(experiment_id=exp_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")

    if exp.status != "SUBMITTED":
        raise HTTPException(status_code=400, detail="Only SUBMITTED experiments can be approved")
    
    if not password:
            raise HTTPException(status_code=401)

    exp.status = "COMPLETED"
    exp.updated_at = datetime.utcnow()
    
    sig = ExperimentSignature(
            experiment_id=exp_id,
            signed_by="reviewer",   # replace later with real user
            action="APPROVE",
        )
    db.add(sig)
    db.commit()
    
    log_event(
        db=db,
        user="Reviewer",
        action="APPROVE",
        entity="experiment",
        entity_id=exp_id,
        details="Experiment approved"
    )

    
    return {"status": "COMPLETED"}


@router.post("/{exp_id}/reject")
def reject_experiment(exp_id: str, reason: str, db: Session = Depends(get_db)):
    exp = db.query(Experiment).filter_by(experiment_id=exp_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")

    if exp.status != "SUBMITTED":
        raise HTTPException(status_code=400, detail="Only SUBMITTED experiments can be rejected")

    exp.status = "REJECTED"
    exp.updated_at = datetime.utcnow()
    db.commit()
    
    log_event(
        db=db,
        user="Reviewer",
        action="REJECT",
        entity="experiment",
        entity_id=exp_id,
        details=f"Rejected experiment: {reason}"
    )

    
    return {"status": "REJECTED"}
