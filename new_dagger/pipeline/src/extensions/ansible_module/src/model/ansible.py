from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class HostGroup(BaseModel):
    group: str
    nodes: Optional[List[str]] = None

class AnsibleInventory(BaseModel):
    hosts: List[HostGroup]
    vars: Optional[Dict[str, Any]] = None

class AnsibleConfig(BaseModel):
    name: str
    location: str
    play: str
    inventory: AnsibleInventory 