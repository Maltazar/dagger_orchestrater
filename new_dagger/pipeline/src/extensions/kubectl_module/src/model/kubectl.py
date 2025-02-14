from typing import List
from pydantic import BaseModel

class KubectlConfig(BaseModel):
    apply: str
    files: List[str] 