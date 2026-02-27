from datetime import datetime
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from backend.database import Base

class Section(Base):
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    books = relationship("Book", back_populates="section", cascade="all, delete-orphan")


class Book(Base):
    __tablename__ = "books"
    __table_args__ = (
        UniqueConstraint("title", "author", "version", "section_id", name="uq_book_identity"),
    )

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    version = Column(String, nullable=False)
    cost = Column(Float, nullable=False)

    total_copies = Column(Integer, nullable=False)
    available_copies = Column(Integer, nullable=False)

    status = Column(String, default="AVAILABLE")

    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)
    section = relationship("Section", back_populates="books")

    borrows = relationship("BorrowRecord", back_populates="book", cascade="all, delete-orphan")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    matric_number = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    department = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    borrows = relationship("BorrowRecord", back_populates="student")


class BorrowRecord(Base):
    __tablename__ = "borrow_records"

    id = Column(Integer, primary_key=True)

    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)

    borrowed_at = Column(DateTime, default=datetime.now, nullable=False)
    due_at = Column(DateTime, nullable=False)
    lend_days = Column(Integer, nullable=False)
    returned_at = Column(DateTime, nullable=True)

    fine_amount = Column(Float, default=0.0, nullable=False)

    student = relationship("Student", back_populates="borrows")
    book = relationship("Book", back_populates="borrows")
