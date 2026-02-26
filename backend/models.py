from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Section(Base):
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    books = relationship("Book", back_populates="section")


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    version = Column(String, nullable=False)
    cost = Column(Float, nullable=False)

    total_copies = Column(Integer, nullable=False)
    available_copies = Column(Integer, nullable=False)

    status = Column(String, default="AVAILABLE")

    section_id = Column(Integer, ForeignKey("sections.id"))
    section = relationship("Section", back_populates="books")

    borrows = relationship("BorrowRecord", back_populates="book")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

    borrows = relationship("BorrowRecord", back_populates="user")


class BorrowRecord(Base):
    __tablename__ = "borrow_records"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    book_id = Column(Integer, ForeignKey("books.id"))

    borrow_date = Column(Date)
    due_date = Column(Date)
    return_date = Column(Date, nullable=True)

    fine = Column(Float, default=0)

    user = relationship("User", back_populates="borrows")
    book = relationship("Book", back_populates="borrows")