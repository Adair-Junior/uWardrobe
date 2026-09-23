from fastapi import FastAPI, HTTPException
from backend.app.models import ClothingItem

app = FastAPI(
    title="uWardrobe API",
    description="Backend API for the uWardrobe application.",
    version="0.1.0",
)

wardrobe_items: list[ClothingItem] = []

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post ("/wardrobe")
def create_clothing_item(item: ClothingItem):
    wardrobe_items.append(item)
    return item

@app.get("/wardrobe")
def get_wardrobe():
    return wardrobe_items


@app.get("/wardrobe/{item_id}")
def get_clothing_item(item_id: str):
    for item in wardrobe_items:
        if str(item.id) == item_id:
            return item

    raise HTTPException(
        status_code=404,
        detail="Clothing item not found"
    )


@app.delete("/wardrobe/{item_id}")
def delete_clothing_item(item_id: str):
    for item in wardrobe_items:
        if str(item.id) == item_id:
            wardrobe_items.remove(item)
            return {"message": "Clothing item deleted"}


    raise HTTPException(
        status_code=404,
        detail="Clothing item not found"
    )


@app.put("/wardrobe/{item_id}")
def update_clothing_item(item_id: str, updated_item: ClothingItem):
    for index, item in enumerate(wardrobe_items):
        if str(item.id) == item_id:
            updated_item.id = item.id
            wardrobe_items[index] = updated_item
            return updated_item

    raise HTTPException(
        status_code=404,
        detail="Clothing item not found"
    )