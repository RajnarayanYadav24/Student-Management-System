from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
import sqlite3, csv
from dotenv import load_dotenv
import os

load_dotenv()  

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')  

# Initialize DB
def init_db():
    conn = sqlite3.connect('students.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS students
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT NOT NULL,
                     age INTEGER NOT NULL,
                     course TEXT NOT NULL,
                     roll_no TEXT,
                     email TEXT,
                     phone TEXT,
                     address TEXT,
                     year TEXT,
                     remarks TEXT)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS users
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     username TEXT UNIQUE NOT NULL,
                     password TEXT NOT NULL,
                     role TEXT NOT NULL)''')
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
     cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                ('Admin', 'Admin123', 'owner'))
    conn.commit()
    print("✅ Seeded initial owner: username='Admin', password='Admin123'")

    conn.close()

    

# Helper to check role
def check_role(allowed_roles):
    role = session.get('role')
    if role not in allowed_roles:
        flash('Unauthorized action for your role.', 'danger')
        return redirect(url_for('index'))



# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('students.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cur.fetchone()
        conn.close()
        if user:
            session['username'] = username
            session['role'] = user[3]  # id, username, password, role
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))

# Index
@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    q = request.args.get('q', '')
    conn = sqlite3.connect('students.db')
    cur = conn.cursor()
    if q:
        cur.execute("SELECT * FROM students WHERE name LIKE ? OR course LIKE ?", (f'%{q}%', f'%{q}%'))
    else:
        cur.execute("SELECT * FROM students")
    students = cur.fetchall()
    conn.close()
    return render_template('index.html', students=students)

# Add
@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if 'username' not in session:
        return redirect(url_for('login'))
    if check_role(['owner', 'staff1']): return check_role(['owner', 'staff1'])
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        course = request.form['course']
        roll_no = request.form['roll_no']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        year = request.form['year']
        remarks = request.form['remarks']
        conn = sqlite3.connect('students.db')
        conn.execute('INSERT INTO students (name, age, course, roll_no, email, phone, address, year, remarks) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                     (name, age, course, roll_no, email, phone, address, year, remarks))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_student.html')

# Update
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_student(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    if check_role(['owner', 'staff3']): return check_role(['owner', 'staff3'])
    conn = sqlite3.connect('students.db')
    cur = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        course = request.form['course']
        roll_no = request.form['roll_no']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        year = request.form['year']
        remarks = request.form['remarks']
        cur.execute('UPDATE students SET name=?, age=?, course=?, roll_no=?, email=?, phone=?, address=?, year=?, remarks=? WHERE id=?',
                    (name, age, course, roll_no, email, phone, address, year, remarks, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    cur.execute("SELECT * FROM students WHERE id=?", (id,))
    student = cur.fetchone()
    conn.close()
    return render_template('update_student.html', student=student)

# Delete
@app.route('/delete/<int:id>')
def delete_student(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    if check_role(['owner', 'staff2']): return check_role(['owner', 'staff2'])
    conn = sqlite3.connect('students.db')
    conn.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Export
@app.route('/export')
def export():
    if 'username' not in session:
        return redirect(url_for('login'))
    if check_role(['owner']): return check_role(['owner'])
    conn = sqlite3.connect('students.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM students")
    data = cur.fetchall()
    conn.close()
    def generate():
        data.insert(0, ('ID', 'Name', 'Age', 'Course', 'Roll No', 'Email', 'Phone', 'Address', 'Year', 'Remarks'))
        for row in data:
            yield ','.join(str(item) for item in row) + '\n'
    return Response(generate(), mimetype='text/csv',
                    headers={"Content-Disposition": "attachment;filename=students.csv"})


@app.route('/delete_user/<int:id>')
def delete_user(id):
    if 'username' not in session or session['role'] != 'owner':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('index'))

    conn = sqlite3.connect('students.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('manage_users'))



@app.route('/manage_users', methods=['GET', 'POST'])
def manage_users():
    if 'username' not in session or session['role'] != 'owner':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('index'))

    conn = sqlite3.connect('students.db')
    cur = conn.cursor()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        try:
            cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
            conn.commit()
            flash('User added successfully!', 'success')
        except sqlite3.IntegrityError:
            flash('Username already exists.', 'danger')

    cur.execute("SELECT id, username, role FROM users")
    users = cur.fetchall()
    conn.close()
    return render_template('manage_users.html', users=users)



if __name__ == '__main__':
    import os
    # if os.path.exists("students.db"):
    #     os.remove("students.db")
    init_db()
    app.run(debug=False)

