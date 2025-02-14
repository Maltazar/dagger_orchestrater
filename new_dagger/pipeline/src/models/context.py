from typing import Dict
from pydantic import BaseModel
import dagger
from .config import ModuleExecutionConfig

class ModuleContext(BaseModel):
    """Context object passed to modules containing shared resources"""
    client: dagger.Client
    workspace: dagger.Container
    secrets: Dict[str, dict]
    execution_config: ModuleExecutionConfig 