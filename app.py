from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
from typing import List, Optional
from pydantic import BaseModel


app = FastAPI()

#sqlite3
SQLALCHEMY_DATABASE_URL = "sqlite:///./your_database_name.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# CORSの設定
origins = [
    "http://localhost:3000",  # Reactアプリケーションがホストされているオリジン
    # 必要に応じて他のオリジンも追加可能
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    param1 = Column(Float, index=True)
    param2 = Column(Float, index=True)
    param3 = Column(Float, index=True)
    name = Column(String, index=True)

Base.metadata.create_all(bind=engine)


# Pydanticモデル
class ItemResponse(BaseModel):
    id: int
    param1: float
    param2: float
    param3: float
    name: str

    class Config:
        orm_mode = True



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# @app.get("/items/", response_model=List[ItemResponse])
@app.get("/fastAPI_sample/items/", response_model=List[ItemResponse])
async def read_items(id: Optional[int] = Query(None, description="Filter by id"),db: Session = Depends(get_db)):
    if id is not None:
        items = db.query(Item).filter(Item.id == id).all()
    else:
        items = db.query(Item).all()
    return items
    
    if not items:
        raise HTTPException(status_code=404, detail="Items not found")

    return items

# サーバーの起動
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

