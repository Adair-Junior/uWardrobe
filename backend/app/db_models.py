from sqlalchemy import Column, String, ForeignKey
from backend.app.database import Base 

class ClothingItemDB(Base):
    __tablename__ = "clothing_items"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    color = Column(String, nullable=False)
    style = Column(String, nullable=False)
    season = Column(String, nullable=False)

class UserDB(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

class OutfitDB(Base):
    __tablename__ = "outfits"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

class OutfitItemDB(Base):
    __tablename__ = "outfit_items"

    id = Column(String, primary_key=True, index=True)
    outfit_id = Column(
        String,
        ForeignKey("outfits.id"),
        nullable=False,
        index=True,
    )
    clothing_item_id = Column(
        String,
        ForeignKey("clothing_items.id"),
        nullable=False,
        index=True,
    )

class StyleProfileDB(Base):
    __tablename__ = "style_profiles"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(
        String,
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
        index=True,
    )
    preferred_styles = Column(String, nullable=True)
    preferred_colors = Column(String, nullable=True)
    avoided_colors = Column(String, nullable=True)