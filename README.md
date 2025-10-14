# Employee Management System (SQLite)

A simple Employee Management System built with Flask + SQLAlchemy using SQLite.
This repository is intended for learning / small projects and demonstrates:
- Relational schema (departments, roles, employees, salary_history)
- Flask app with basic CRUD and HTML templates (Bootstrap)
- SQLite as the database for easy local runs

## Requirements
- Python 3.8+
- pip

## Quick start
```bash
git clone <this-repo>
cd employee_management_system_sqlite
python -m venv venv
source venv/bin/activate    # on Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000 in your browser. The app initializes `employees.db` automatically if not present.

## Notes
- Database: `sqlite:///employees.db` (created in project root)
- To reset the DB: delete `employees.db` and restart the app.
- This is a demo project. For production use, move to PostgreSQL/MySQL and add migrations & auth.
