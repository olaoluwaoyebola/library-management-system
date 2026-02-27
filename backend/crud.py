from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from backend.config import (
    DEFAULT_BORROW_DAYS,
    FINE_PER_DAY,
    LIBRARY_SECTIONS,
    MAX_BORROW_DAYS,
)
from backend.models import Book, BorrowRecord, Section, Student
from backend.schemas import BookCreate, BorrowCreate, StudentCreate


def ensure_sections(db: Session) -> None:
    """Seed required library sections if they do not already exist."""
    existing_names = {name for (name,) in db.query(Section.name).all()}
    missing = [Section(name=name) for name in LIBRARY_SECTIONS if name not in existing_names]
    if missing:
        db.add_all(missing)
        db.commit()


def _overdue_days(due_at: datetime, reference_time: datetime) -> int:
    if reference_time.date() <= due_at.date():
        return 0
    return (reference_time.date() - due_at.date()).days


def _update_book_status(book: Book) -> None:
    # Clamp copies so status and inventory cannot drift apart.
    if book.available_copies < 0:
        book.available_copies = 0
    if book.available_copies > book.total_copies:
        book.available_copies = book.total_copies
    book.status = "OUT_OF_STOCK" if book.available_copies == 0 else "AVAILABLE"


def _serialize_book(book: Book) -> Dict[str, Any]:
    return {
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "version": book.version,
        "cost": book.cost,
        "total_copies": book.total_copies,
        "available_copies": book.available_copies,
        "status": book.status,
        "section_id": book.section_id,
        "section_name": book.section.name if book.section else "",
    }


def _serialize_borrow(record: BorrowRecord, now: Optional[datetime] = None) -> Dict[str, Any]:
    now = now or datetime.now()
    is_returned = record.returned_at is not None
    is_overdue = (not is_returned) and (now > record.due_at)

    if is_returned:
        status_name = "RETURNED"
        outstanding_fine = float(record.fine_amount)
    elif is_overdue:
        status_name = "OVERDUE"
        outstanding_fine = float(_overdue_days(record.due_at, now) * FINE_PER_DAY)
    else:
        status_name = "BORROWED"
        outstanding_fine = 0.0

    return {
        "id": record.id,
        "student_id": record.student_id,
        "student_name": record.student.full_name if record.student else "",
        "matric_number": record.student.matric_number if record.student else "",
        "book_id": record.book_id,
        "book_title": record.book.title if record.book else "",
        "section_name": record.book.section.name if record.book and record.book.section else "",
        "borrowed_at": record.borrowed_at,
        "due_at": record.due_at,
        "lend_days": record.lend_days,
        "returned_at": record.returned_at,
        "fine_amount": float(record.fine_amount),
        "outstanding_fine": float(outstanding_fine),
        "status": status_name,
    }


def list_sections(db: Session) -> List[Dict[str, Any]]:
    rows = (
        db.query(
            Section.id.label("id"),
            Section.name.label("name"),
            func.count(Book.id).label("book_count"),
        )
        .outerjoin(Book, Book.section_id == Section.id)
        .group_by(Section.id, Section.name)
        .order_by(Section.name.asc())
        .all()
    )
    return [{"id": row.id, "name": row.name, "book_count": int(row.book_count)} for row in rows]


def list_books(
    db: Session,
    section_id: Optional[int] = None,
    include_out_of_stock: bool = True,
) -> List[Dict[str, Any]]:
    query = db.query(Book).options(joinedload(Book.section))
    if section_id is not None:
        query = query.filter(Book.section_id == section_id)
    if not include_out_of_stock:
        query = query.filter(Book.available_copies > 0)

    books = query.order_by(Book.title.asc()).all()
    return [_serialize_book(book) for book in books]


def create_book(db: Session, payload: BookCreate) -> Dict[str, Any]:
    section = db.query(Section).filter(Section.id == payload.section_id).first()
    if not section:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")

    existing = (
        db.query(Book)
        .filter(
            Book.title == payload.title.strip(),
            Book.author == payload.author.strip(),
            Book.version == payload.version.strip(),
            Book.section_id == payload.section_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This book/version already exists in the selected section",
        )

    book = Book(
        title=payload.title.strip(),
        author=payload.author.strip(),
        version=payload.version.strip(),
        cost=payload.cost,
        total_copies=payload.total_copies,
        available_copies=payload.total_copies,
        section_id=payload.section_id,
    )
    _update_book_status(book)

    db.add(book)
    db.commit()
    db.refresh(book)
    db.refresh(section)
    return _serialize_book(book)


def add_book_stock(db: Session, book_id: int, added_copies: int) -> Dict[str, Any]:
    book = db.query(Book).options(joinedload(Book.section)).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    book.total_copies += added_copies
    book.available_copies += added_copies
    _update_book_status(book)

    db.commit()
    db.refresh(book)
    return _serialize_book(book)


def _student_outstanding_fine(student: Student, now: datetime) -> float:
    outstanding = 0.0
    for borrow in student.borrows:
        if borrow.returned_at is None and now > borrow.due_at:
            outstanding += _overdue_days(borrow.due_at, now) * FINE_PER_DAY
    return float(outstanding)


def _serialize_student(student: Student, now: Optional[datetime] = None) -> Dict[str, Any]:
    now = now or datetime.now()
    active_borrows = sum(1 for borrow in student.borrows if borrow.returned_at is None)
    return {
        "id": student.id,
        "full_name": student.full_name,
        "matric_number": student.matric_number,
        "email": student.email,
        "department": student.department,
        "created_at": student.created_at,
        "active_borrows": active_borrows,
        "outstanding_fine": _student_outstanding_fine(student, now),
    }


def create_student(db: Session, payload: StudentCreate) -> Dict[str, Any]:
    existing = (
        db.query(Student)
        .filter(
            (Student.matric_number == payload.matric_number.strip())
            | (Student.email == payload.email.strip().lower())
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student with matric number or email already exists",
        )

    student = Student(
        full_name=payload.full_name.strip(),
        matric_number=payload.matric_number.strip().upper(),
        email=payload.email.strip().lower(),
        department=payload.department.strip() if payload.department else None,
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    student = db.query(Student).options(joinedload(Student.borrows)).filter(Student.id == student.id).first()
    return _serialize_student(student)


def list_students(db: Session) -> List[Dict[str, Any]]:
    students = (
        db.query(Student)
        .options(joinedload(Student.borrows))
        .order_by(Student.full_name.asc())
        .all()
    )
    now = datetime.now()
    return [_serialize_student(student, now=now) for student in students]


def borrow_book(db: Session, payload: BorrowCreate) -> Dict[str, Any]:
    lend_days = payload.lend_days or DEFAULT_BORROW_DAYS
    if lend_days < 1 or lend_days > MAX_BORROW_DAYS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"lend_days must be between 1 and {MAX_BORROW_DAYS}",
        )

    student = db.query(Student).filter(Student.id == payload.student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    book = db.query(Book).options(joinedload(Book.section)).filter(Book.id == payload.book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    if book.available_copies <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book is out of stock")

    already_borrowed = (
        db.query(BorrowRecord)
        .filter(
            BorrowRecord.student_id == payload.student_id,
            BorrowRecord.book_id == payload.book_id,
            BorrowRecord.returned_at.is_(None),
        )
        .first()
    )
    if already_borrowed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student already has this book and has not returned it",
        )

    borrowed_at = datetime.now()
    borrow_record = BorrowRecord(
        student_id=payload.student_id,
        book_id=payload.book_id,
        borrowed_at=borrowed_at,
        due_at=borrowed_at + timedelta(days=lend_days),
        lend_days=lend_days,
    )

    book.available_copies -= 1
    _update_book_status(book)

    db.add(borrow_record)
    db.commit()
    db.refresh(borrow_record)

    borrow_record = (
        db.query(BorrowRecord)
        .options(
            joinedload(BorrowRecord.student),
            joinedload(BorrowRecord.book).joinedload(Book.section),
        )
        .filter(BorrowRecord.id == borrow_record.id)
        .first()
    )
    return _serialize_borrow(borrow_record)


def return_book(db: Session, borrow_id: int) -> Dict[str, Any]:
    borrow_record = (
        db.query(BorrowRecord)
        .options(
            joinedload(BorrowRecord.student),
            joinedload(BorrowRecord.book).joinedload(Book.section),
        )
        .filter(BorrowRecord.id == borrow_id)
        .first()
    )
    if not borrow_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Borrow record not found")
    if borrow_record.returned_at is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Book already returned")

    returned_at = datetime.now()
    overdue_days = _overdue_days(borrow_record.due_at, returned_at)

    borrow_record.returned_at = returned_at
    borrow_record.fine_amount = float(overdue_days * FINE_PER_DAY)

    book = borrow_record.book
    book.available_copies += 1
    _update_book_status(book)

    db.commit()
    db.refresh(borrow_record)

    borrow_record = (
        db.query(BorrowRecord)
        .options(
            joinedload(BorrowRecord.student),
            joinedload(BorrowRecord.book).joinedload(Book.section),
        )
        .filter(BorrowRecord.id == borrow_id)
        .first()
    )
    return _serialize_borrow(borrow_record, now=returned_at)


def list_borrows(
    db: Session,
    only_active: bool = False,
    only_overdue: bool = False,
) -> List[Dict[str, Any]]:
    query = (
        db.query(BorrowRecord)
        .options(
            joinedload(BorrowRecord.student),
            joinedload(BorrowRecord.book).joinedload(Book.section),
        )
        .order_by(BorrowRecord.borrowed_at.desc())
    )

    now = datetime.now()
    if only_active:
        query = query.filter(BorrowRecord.returned_at.is_(None))
    if only_overdue:
        query = query.filter(BorrowRecord.returned_at.is_(None), BorrowRecord.due_at < now)

    records = query.all()
    return [_serialize_borrow(record, now=now) for record in records]


def list_defaulters(db: Session) -> List[Dict[str, Any]]:
    # Defaulters are currently overdue borrow records not yet returned.
    return list_borrows(db, only_active=True, only_overdue=True)


def dashboard_summary(db: Session) -> Dict[str, Any]:
    now = datetime.now()

    total_sections = db.query(func.count(Section.id)).scalar() or 0
    total_books = db.query(func.count(Book.id)).scalar() or 0
    available_books = db.query(func.coalesce(func.sum(Book.available_copies), 0)).scalar() or 0
    out_of_stock_books = db.query(func.count(Book.id)).filter(Book.available_copies <= 0).scalar() or 0
    total_students = db.query(func.count(Student.id)).scalar() or 0
    active_borrows = (
        db.query(func.count(BorrowRecord.id))
        .filter(BorrowRecord.returned_at.is_(None))
        .scalar()
        or 0
    )
    overdue_borrows = (
        db.query(func.count(BorrowRecord.id))
        .filter(BorrowRecord.returned_at.is_(None), BorrowRecord.due_at < now)
        .scalar()
        or 0
    )
    total_fines_collected = (
        db.query(func.coalesce(func.sum(BorrowRecord.fine_amount), 0.0))
        .filter(BorrowRecord.returned_at.isnot(None))
        .scalar()
        or 0.0
    )

    overdue_records = (
        db.query(BorrowRecord)
        .filter(BorrowRecord.returned_at.is_(None), BorrowRecord.due_at < now)
        .all()
    )
    outstanding_fines = sum(_overdue_days(record.due_at, now) * FINE_PER_DAY for record in overdue_records)

    return {
        "total_sections": int(total_sections),
        "total_books": int(total_books),
        "available_books": int(available_books),
        "out_of_stock_books": int(out_of_stock_books),
        "total_students": int(total_students),
        "active_borrows": int(active_borrows),
        "overdue_borrows": int(overdue_borrows),
        "total_fines_collected": float(total_fines_collected),
        "outstanding_fines": float(outstanding_fines),
    }
