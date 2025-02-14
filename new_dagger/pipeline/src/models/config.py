from typing import Dict, List
from pydantic import BaseModel, Field

class RetryConfig(BaseModel):
    """Retry configuration for modules"""
    max_attempts: int = Field(default=3, ge=1)
    delay_seconds: float = Field(default=5.0, ge=0)
    exponential_backoff: bool = Field(default=True)
    retry_on_exceptions: List[str] = Field(default=["ConnectionError", "TimeoutError"])

class ModuleExecutionConfig(BaseModel):
    """Execution configuration for modules"""
    timeout_seconds: float = Field(default=300.0, ge=0)  # 5 minutes default
    retry: RetryConfig = Field(default_factory=RetryConfig)
    parallel_execution: bool = Field(default=True)

class ModuleConfig(BaseModel):
    """Base configuration for all modules"""
    execution: ModuleExecutionConfig = Field(default_factory=ModuleExecutionConfig)

class PipelineConfig(BaseModel):
    """Pipeline configuration validator"""
    name: str
    modules: Dict[str, List[ModuleConfig]] = Field(description="Module configurations")

    class Config:
        extra = "allow"  # Allow extra fields for module-specific configs 