"""Class for the deploy_model module"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, RootModel


class Secret(BaseModel):
    name: str
    location: str


class Network(BaseModel):
    vlan: int
    ip_range: str = Field(alias="ip-range")


class Terraform(BaseModel):
    name: str
    location: str
    vars: List[dict]


class Hosts(BaseModel):
    group: str


class AnsibleInventory(BaseModel):
    hosts: List[Hosts]
    vars: Optional[List[dict]] = None


class Ansible(BaseModel):
    name: str
    location: str
    play: str
    inventory: AnsibleInventory


class Helm(BaseModel):
    name: str
    chart: str
    set: Optional[List[dict]] = None
    values: Optional[List[dict]] = None
    values_git: Optional[List[str]] = None


class Kubectl(BaseModel):
    apply: str
    files: List[str]


class Modules(BaseModel):
    secrets: Optional[List[Secret]]
    terraform: Optional[List[Terraform]]
    ansible: Optional[List[Ansible]]
    helm: Optional[List[Helm]]
    kubectl: Optional[List[Kubectl]]


class Orchestrate(RootModel):
    root: Dict[str, Modules]  # This allows for a dynamic first-level key name
