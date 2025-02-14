from typing import List, Dict
from pydantic import BaseModel, Field
from pipeline.models.config import ModuleConfig

class NetworkConfig(BaseModel):
    vlan: int
    ip_range: str = Field(alias="ip-range")
    
    @field_validator("ip_range")
    @classmethod
    def validate_ip_range(cls, v: str) -> str:
        if not "-" in v:
            raise ValueError("IP range must be in format start-end")
        return v

class GroupConfig(BaseModel):
    group: str
    name: str
    count: int
    cores: int
    memory: int
    disk: int
    network: List[NetworkConfig]

class TerraformConfig(ModuleConfig):
    """Terraform module specific configuration"""
    name: str
    state_file: str = Field(alias="state_file")
    location: str
    vars: List[Dict[str, str]]
    groups: List[GroupConfig] 