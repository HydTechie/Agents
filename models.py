from pydantic import BaseModel
from typing import List, Optional

class Step(BaseModel):
    action: str
    condition: Optional[str] = None

class Flow(BaseModel):
    name: str
    steps: List[Step]
