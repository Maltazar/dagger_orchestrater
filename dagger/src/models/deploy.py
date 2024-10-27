"""Class for the deploy_model module"""

from typing import List, Optional

from pydantic import BaseModel, Field


class Secret(BaseModel):
    name: str
    file: str


class Network(BaseModel):
    vlan: int
    ip_range: str = Field(alias="ip-range")


class TerraformVars(BaseModel):
    group: str
    name: str
    count: int
    cores: int
    memory: int
    disk: int
    network: List[Network]


class Terraform(BaseModel):
    name: str
    location: str
    pm_password: str
    pm_user: str
    target_node: str
    clone: str
    nameserver: str
    ssh_key: str
    disk_storage: str
    cloud_init_storage: str
    vars: List[TerraformVars]


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
