from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SectionOut(BaseModel):
    id: int
    name: str
    book_count: int = 0


class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=120)
    version: str = Field(..., min_length=1, max_length=60)
    cost: float = Field(..., gt=0)
    section_id: int = Field(..., gt=0)
    total_copies: int = Field(..., ge=1)


class BookOut(BaseModel):
    id: int
    title: str
    author: str
    version: str
    cost: float
    total_copies: int
    available_copies: int
    status: str
    section_id: int
    section_name: str


class StockUpdate(BaseModel):
    added_copies: int = Field(..., ge=1)


class StudentCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=120)
    matric_number: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=5, max_length=200)
    department: Optional[str] = Field(default=None, max_length=120)


class StudentOut(BaseModel):
    id: int
    full_name: str
    matric_number: str
    email: str
    department: Optional[str]
    created_at: datetime
    active_borrows: int
    outstanding_fine: float


class BorrowCreate(BaseModel):
    student_id: int = Field(..., gt=0)
    book_id: int = Field(..., gt=0)
    lend_days: Optional[int] = Field(default=None, ge=1, le=30)


class BorrowOut(BaseModel):
    id: int
    student_id: int
    student_name: str
    matric_number: str
    book_id: int
    book_title: str
    section_name: str
    borrowed_at: datetime
    due_at: datetime
    lend_days: int
    returned_at: Optional[datetime]
    fine_amount: float
    outstanding_fine: float
    status: str


class DashboardOut(BaseModel):
    total_sections: int
    total_books: int
    available_books: int
    out_of_stock_books: int
    total_students: int
    active_borrows: int
    overdue_borrows: int
    total_fines_collected: float
    outstanding_fines: float
