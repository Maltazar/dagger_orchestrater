from enum import Enum
from typing import Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class PipelineStatus(str, Enum):
    """Pipeline execution status"""
    INITIALIZING = "initializing"
    VALIDATING = "validating"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PipelineStats(BaseModel):
    """Pipeline execution statistics"""
    start_time: datetime | None = None
    end_time: datetime | None = None
    duration_seconds: float = 0.0
    modules_total: int = 0
    modules_completed: int = 0
    modules_failed: int = 0
    current_module: str | None = None

class PipelineStatusInfo(BaseModel):
    """Pipeline status information"""
    status: PipelineStatus
    stats: PipelineStats = Field(default_factory=PipelineStats)
    error: str | None = None
    metrics: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    additional_info: Dict[str, Any] = Field(default_factory=dict) 