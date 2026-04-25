from pydantic import BaseModel
from typing import Optional
class ExperimentCreateRequest(BaseModel):
    title:  Optional[str] = None
    author: str
    project_id:  Optional[str] = None
    category_id:  Optional[str] = None
    #notes: str | None = None