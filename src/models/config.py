from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict, RootModel

class ExecutionDefaults(BaseModel):
    """Default execution settings"""
    timeout_seconds: int = 300
    max_attempts: int = 3
    delay_seconds: int = 5
    exponential_backoff: bool = True
    retry_on_exceptions: List[str] = Field(default_factory=lambda: ["ConnectionError", "TimeoutError"])
    retry: Optional[Dict[str, Any]] = None

class CoreConfig(BaseModel):
    """Core pipeline configuration"""
    execution_defaults: ExecutionDefaults = Field(default_factory=ExecutionDefaults)
class PipelineDefinition(BaseModel):
    """Pipeline definition - core config and extensions"""
    model_config = ConfigDict(extra='allow')
    
    core: CoreConfig
    extensions: Dict[str, Dict] = Field(default_factory=dict)

class PipelineConfig(RootModel):
    """Root configuration - allows any pipeline name as key"""
    root: Dict[str, PipelineDefinition]

    def get_pipeline(self) -> PipelineDefinition:
        """Get the first pipeline definition (since we only support one for now)"""
        return next(iter(self.root.values()))
