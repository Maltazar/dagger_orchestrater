"""Class for the deploy_model module"""

from typing import List, Optional

from pydantic import BaseModel, Field


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
    values: List[dict]


class Kubectl(BaseModel):
    apply: str
    files: List[str]


class Orchestrate(BaseModel):
    secrets: List[Secret]
    terraform: List[Terraform]
    ansible: List[Ansible]
    helm: List[Helm]
    kubectl: List[Kubectl]


class DeployModel(BaseModel):
    orchestrate: Orchestrate
