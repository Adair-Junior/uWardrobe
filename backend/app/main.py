from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session 
from backend.app.models import ClothingItem, UserCreate, UserResponse, UserLogin, Outfit, StyleProfile 
from backend.app.database import engine, Base, get_db
from backend.app import db_models 
from backend.app.db_models import ClothingItemDB, OutfitDB, OutfitItemDB, StyleProfileDB
from backend.app.db_models import UserDB
from backend.app.security import (
    hash_password, 
    verify_password,
    create_access_token,
    decode_access_token,
)
from uuid import uuid4

Base.metadata.create_all(bind=engine)

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user_id = decode_access_token(credentials.credentials)

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )

    db_user = (
        db.query(UserDB)
        .filter(UserDB.id == user_id)
        .first()
    )

    if db_user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    return db_user

app = FastAPI(
    title="uWardrobe API",
    description="Backend API for the uWardrobe application.",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/user/register", response_model=UserResponse, status_code=201)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(UserDB)
        .filter(UserDB.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    db_user = UserDB(
        id=str(uuid4()),
        email=user.email,
        hashed_password=hash_password(user.password),
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

@app.post("/user/login")
def login_user(
    user: UserLogin,
    db: Session = Depends(get_db),
):
    db_user = (
        db.query(UserDB)
        .filter(UserDB.email == user.email)
        .first()
    )

    if not db_user or not verify_password(
        user.password,
        db_user.hashed_password,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    access_token = create_access_token(db_user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@app.get("/user/me", response_model=UserResponse)
def get_me(
    current_user: UserDB = Depends(get_current_user),
):
    return current_user

@app.post("/wardrobe")
def create_clothing_item(
    item: ClothingItem,
    db: Session = Depends(get_db),
    current_user: UserDb = Depends(get_current_user)
):

    db_item = ClothingItemDB(
        id=str(item.id),
        user_id=current_user.id,
        name=item.name,
        category=item.category,
        color=item.color,
        style=item.style,
        season=item.season,
    )

    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item 
    

@app.get("/wardrobe")
def get_wardrobe(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    items = (
        db.query(ClothingItemDB)
        .filter(ClothingItemDB.user_id == current_user.id)
        .all()
    )

    return items


@app.get("/wardrobe/{item_id}")
def get_clothing_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    db_item = (
        db.query(ClothingItemDB)
        .filter(
        ClothingItemDB.id == item_id,
        ClothingItemDB.user_id == current_user.id,
        )
    .first()
    )

    if db_item is None:
        raise HTTPException(
            status_code=404,
            detail="Clothing item not found"
        )

    return db_item


@app.delete("/wardrobe/{item_id}")
def delete_clothing_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    db_item = (
        db.query(ClothingItemDB)
        .filter(
            ClothingItemDB.id == item_id,
            ClothingItemDB.user_id == current_user.id,
        )
        .first()
    )


    if db_item is None:
        raise HTTPException(
            status_code=404,
            detail="Clothing item not found"
        )

    db.query(OutfitItemDB).filter(
        OutfitItemDB.clothing_item_id == db_item.id
    ).delete()

    db.delete(db_item)
    db.commit()

    return {"message": "Clothing item deleted"}


@app.put("/wardrobe/{item_id}")
def update_clothing_item(
    item_id: str,
    item: ClothingItem,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):

    db_item = (
        db.query(ClothingItemDB)
        .filter(
            ClothingItemDB.id == item_id,
            ClothingItemDB.user_id == current_user.id,
        )
        .first()
    )

    if db_item is None:
        raise HTTPException(
            status_code=404,
            detail="Clothing item not found"
        )

    db_item.name = item.name
    db_item.category = item.category
    db_item.color = item.color
    db_item.style = item.style
    db_item.season = item.season

    db.commit()
    db.refresh(db_item)

    return db_item

@app.post("/outfits", status_code=201)
def create_outfit(
    outfit: Outfit,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):

    if len(outfit.item_ids) != len(set(outfit.item_ids)):
        raise HTTPException(
            status_code=400,
            detail="Duplicate clothing items are not allowed",
        )
    
    db_outfit = OutfitDB(
        id=str(uuid4()),
        name=outfit.name,
        owner_id=current_user.id,
    )

    db.add(db_outfit)
    db.flush()

    saved_item_ids = []

    for item_id in outfit.item_ids:
        clothing_item = (
            db.query(ClothingItemDB)
            .filter(
                ClothingItemDB.id == item_id,
                ClothingItemDB.user_id == current_user.id,
            )
            .first()
        )

        if clothing_item is None:
            raise HTTPException(
                status_code=404,
                detail="Clothing item not found",
            )

        outfit_item = OutfitItemDB(
            id=str(uuid4()),
            outfit_id=db_outfit.id,
            clothing_item_id=clothing_item.id,
        )

        db.add(outfit_item)
        saved_item_ids.append(clothing_item.id)

    db.commit()
    db.refresh(db_outfit)

    return {
        "id": db_outfit.id,
        "name": db_outfit.name,
        "item_ids": saved_item_ids,
    }

@app.get("/outfits")
def get_outfits(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    outfits = (
        db.query(OutfitDB)
        .filter(OutfitDB.owner_id == current_user.id)
        .all()
    )

    result = []

    for outfit in outfits:
        outfit_items = (
            db.query(OutfitItemDB)
            .filter(OutfitItemDB.outfit_id == outfit.id)
            .all()
        )

        result.append(
            {
                "id": outfit.id,
                "name": outfit.name,
                "item_ids": [
                    outfit_item.clothing_item_id
                    for outfit_item in outfit_items
                ],
            }
        )

    return result

@app.get("/outfits/{outfit_id}")
def get_outfit(
    outfit_id: str,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    outfit = (
        db.query(OutfitDB)
        .filter(
            OutfitDB.id == outfit_id,
            OutfitDB.owner_id == current_user.id,
        )
        .first()
    )

    if outfit is None:
        raise HTTPException(
            status_code=404,
            detail="Outfit not found",
        )

    outfit_items = (
        db.query(OutfitItemDB)
        .filter(OutfitItemDB.outfit_id == outfit.id)
        .all()
    )

    return {
        "id": outfit.id,
        "name": outfit.name,
        "item_ids": [
            outfit_item.clothing_item_id
            for outfit_item in outfit_items
        ],
    }

@app.delete("/outfits/{outfit_id}", status_code=204)
def delete_outfit(
    outfit_id: str,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    outfit = (
        db.query(OutfitDB)
        .filter(
            OutfitDB.id == outfit_id,
            OutfitDB.owner_id == current_user.id,
        )
        .first()
    )

    if outfit is None:
        raise HTTPException(
            status_code=404,
            detail="Outfit not found",
        )

    db.query(OutfitItemDB).filter(
        OutfitItemDB.outfit_id == outfit.id
    ). delete()
    
    db.delete(outfit)
    db.commit()

    return None

@app.put("/outfits/{outfit_id}")
def update_outfit(
    outfit_id: str,
    updated_outfit: Outfit,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    if len(updated_outfit.item_ids) != len(set(updated_outfit.item_ids)):
        raise HTTPException(
            status_code=400,
            detail="Duplicate clothing items are not allowed",
        )
    
    outfit = (
        db.query(OutfitDB)
        .filter(
            OutfitDB.id == outfit_id,
            OutfitDB.owner_id == current_user.id,
        )
        .first()
    )

    if outfit is None:
        raise HTTPException(
            status_code=404,
            detail="Outfit not found",
        )

    # Validate all wardrobe items first
    clothing_items = []

    for item_id in updated_outfit.item_ids:
        clothing_item = (
            db.query(ClothingItemDB)
            .filter(
                ClothingItemDB.id == item_id,
                ClothingItemDB.user_id == current_user.id,
            )
            .first()
        )

        if clothing_item is None:
            raise HTTPException(
                status_code=404,
                detail="Clothing item not found",
            )

        clothing_items.append(clothing_item)

    # Update outfit name
    outfit.name = updated_outfit.name

    # Remove old item relationships
    db.query(OutfitItemDB).filter(
        OutfitItemDB.outfit_id == outfit.id
    ).delete()

    # Create the new relationships
    for clothing_item in clothing_items:
        outfit_item = OutfitItemDB(
            id=str(uuid4()),
            outfit_id=outfit.id,
            clothing_item_id=clothing_item.id,
        )

        db.add(outfit_item)

    db.commit()
    db.refresh(outfit)

    return {
        "id": outfit.id,
        "name": outfit.name,
        "item_ids": [
            clothing_item.id
            for clothing_item in clothing_items
        ],
    }

@app.post("/profile/style", status_code=201)
def create_style_profile(
    profile: StyleProfile,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    existing_profile = (
        db.query(StyleProfileDB)
        .filter(StyleProfileDB.user_id == current_user.id)
        .first()
    )

    if existing_profile:
        raise HTTPException(
            status_code=400,
            detail="Style profile already exists",
        )

    db_profile = StyleProfileDB(
        id=str(uuid4()),
        user_id=current_user.id,
        preferred_styles=",".join(profile.preferred_styles),
        preferred_colors=",".join(profile.preferred_colors),
        avoided_colors=",".join(profile.avoided_colors),
        top_size=profile.top_size,
        bottom_size=profile.bottom_size,
        shoe_size=profile.shoe_size,
        preferred_fit=profile.preferred_fit,
        preferred_occasions=",".join(profile.preferred_occasions),
    )

    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)

    return {
        "preferred_styles": profile.preferred_styles,
        "preferred_colors": profile.preferred_colors,
        "avoided_colors": profile.avoided_colors,
        "top_size": profile.top_size,
        "bottom_size": profile.bottom_size,
        "shoe_size": profile.shoe_size,
        "preferred_fit": profile.preferred_fit,
        "preferred_occasions": profile.preferred_occasions,
    }

@app.get("/profile/style")
def get_style_profile(
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_profile = (
        db.query(StyleProfileDB)
        .filter(StyleProfileDB.user_id == current_user.id)
        .first()
    )

    if not db_profile:
        raise HTTPException(
            status_code=404,
            detail="Style profile not found",
        )

    return {
        "preferred_styles": (
            db_profile.preferred_styles.split(",")
            if db_profile.preferred_styles
            else []
        ),
        "preferred_colors": (
            db_profile.preferred_colors.split(",")
            if db_profile.preferred_colors
            else []
        ),
        "avoided_colors": (
            db_profile.avoided_colors.split(",")
            if db_profile.avoided_colors
            else []
        ),
        "top_size": db_profile.top_size,
        "bottom_size": db_profile.bottom_size,
        "shoe_size": db_profile.shoe_size,
        "preferred_fit": db_profile.preferred_fit,
        "preferred_occasions": (
            db_profile.preferred_occasions.split(",")
            if db_profile.preferred_occasions
            else []
        ),
    }

@app.put("/profile/style")
def update_style_profile(
    profile: StyleProfile,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_profile = (
        db.query(StyleProfileDB)
        .filter(StyleProfileDB.user_id == current_user.id)
        .first()
    )

    if not db_profile:
        raise HTTPException(
            status_code=404,
            detail="Style profile not found",
        )

    db_profile.preferred_styles = ",".join(profile.preferred_styles)
    db_profile.preferred_colors = ",".join(profile.preferred_colors)
    db_profile.avoided_colors = ",".join(profile.avoided_colors)
    db_profile.top_size = profile.top_size
    db_profile.bottom_size = profile.bottom_size
    db_profile.shoe_size = profile.shoe_size
    db_profile.preferred_fit = profile.preferred_fit
    db_profile.preferred_occasions = ",".join(profile.preferred_occasions)

    db.commit()
    db.refresh(db_profile)

    return {
        "preferred_styles": profile.preferred_styles,
        "preferred_colors": profile.preferred_colors,
        "avoided_colors": profile.avoided_colors,
        "top_size": profile.top_size,
        "bottom_size": profile.bottom_size,
        "shoe_size": profile.shoe_size,
        "preferred_fit": profile.preferred_fit,
        "preferred_occasions": profile.preferred_occasions,
    }

@app.delete("/profile/style", status_code=204)
def delete_style_profile(
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_profile = (
        db.query(StyleProfileDB)
        .filter(StyleProfileDB.user_id == current_user.id)
        .first()
    )

    if not db_profile:
        raise HTTPException(
            status_code=404,
            detail="Style profile not found",
        )

    db.delete(db_profile)
    db.commit()

    return None