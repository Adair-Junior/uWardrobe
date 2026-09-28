from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class ClothingItem(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    category: str
    color: str
    style: str
    season: str

class UserCreate(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: UUID
    email: str 

class UserLogin(BaseModel):
    email: str
    password: str

class Outfit(BaseModel):
    name: str
    item_ids: list[str] = []