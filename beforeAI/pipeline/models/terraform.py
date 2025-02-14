from typing import Any, List, Dict
from pydantic import BaseModel, Field

class TerraformVar(BaseModel):
    key: str
    value: str

class Network(BaseModel):
    vlan: int
    ip_range: str = Field(alias="ip-range")

class TerraformGroup(BaseModel):
    name: str
    count: int
    cores: int
    memory: int
    disk: int
    network: List[Dict[str, Any]]

class TerraformModule(BaseModel):
    name: str
    location: str
    state_file: str = Field(alias="state-file")
    vars: List[Dict[str, Any]]
