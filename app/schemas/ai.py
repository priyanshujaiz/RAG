import stat
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List, Dict, Any, Optional

#INPUT
class AIRunCreate(BaseModel):
    run_type: str="DOCUMENT_QA"
    document_ids: List[UUID]
    parameters: Dict[str, Any]

#OUTPUT
class AIRunResponse(BaseModel):
    id:UUID
    project_id:UUID
    run_type:str
    status:str
    input_payload:Optional[Dict[str, Any]]=None
    output_payload:Optional[Dict[str, Any]]=None
    error_message:Optional[str]=None
    created_at:datetime
    started_at:Optional[datetime]=None
    finished_at:Optional[datetime]=None

    class Config:
        from_attributes = True


