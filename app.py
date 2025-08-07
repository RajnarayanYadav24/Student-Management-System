from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
import sqlite3, csv
from dotenv import load_dotenv
import bcrypt
import os

load_dotenv()  


app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')  

DEFAULT_ADMIN_USERNAME = os.getenv("DEFAULT_ADMIN_USERNAME")
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD")
DEFAULT_ADMIN_ROLE = os.getenv("DEFAULT_ADMIN_ROLE")


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
        hashed_password = bcrypt.hashpw(DEFAULT_ADMIN_PASSWORD.encode('utf-8'), bcrypt.gensalt())
        cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                    (DEFAULT_ADMIN_USERNAME, hashed_password.decode('utf-8'), DEFAULT_ADMIN_ROLE))
        conn.commit()
        print(f"✅ Seeded initial owner: username='{DEFAULT_ADMIN_USERNAME}', password='{DEFAULT_ADMIN_PASSWORD}'")

    else:
     print("ℹ️ Owner already exists. No seeding needed.")

    conn.close()

    

# Helper to check role
def check_role(allowed_roles):
    role = session.get('role')
    if role not in allowed_roles:
        flash('Unauthorized action for your role.', 'danger')
        return redirect(url_for('index'))



# Login
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        # Connect to DB
        conn = sqlite3.connect("students.db")
        cur = conn.cursor()
        cur.execute("SELECT password, role FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        conn.close()

        if row:
            hashed_password_from_db, role = row
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password_from_db.encode('utf-8')):
                session['username'] = username
                session['role'] = role
                flash("Login successful!", "success")
                return redirect(url_for("index"))  
            else:
                flash("Invalid password", "danger")
        else:
            flash("User not found", "danger")

    return render_template("login.html")



# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully", "info")
    return redirect(url_for('login'))


# Index
@app.route('/index')
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


# Manage
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
           hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
           cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed_pw, role))

           conn.commit()
           flash('User added successfully!', 'success')
        except sqlite3.IntegrityError:
            flash('Username already exists.', 'danger')

    cur.execute("SELECT id, username, role FROM users")
    users = cur.fetchall()
    conn.close()
    return render_template('manage_users.html', users=users)



@app.errorhandler(Exception)
def handle_exception(e):
    import traceback
    return f"<pre>{traceback.format_exc()}</pre>", 500

if __name__ == '__main__':
    import os
    # if os.path.exists("students.db"):
    #     os.remove("students.db")
    init_db()
    app.run(debug=False)

