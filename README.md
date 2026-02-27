# Library Management System

Full-stack library application built with FastAPI (backend) and Streamlit (frontend).

## Project Overview
This project helps a school library manage books, students, borrowing, returns, overdue tracking, and fines in one place.  
The FastAPI backend exposes REST endpoints for all library operations, while the Streamlit frontend provides a simple interface for librarians to use those features.

## Core Features
- Fixed section storage:
  - `SCIENCES`
  - `ARTS`
  - `SOCIALS`
  - `ECONOMICS`
  - `RELIGION`
  - `GENERAL STUDIES`
- Book inventory with:
  - `Title`, `Author`, `Version`, `Cost`, `Status`
  - total copies, available copies, out-of-stock updates
- Student records:
  - full name, matric number, email, department
- Borrow workflow:
  - student, book, borrow datetime, due datetime, lend days
- Return workflow:
  - return datetime and automatic fine calculation
- Defaulter tracking:
  - overdue students and outstanding fines
- Fine rule:
  - `#500` per overdue day

## Project Structure
```
library-management-system/
|-- backend/
|   |-- __init__.py
|   |-- config.py
|   |-- database.py
|   |-- models.py
|   |-- schemas.py
|   |-- crud.py
|   |-- main.py
|   `-- init__db.py
|-- frontend/
|   `-- app.py
|-- requirements.txt
`-- README.md
```

## Getting Started (Clone to Run)
1. Clone the repository:
   - `git clone https://github.com/olaoluwaoyebola/library-management-system.git`
2. Move into the project folder:
   - `cd library-management-system`
3. Create and activate a virtual environment:
   - Windows (PowerShell): `python -m venv .venv` then `.venv\Scripts\Activate.ps1`
   - macOS/Linux: `python -m venv .venv` then `source .venv/bin/activate`
4. Install dependencies:
   - `pip install -r requirements.txt`
5. Initialize the database and seed the default sections:
   - `python -m backend.init__db`
6. Start the backend API (from project root):
   - `uvicorn backend.main:app --reload`
7. In a new terminal (same project root), start the frontend:
   - `streamlit run frontend/app.py`
8. Open the app:
   - Frontend: `http://localhost:8501`
   - API docs: `http://127.0.0.1:8000/docs`

## Main API Endpoints
- `GET /health`
- `GET /sections`
- `POST /sections/seed`
- `GET /books`
- `POST /books`
- `PATCH /books/{book_id}/stock`
- `GET /students`
- `POST /students`
- `GET /borrows`
- `POST /borrow`
- `POST /return/{borrow_id}`
- `GET /defaulters`
- `GET /dashboard`
