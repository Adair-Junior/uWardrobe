from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session 
from backend.app.models import ClothingItem, UserCreate, UserResponse, UserLogin
from backend.app.database import engine, Base, get_db
from backend.app import db_models 
from backend.app.db_models import ClothingItemDB
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