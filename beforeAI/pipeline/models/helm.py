from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class HelmModule(BaseModel):
    name: str
    chart: str
    values_git: Optional[List[str]] = Field(alias="values-git", default=None)
    values: Optional[List[Dict[str, Any]]] = None
    set: Optional[List[Dict[str, Any]]] = None
