
import os
from ..config import STORAGE_PATH

# Save uploaded file to local storage
def save_file(experiment_id: str, version: int, file) -> str:
    directory = f"{STORAGE_PATH}/{experiment_id}/{version}"
    os.makedirs(directory, exist_ok=True)

    file_path = f"{directory}/{file.filename}"
    with open(file_path, 'wb') as f:
        f.write(file.file.read())

    return file_path
