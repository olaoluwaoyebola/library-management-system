# Library Management System

Full-stack library application built with FastAPI (backend) and Streamlit (frontend).

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

## Setup
1. Create and activate virtual environment.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Initialize database and seed required sections:
   - `python -m backend.init__db`

## Run
1. Start backend API from project root:
   - `uvicorn backend.main:app --reload`
2. Start Streamlit UI from project root:
   - `streamlit run frontend/app.py`

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
