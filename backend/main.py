from typing import List, Optional

from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend import crud, schemas
from backend.database import Base, SessionLocal, engine

app = FastAPI(
    title="Library Management API",
    version="1.0.0",
    description="API for sections, books, students, borrowing, returns, and overdue fines.",
)

# Allow local Streamlit app to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        crud.ensure_sections(db)
    finally:
        db.close()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/sections", response_model=List[schemas.SectionOut])
def get_sections(db: Session = Depends(get_db)):
    return crud.list_sections(db)


@app.post("/sections/seed", response_model=List[schemas.SectionOut])
def seed_sections(db: Session = Depends(get_db)):
    crud.ensure_sections(db)
    return crud.list_sections(db)


@app.get("/books", response_model=List[schemas.BookOut])
def get_books(
    section_id: Optional[int] = Query(default=None, gt=0),
    include_out_of_stock: bool = True,
    db: Session = Depends(get_db),
):
    return crud.list_books(db, section_id=section_id, include_out_of_stock=include_out_of_stock)


@app.post("/books", response_model=schemas.BookOut)
def create_book(payload: schemas.BookCreate, db: Session = Depends(get_db)):
    return crud.create_book(db, payload)


@app.patch("/books/{book_id}/stock", response_model=schemas.BookOut)
def restock_book(book_id: int, payload: schemas.StockUpdate, db: Session = Depends(get_db)):
    return crud.add_book_stock(db, book_id, payload.added_copies)


@app.get("/students", response_model=List[schemas.StudentOut])
def get_students(db: Session = Depends(get_db)):
    return crud.list_students(db)


@app.post("/students", response_model=schemas.StudentOut)
def create_student(payload: schemas.StudentCreate, db: Session = Depends(get_db)):
    return crud.create_student(db, payload)


@app.get("/borrows", response_model=List[schemas.BorrowOut])
def get_borrows(
    only_active: bool = False,
    only_overdue: bool = False,
    db: Session = Depends(get_db),
):
    return crud.list_borrows(db, only_active=only_active, only_overdue=only_overdue)


@app.post("/borrow", response_model=schemas.BorrowOut)
def borrow(payload: schemas.BorrowCreate, db: Session = Depends(get_db)):
    return crud.borrow_book(db, payload)


@app.post("/return/{borrow_id}", response_model=schemas.BorrowOut)
def return_book(borrow_id: int, db: Session = Depends(get_db)):
    return crud.return_book(db, borrow_id)


@app.get("/defaulters", response_model=List[schemas.BorrowOut])
def get_defaulters(db: Session = Depends(get_db)):
    return crud.list_defaulters(db)


@app.get("/dashboard", response_model=schemas.DashboardOut)
def get_dashboard(db: Session = Depends(get_db)):
    return crud.dashboard_summary(db)
