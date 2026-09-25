from sqlalchemy import Column, String
from backend.app.database import Base 

class ClothingItemDB(Base):
    __tablename__ = "clothing_items"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    color = Column(String, nullable=False)
    style = Column(String, nullable=False)
    season = Column(String, nullable=False)