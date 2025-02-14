from typing import List
from pydantic import BaseModel

class ModuleDependencies(BaseModel):
    """Module dependency configuration"""
    requires: List[str] | None = None
    provides: List[str] | None = None
    conflicts: List[str] | None = None 