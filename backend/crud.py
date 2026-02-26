from sqlalchemy.orm import Session
from datetime import date, timedelta
from models import Book, BorrowRecord
from config import BORROW_DAYS, FINE_PER_DAY


def update_book_status(book: Book):
    if book.available_copies <= 0:
        book.status = "OUT_OF_STOCK"
        book.available_copies = 0
    else:
        book.status = "AVAILABLE"


def borrow_book(db: Session, user_id: int, book_id: int):

    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        raise Exception("Book not found")

    if book.available_copies <= 0:
        raise Exception("Book is out of stock")

    book.available_copies -= 1
    update_book_status(book)

    borrow = BorrowRecord(
        user_id=user_id,
        book_id=book_id,
        borrow_date=date.today(),
        due_date=date.today() + timedelta(days=BORROW_DAYS)
    )

    db.add(borrow)
    db.commit()
    db.refresh(borrow)

    return borrow


def return_book(db: Session, borrow_id: int):

    borrow = db.query(BorrowRecord).filter(
        BorrowRecord.id == borrow_id
    ).first()

    if not borrow:
        raise Exception("Borrow record not found")

    if borrow.return_date:
        raise Exception("Book already returned")

    borrow.return_date = date.today()

    # Fine calculation
    if borrow.return_date > borrow.due_date:
        days_late = (borrow.return_date - borrow.due_date).days
        borrow.fine = days_late * FINE_PER_DAY

    book = borrow.book
    book.available_copies += 1
    update_book_status(book)

    db.commit()
    db.refresh(borrow)

    return borrow