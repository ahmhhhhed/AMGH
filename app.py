
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.db'
db = SQLAlchemy(app)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    place_of_birth = db.Column(db.String(100))
    birth_date = db.Column(db.String(20))
    department = db.Column(db.String(100))
    position = db.Column(db.String(100))
    join_date = db.Column(db.String(20))
    leave_date = db.Column(db.String(20))
    note = db.Column(db.String(200))

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        code = request.form.get('code', '')

        if role == 'admin' and code != 'gx0988':
            return "رمز الدعم الفني غير صحيح"
        if username and password:
            session['role'] = role
            return redirect('/admin' if role == 'admin' else '/user')
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if session.get('role') != 'admin':
        return redirect('/')
    if request.method == 'POST':
        emp = Employee(
            name=request.form['name'],
            place_of_birth=request.form['place_of_birth'],
            birth_date=request.form['birth_date'],
            department=request.form['department'],
            position=request.form['position'],
            join_date=request.form['join_date'],
            leave_date=request.form['leave_date'],
            note=request.form['note']
        )
        db.session.add(emp)
        db.session.commit()
    employees = Employee.query.all()
    return render_template('admin.html', employees=employees)

@app.route('/update/<int:emp_id>', methods=['POST'])
def update(emp_id):
    emp = Employee.query.get_or_404(emp_id)
    emp.name = request.form['name']
    emp.place_of_birth = request.form['place_of_birth']
    emp.birth_date = request.form['birth_date']
    emp.department = request.form['department']
    emp.position = request.form['position']
    emp.join_date = request.form['join_date']
    emp.leave_date = request.form['leave_date']
    emp.note = request.form['note']
    db.session.commit()
    return redirect('/admin')

@app.route('/user', methods=['GET', 'POST'])
def user():
    results = []
    if request.method == 'POST':
        search_type = request.form['search_type']
        search_value = request.form['search_value']
        access_code = request.form.get('access_code', '')
        if search_type == 'free_search' and access_code == '$$$$':
            results = Employee.query.filter(
                (Employee.name.contains(search_value)) |
                (Employee.place_of_birth.contains(search_value)) |
                (Employee.department.contains(search_value))
            ).all()
        elif search_type == 'name_search' and access_code == '0000':
            results = Employee.query.filter(Employee.name.contains(search_value)).all()
        elif search_type == 'id_search':
            results = Employee.query.filter(Employee.id == search_value).all()
    return render_template('user.html', results=results)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
