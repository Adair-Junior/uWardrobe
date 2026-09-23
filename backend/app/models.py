from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class ClothingItem(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    category: str
    color: str
    style: str
    season: str
