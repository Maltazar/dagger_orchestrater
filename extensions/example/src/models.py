"""Models for the example extension."""

from typing import List, Optional
from pydantic import BaseModel, Field

class ExampleCommand(BaseModel):
    """Model for a command to be executed"""
    command: str = Field(..., description="Command to execute")
    working_dir: Optional[str] = Field(default="/src", description="Working directory for command")
    env_vars: dict[str, str] = Field(default_factory=dict, description="Environment variables for command")

class ExampleConfig(BaseModel):
    """Configuration model for example extension
    
    This model defines the structure of the configuration that
    should be present in the pipeline YAML under the 'example' key.
    """
    name: str = Field(..., description="Name of this example instance")
    location: str = Field(..., description="Source code location (file/http/git)")
    message: str = Field(..., description="Message to use in commands")
    commands: List[ExampleCommand] = Field(default_factory=list, description="Commands to execute")
    execution_settings: Optional[dict] = Field(default_factory=dict, description="Override default execution settings")

class ExampleState(BaseModel):
    """Runtime state model for example extension"""
    container_id: Optional[str] = None
    mounted_paths: List[str] = Field(default_factory=list)
    env_vars: dict[str, str] = Field(default_factory=dict)
    current_command: Optional[str] = None
    results: List[str] = Field(default_factory=list)

class ExampleResult(BaseModel):
    """Result model for example extension execution"""
    success: bool
    message: str
    command_outputs: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list) 