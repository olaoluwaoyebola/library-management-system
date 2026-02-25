# 📚 Library Management System

A structured full-stack Library Management System built with FastAPI,
SQLite, SQLAlchemy, and Streamlit.

This system manages:

-   Book sections (6 predefined categories)
-   Book inventory & stock control
-   Borrow and return tracking
-   Automatic fine calculation
-   Status updates when books go out of stock
-   Clean backend architecture separation

------------------------------------------------------------------------

# 🏗 Project Architecture

library-management-system/
│
├── backend/
│ ├── main.py → API endpoints (Controller Layer)
│ ├── database.py → Database connection setup
│ ├── models.py → ORM table definitions
│ ├── schemas.py → API validation models
│ ├── crud.py → Business logic layer
│ ├── init_db.py → Database initialization script
│ └── config.py → System configuration
│
├── frontend/
│ └── app.py → Streamlit User Interface
│
├── requirements.txt
├── .gitignore
└── README.md

------------------------------------------------------------------------

# 📚 Library Sections

-   SCIENCES
-   ARTS
-   SOCIALS
-   ECONOMICS
-   RELIGION
-   GENERAL STUDIES

------------------------------------------------------------------------

# ⚙️ Features

## Book Management

-   Title
-   Author
-   Version / Edition
-   Cost
-   Section
-   Total copies
-   Available copies
-   Status (AVAILABLE / OUT_OF_STOCK)

## Borrow System

-   Borrow date tracking
-   Due date (7 days default)
-   Stock reduction
-   Automatic status update

## Return System

-   Return date tracking
-   Automatic stock increment
-   Fine calculation
-   Status auto-restoration

## Fine Calculation

-   Configurable fine per day
-   Applied only if returned after due date
-   Automatically stored in borrow record

------------------------------------------------------------------------

# 🛠 Tech Stack

-   Backend: FastAPI
-   Database: SQLite
-   ORM: SQLAlchemy
-   Frontend: Streamlit
-   API Communication: REST

------------------------------------------------------------------------

# 🚀 Installation & Setup Guide

## 1️⃣ Clone the Repository

git clone
https://github.com/`<your-username>`{=html}/library-management-system.git
cd library-management-system

## 2️⃣ Create Virtual Environment

python -m venv venv

Activate:

Windows: venv`\Scripts`{=tex}`\activate`{=tex}

Mac/Linux: source venv/bin/activate

## 3️⃣ Install Dependencies

pip install -r requirements.txt

## 4️⃣ Initialize Database

python backend/init_db.py

## 5️⃣ Start Backend

uvicorn backend.main:app --reload

## 6️⃣ Start Frontend

streamlit run frontend/app.py

------------------------------------------------------------------------

# 🔄 System Workflow

### Borrow Flow
1. User sends borrow request
2. System checks stock availability
3. Stock decreases
4. Borrow record created
5. Due date assigned
6. Status updated if out of stock

### Return Flow
1. Return request sent
2. System checks due date
3. Fine calculated if overdue
4. Stock increases
5. Status updated to AVAILABLE

No logical loopholes:
- Cannot borrow if stock is 0
- Status auto-syncs with available copies
- Fine applies only when overdue

------------------------------------------------------------------------

# 🤝 Collaboration Guide

⚠️ Never work directly on the main branch.

## Clone & Pull Latest

git pull origin main

## Create Branch

git checkout -b feature/your-feature-name

## Commit Changes

git add . git commit -m "Describe your change clearly"

## Push Branch

git push origin feature/your-feature-name

## Create Pull Request

Open a Pull Request on GitHub and describe: - What you added - Why it is
needed - Any changes made

------------------------------------------------------------------------

# 📏 Contribution Rules

-   Do not push directly to main
-   Keep commits small and focused
-   Test backend before pushing
-   Ensure Streamlit UI runs correctly
-   Follow project architecture strictly

------------------------------------------------------------------------

# 📌 Future Improvements(Optional)

-   Authentication (JWT)
-   Admin dashboard
-   Search & filter by section
-   PostgreSQL upgrade
-   Docker deployment
-   Role-based access control

------------------------------------------------------------------------

# 📄 License

This project is open for academic and learning purposes.
