from pydantic import BaseModel, field_validator
from typing import Optional
from pathlib import Path

BASE_STUDIES_DIR = Path("storage") / "studies"

class SegmentationRequest(BaseModel):
    study_code: str
    simulate: Optional[bool] = False

    @field_validator("study_code")
    @classmethod
    def validate_study_dir(cls, v: str):
        study_dir = BASE_STUDIES_DIR / v
        if not study_dir.exists() or not study_dir.is_dir():
            raise ValueError(f"Study directory not found: {study_dir}")

        required_suffixes = ["t1c.nii.gz", "t1n.nii.gz", "t2f.nii.gz", "t2w.nii.gz"]
        missing = []
        for suf in required_suffixes:
            matches = list(study_dir.glob(f"*{suf}"))
            if not matches:
                missing.append(suf)
        if missing:
            raise ValueError(f"Missing required files in {study_dir}: {', '.join(missing)}")

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
