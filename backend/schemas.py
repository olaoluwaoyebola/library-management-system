from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date


# -----------------------------
# SECTION SCHEMAS
# -----------------------------

class SectionBase(BaseModel):
    name: str


class SectionOut(SectionBase):
    id: int

    class Config:
        orm_mode = True


# -----------------------------
# BOOK SCHEMAS
# -----------------------------

class BookBase(BaseModel):
    title: str
    author: str
    version: str
    cost: float
    section_id: int
    total_copies: int


class BookCreate(BookBase):
    pass


class BookOut(BookBase):
    id: int
    available_copies: int
    status: str

    class Config:
        orm_mode = True


# -----------------------------
# USER SCHEMAS
# -----------------------------

class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    pass


class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True


# -----------------------------
# BORROW SCHEMAS
# -----------------------------

class BorrowCreate(BaseModel):
    user_id: int
    book_id: int


class BorrowOut(BaseModel):
    id: int
    user_id: int
    book_id: int
    borrow_date: date
    due_date: date
    return_date: Optional[date]
    fine: float

    class Config:
        orm_mode = True