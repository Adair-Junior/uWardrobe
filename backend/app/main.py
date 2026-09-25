from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session 
from backend.app.models import ClothingItem
from backend.app.database import engine, Base, get_db
from backend.app import db_models 
from backend.app.db_models import ClothingItemDB

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="uWardrobe API",
    description="Backend API for the uWardrobe application.",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/wardrobe")
def create_clothing_item(
    item: ClothingItem,
    db: Session = Depends(get_db)
):

    db_item = ClothingItemDB(
        id=str(item.id),
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
    db: Session = Depends(get_db)
):

    return db.query(ClothingItemDB).all()


@app.get("/wardrobe/{item_id}")
def get_clothing_item(
    item_id: str,
    db: Session = Depends(get_db)
):
    db_item = db.query(ClothingItemDB).filter(
        ClothingItemDB.id == item_id
    ).first()

    if db_item is None:
        raise HTTPException(
            status_code=404,
            detail="Clothing item not found"
        )

    return db_item


@app.delete("/wardrobe/{item_id}")
def delete_clothing_item(
    item_id: str,
    db: Session = Depends(get_db)
):
    db_item = db.query(ClothingItemDB).filter(
        ClothingItemDB.id == item_id
    ).first()


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
    updated_item: ClothingItem,
    db: Session = Depends(get_db)
):

    db_item = db.query(ClothingItemDB).filter(
        ClothingItemDB.id == item_id
    ).first()

    if db_item is None:
        raise HTTPException(
            status_code=404,
            detail="Clothing item not found"
        )

    db_item.name = updated_item.name
    db_item.category = updated_item.category
    db_item.color = updated_item.color
    db_item.style = updated_item.style
    db_item.season = updated_item.season

    db.commit()
    db.refresh(db_item)

    return db_item