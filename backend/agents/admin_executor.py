import json
import time
from datetime import datetime
from backend.database import SessionLocal
from backend.models.admin_requests import AdminRequest
from backend.models.admin import Project, Lookup, LookupValue

def execute_admin_requests():
    while True:
        db = SessionLocal()

        try:
            approved = db.query(AdminRequest).filter(
                AdminRequest.status == "Approved"
            ).all()

            for req in approved:
                payload = json.loads(req.payload)

                if req.request_type == "CREATE_PROJECT":
                    project = Project(name=payload["name"])
                    db.add(project)

                elif req.request_type == "CREATE_LOOKUP":
                    lookup = Lookup(
                        name=payload["name"],
                        description=payload.get("description", "")
                    )
                    db.add(lookup)

                elif req.request_type == "ADD_LOOKUP_VALUE":
                    lv = LookupValue(
                        lookup_id=payload["lookup_id"],
                        value=payload["value"]
                    )
                    db.add(lv)

                req.status = "Complete"
                req.executed_by = "system"
                req.executed_at = datetime.utcnow()

                db.commit()
                #db.refresh(lv)
        except Exception as e:
            print("Executor error:", e)
            db.rollback()
        finally:
            db.close()

        time.sleep(5)  # poll every 5 seconds