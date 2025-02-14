"""Class for the deploy_model module"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field, RootModel
from models.terraform import TerraformModule
from models.ansible import AnsibleModule
from models.helm import HelmModule
from models.kubectl import KubectlModule
from models.secret import SecretModel




class Modules(BaseModel):
    secrets: Optional[List[SecretModel]]
    terraform: Optional[List[TerraformModule]]
    ansible: Optional[List[AnsibleModule]]
    helm: Optional[List[HelmModule]]
    kubectl: Optional[List[KubectlModule]]


class Orchestrate(RootModel):
    root: Dict[str, Modules]  # This allows for a dynamic first-level key name
