from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional

#import sql alchemy models
from app.model import Item as DBItem # alias to avoid name clashing with 
# pydantic models
from app.database import get_db, engine, create_db_and_tables

# SQLAlchemy imports for querying
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete

# Lifespan context manager
async def lifespan(app: FastAPI):
    """
    Handles the application startup and shutdown events.
    Ensures databases are created on startup and connections are
    closed and shutdown.
    """
    print("FastAPI application starting up...")
    # startup event: create db tables
    await create_db_and_tables()
    print("Database and tables ensured")
    yield # application will run at this point
    print("Fast application shutting down...")
    # shutdown event: Close database engine connection pool
    await engine.dispose()
    print("Database connection close")

# intialize fastAPI with lifespan handler
app = FastAPI(lifespan=lifespan)

class ItemModel(BaseModel):
    id: Optional[int] = None # id is optional for creation but required for retrieval
    text: str
    is_done: bool = None

    class Config:
        # tells pydantic to convert sql alchemy orm objects into pydantic models
        # when returning data from your API
        from_attributes = True

# FAST API ENDPOINTS

@app.get("/")
def root():
        return {"Hello" : "World"}

@app.post("/items", response_model=ItemModel)
async def create_item(item: ItemModel, db: AsyncSession = Depends(get_db)):
    """Creates a new item in the database"""
    db_item = DBItem(text=item.text, is_done=item.is_done)
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item

@app.get("/items", response_model=list[ItemModel])
async def list_items(limit: int = 10, db: AsyncSession = Depends(get_db)):
    """Retrieves list of items from a database"""
    result = await db.execute(select(DBItem).limit(limit))
    items = result.scalars().all()
    return items

@app.get("/items/{item_id}", response_model=ItemModel)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieves single item by its ID from the database"""
    result = await db.execute(select(DBItem).where(DBItem.id==item_id))
    item = result.scalars().first()
    if item is None:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found.")
    return item

@app.delete("/items/{item_id}")
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """Deletes any item by its ID in the database"""
    result = await db.execute(select(DBItem).where(DBItem.id == item_id))
    item = result.scalars().first()
    if item is None:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found.")
    await db.delete(item)
    await db.commit()
    return {"message" : f"Item: {item_id} delete successfully."}

@app.put("/items/{item_id}", response_model=ItemModel)
async def update_item(item_id: int, item_update: ItemModel, db: AsyncSession = Depends(get_db)):
    """Updates an existing item by its ID in the database"""
    result = await db.execute(select(DBItem).where(DBItem.id == item_id))
    db_item = result.scalars().first()
    if DBItem is None:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found.")
    
    db_item.text = item_update.text # this is required
    if item_update.is_done is not None: # optional, hence why theres checking
        db_item.text = item_update.text

    await db.commit()
    await db.refresh(db_item)
    return db.item