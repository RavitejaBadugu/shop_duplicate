from pydantic import BaseModel
from typing import List,Optional

class Find_Input_Schema(BaseModel):
    title: str
    image: List[int]

class Find_Output_Schema(BaseModel):
    titles: Optional[List[str]] = None
    images: Optional[List[List[int]]] = None