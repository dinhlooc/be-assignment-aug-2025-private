from pydantic import BaseModel, Field
from typing import Annotated
class OrganizationCreateRequest(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=100)]