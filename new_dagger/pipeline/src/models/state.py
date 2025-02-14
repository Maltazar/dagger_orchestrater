from typing import Dict, Any
from enum import Enum
from pydantic import BaseModel

class ModuleState(str, Enum):
    """Possible states for a module"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class ModuleStateInfo(BaseModel):
    """Information about a module's state"""
    state: ModuleState
    data: Dict[str, Any] | None = None
    error: str | None = None 