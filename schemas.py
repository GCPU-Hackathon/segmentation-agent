from pydantic import BaseModel, field_validator
from typing import Optional
from pathlib import Path

class SegmentationRequest(BaseModel):
    t1c_path: str
    t1n_path: str
    t2f_path: str
    t2w_path: str
    output_path: Optional[str] = None

    @field_validator('t1c_path', 't1n_path', 't2f_path', 't2w_path')
    @classmethod
    def validate_file_exists(cls, v):
        if not Path(v).exists():
            raise ValueError(f"File not found: {v}")
        return v


class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str


class TaskStatus(BaseModel):
    task_id: str
    status: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[dict] = None
    error: Optional[str] = None
    progress: Optional[str] = None
