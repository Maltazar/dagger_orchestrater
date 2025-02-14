from typing import Dict
from pydantic import BaseModel

class ModuleResult(BaseModel):
    """Base class for module execution results"""
    success: bool
    message: str
    data: Dict[str, dict] | None = None
    error: str | None = None 