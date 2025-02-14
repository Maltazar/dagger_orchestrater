from typing import List
from pydantic import BaseModel, Field

class NetworkConfig(BaseModel):
    vlan: int
    ip_range: str = Field(alias="ip-range")

class GroupConfig(BaseModel):
    group: str
    name: str
    count: int
    cores: int
    memory: int
    disk: int
    network: List[NetworkConfig]

class TerraformConfig(BaseModel):
    name: str
    state_file: str = Field(alias="state_file")
    location: str
    vars: List[dict]
    groups: List[GroupConfig] 