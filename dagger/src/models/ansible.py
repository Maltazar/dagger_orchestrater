from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class Hosts(BaseModel):
    group: str

class AnsibleInventory(BaseModel):
    hosts: List[Hosts]
    vars: Optional[List[dict]] = None

class AnsibleVar(BaseModel):
    key: str
    value: str

class AnsibleModule(BaseModel):
    name: str
    location: str
    play: str
    inventory: Dict[str, Any]
    vars: List[Dict[str, Any]]