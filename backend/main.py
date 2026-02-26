from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
import crud, schemas

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/borrow", response_model=schemas.BorrowOut)
def borrow(data: schemas.BorrowCreate, db: Session = Depends(get_db)):
    return crud.borrow_book(db, data.user_id, data.book_id)


@app.post("/return/{borrow_id}", response_model=schemas.BorrowOut)
def return_book(borrow_id: int, db: Session = Depends(get_db)):
    return crud.return_book(db, borrow_id)