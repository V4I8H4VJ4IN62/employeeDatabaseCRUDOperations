from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', 'dev-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    location = db.Column(db.String)
    employees = db.relationship('Employee', backref='department', lazy=True)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    grade = db.Column(db.String)
    employees = db.relationship('Employee', backref='role', lazy=True)

class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    phone = db.Column(db.String)
    dob = db.Column(db.Date)
    hire_date = db.Column(db.Date, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    manager = db.relationship('Employee', remote_side=[id])
    salaries = db.relationship('SalaryHistory', backref='employee', lazy=True, cascade='all, delete-orphan')

class SalaryHistory(db.Model):
    __tablename__ = 'salary_history'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    effective_date = db.Column(db.Date, nullable=False)
    salary = db.Column(db.Float, nullable=False)
    note = db.Column(db.String)

def init_db():
    db.drop_all()
    db.create_all()

    d1 = Department(name='Engineering', location='Bengaluru')
    d2 = Department(name='HR', location='Mumbai')
    d3 = Department(name='Finance', location='Delhi')
    db.session.add_all([d1,d2,d3])

    r1 = Role(title='Software Engineer', grade='L2')
    r2 = Role(title='Senior Software Engineer', grade='L3')
    r3 = Role(title='HR Executive', grade='L2')
    db.session.add_all([r1,r2,r3])
    db.session.commit()

    e1 = Employee(first_name='Anita', last_name='Sharma', email='anita.sharma@example.com', phone='+91-9876500001', dob=datetime(1992,3,10), hire_date=datetime(2021,6,15), department_id=d1.id, role_id=r1.id)
    e2 = Employee(first_name='Rohit', last_name='Patel', email='rohit.patel@example.com', phone='+91-9876500002', dob=datetime(1988,11,5), hire_date=datetime(2019,4,1), department_id=d1.id, role_id=r2.id, manager_id=None)
    e3 = Employee(first_name='Sonia', last_name='Kapoor', email='sonia.kapoor@example.com', phone='+91-9876500003', dob=datetime(1995,8,20), hire_date=datetime(2023,1,20), department_id=d2.id, role_id=r3.id)
    db.session.add_all([e1,e2,e3])
    db.session.commit()

    s1 = SalaryHistory(employee_id=e1.id, effective_date=datetime(2021,6,15), salary=45000, note='Joining')
    s2 = SalaryHistory(employee_id=e1.id, effective_date=datetime(2022,7,1), salary=50000, note='Increment')
    s3 = SalaryHistory(employee_id=e2.id, effective_date=datetime(2019,4,1), salary=90000, note='Joining')
    db.session.add_all([s1,s2,s3])
    db.session.commit()

@app.route('/')
def index():
    employees = Employee.query.order_by(Employee.id).all()
    return render_template('index.html', employees=employees)

@app.route('/employee/new', methods=['GET','POST'])
def employee_new():
    departments = Department.query.all()
    roles = Role.query.all()
    managers = Employee.query.all()
    if request.method == 'POST':
        data = request.form
        dob = datetime.strptime(data.get('dob'), '%Y-%m-%d') if data.get('dob') else None
        hire_date = datetime.strptime(data.get('hire_date'), '%Y-%m-%d')
        emp = Employee(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email'),
            phone=data.get('phone'),
            dob=dob,
            hire_date=hire_date,
            department_id=int(data.get('department_id')),
            role_id=int(data.get('role_id')),
            manager_id=int(data.get('manager_id')) if data.get('manager_id') else None
        )
        db.session.add(emp)
        db.session.commit()
        sal = data.get('salary')
        if sal:
            sh = SalaryHistory(employee_id=emp.id, effective_date=hire_date, salary=float(sal), note='Joining salary')
            db.session.add(sh)
            db.session.commit()
        flash('Employee created', 'success')
        return redirect(url_for('index'))
    return render_template('employee_form.html', departments=departments, roles=roles, managers=managers)

@app.route('/employee/<int:emp_id>')
def employee_detail(emp_id):
    emp = Employee.query.get_or_404(emp_id)
    return render_template('employee_detail.html', emp=emp)

@app.route('/employee/<int:emp_id>/delete', methods=['POST'])
def employee_delete(emp_id):
    emp = Employee.query.get_or_404(emp_id)
    db.session.delete(emp)
    db.session.commit()
    flash('Employee deleted', 'warning')
    return redirect(url_for('index'))

@app.route('/api/employees')
def api_employees():
    emps = Employee.query.all()
    data = []
    for e in emps:
        data.append({
            'id': e.id,
            'name': f"{e.first_name} {e.last_name}",
            'email': e.email,
            'department': e.department.name if e.department else None,
            'role': e.role.title if e.role else None
        })
    return jsonify(data)

if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True)
