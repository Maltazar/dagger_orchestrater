from typing import List
from pydantic import BaseModel


class KubectlModule(BaseModel):
    apply: str
    files: List[str]