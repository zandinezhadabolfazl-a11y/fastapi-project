from typing import Annotated, Optional
from pydantic import BaseModel, StringConstraints, Field


class Post(BaseModel):
    title: Annotated[str, StringConstraints(min_length=5, max_length=15)]
    content: Optional[str] = None

class PostOut(Post):
    id: int
    user_id: int

    model_config = {"from_attributes": True}

class PostPatch(BaseModel):
    title: Annotated[Optional[str], StringConstraints(min_length=5, max_length=15)] = None
    content: Annotated[Optional[str], StringConstraints(min_length=5, max_length=15)] = None
