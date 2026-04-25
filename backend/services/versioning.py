
import json, uuid
from datetime import datetime
from ..models.version import ExperimentVersion
from ..services.hashing import compute_hash

def create_new_version(db, experiment_id, payload_dict, username):
    data_json = json.dumps(payload_dict)
    hash_val = compute_hash(data_json)

    # Determine latest version number
    latest = db.query(ExperimentVersion).filter_by(experiment_id=experiment_id).order_by(ExperimentVersion.version.desc()).first()
    version_num = 1 if latest is None else latest.version + 1

    version = ExperimentVersion(
        experiment_id=experiment_id,
        version=version_num,
        data_json=data_json,
        hash_value=hash_val,
        saved_by=username,
        saved_at=datetime.utcnow()
    )
    db.add(version)
    db.commit()
    return version_num
