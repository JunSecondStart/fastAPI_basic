from fastapi import FastAPI, Request, Depends, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
from typing import List, Optional, Any
from pydantic import BaseModel

app = FastAPI()

# テンプレートディレクトリの設定
templates = Jinja2Templates(directory="templates")

# SQLite3 データベース接続設定
SQLALCHEMY_DATABASE_URL = "sqlite:///./your_database_name.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    param1 = Column(Float, index=True)
    param2 = Column(Float, index=True)
    param3 = Column(Float, index=True)
    name = Column(String, index=True)

Base.metadata.create_all(bind=engine)

# Pydanticモデル
class ItemCreate(BaseModel):
    param1: float
    param2: float
    param3: float
    name: str

class ItemResponse(BaseModel):
    id: int
    param1: float
    param2: float
    param3: float
    name: str

    class Config:
        orm_mode = True
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/items/", response_class=HTMLResponse)
async def read_items(request: Request, id: Optional[int] = Query(None, description="Filter by id"), db: Session = Depends(get_db)) -> Any:
    if id is not None:
        items = db.query(Item).filter(Item.id == id).all()
    else:
        items = db.query(Item).all()
    
    if not items:
        raise HTTPException(status_code=404, detail="Items not found")

    items_response = [ItemResponse.from_orm(item).dict() for item in items]

    return templates.TemplateResponse(
            request=request,
            name="items.html",
            context={"items": items_response}
        )


@app.post("/items/", response_model=ItemResponse)
async def create_item(name:str ,param1: int, param2: int, param3: int, db: Session = Depends(get_db)) -> Any:
    db_item = Item(name=name, param1=param1, param2=param2, param3=param3)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return ItemResponse.from_orm(db_item)


@app.delete("/items/{item_id}", response_model=ItemResponse)
async def delete_item(
    item_id: int,
    db: Session = Depends(get_db)
) -> Any:
    item = db.query(Item).filter(Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()
    return ItemResponse.from_orm(item)

@app.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int,
    name: str,
    param1: int,
    param2: int,
    param3: int,
    db: Session = Depends(get_db)
) -> Any:
    item = db.query(Item).filter(Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    item.param1 = param1
    item.param2 = param2
    item.param3 = param3
    item.name = name

    db.commit()
    db.refresh(item)
    return ItemResponse.from_orm(item)


# サーバーの起動
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

