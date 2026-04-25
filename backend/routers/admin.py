# admin routes placeholder
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models.admin import Project, Lookup, LookupValue

router = APIRouter(prefix="/admin", tags=["admin"])


# ------------------------
# DB Dependency
# ------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------------
# ✅ PROJECT CRUD
# ---------------------------------------------------------
@router.get("/projects")
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).order_by(Project.name).all()


@router.post("/projects")
def create_project(name: str, db: Session = Depends(get_db)):
    proj = Project(name=name)
    db.add(proj)
    db.commit()
    db.refresh(proj)
    return proj


@router.put("/projects/{pid}")
def update_project(pid: int, name: str, db: Session = Depends(get_db)):
    proj = db.query(Project).filter(Project.id == pid).first()
    if not proj:
        raise HTTPException(404, "Project not found")
    proj.name = name
    db.commit()
    db.refresh(proj)
    return proj


@router.delete("/projects/{pid}")
def delete_project(pid: int, db: Session = Depends(get_db)):
    proj = db.query(Project).filter(Project.id == pid).first()
    if not proj:
        raise HTTPException(404, "Project not found")
    db.delete(proj)
    db.commit()
    return {"status": "deleted"}


# ---------------------------------------------------------
# ✅ LOOKUP CRUD
# ---------------------------------------------------------
@router.get("/lookups")
def list_lookups(db: Session = Depends(get_db)):
    return db.query(Lookup).all()


@router.post("/lookups")
def create_lookup(name: str, description: str, db: Session = Depends(get_db)):
    lu = Lookup(name=name, description=description)
    db.add(lu)
    db.commit()
    db.refresh(lu)
    return lu


@router.delete("/lookups/{lid}")
def delete_lookup(lid: int, db: Session = Depends(get_db)):
    lu = db.query(Lookup).filter(Lookup.id == lid).first()
    if not lu:
        raise HTTPException(404, "Lookup not found")
    db.delete(lu)
    db.commit()
    return {"status": "deleted"}


# ---------------------------------------------------------
# ✅ LOOKUP VALUE CRUD
# ---------------------------------------------------------
@router.get("/lookups/{lid}/values")
def list_lookup_values(lid: int, db: Session = Depends(get_db)):
    return db.query(LookupValue).filter(LookupValue.lookup_id == lid).all()


@router.post("/lookups/{lid}/values")
def add_lookup_value(lid: int, value: str, db: Session = Depends(get_db)):
    lv = LookupValue(lookup_id=lid, value=value)
    db.add(lv)
    db.commit()
    db.refresh(lv)
    return lv


@router.put("/lookups/{lid}/values/{vid}")
def update_lookup_value(lid: int, vid: int, value: str, db: Session = Depends(get_db)):
    lv = db.query(LookupValue).filter(LookupValue.id == vid).first()
    if not lv:
        raise HTTPException(404, "Lookup value not found")
    lv.value = value
    db.commit()
    db.refresh(lv)
    return lv


@router.delete("/lookups/{lid}/values/{vid}")
def delete_lookup_value(lid: int, vid: int, db: Session = Depends(get_db)):
    lv = db.query(LookupValue).filter(LookupValue.id == vid).first()
    if not lv:
        raise HTTPException(404, "Lookup value not found")
    db.delete(lv)
    db.commit()
    return {"status": "deleted"}
