from flask import Flask, render_template, request, redirect, url_for,session, flash,Response
import sqlite3,csv

app = Flask(__name__)

app.secret_key = 'secret123'  # Needed for sessions




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
                     password TEXT NOT NULL)''')
    conn.close()



# Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('students.db')
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash('Signup successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists.', 'danger')
        finally:
            conn.close()
    return render_template('signup.html')


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
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')


# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))



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




# from flask import Response
# import csv
@app.route('/export')
def export():
    conn = sqlite3.connect('students.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM students")
    data = cur.fetchall()
    conn.close()

    def generate():
        data.insert(0, ('ID', 'Name', 'Age', 'Course'))
        for row in data:
            yield ','.join(str(item) for item in row) + '\n'

    return Response(generate(), mimetype='text/csv',
                    headers={"Content-Disposition":"attachment;filename=students.csv"})


@app.route('/add', methods=['GET', 'POST'])
def add_student():
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



@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_student(id):
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



@app.route('/delete/<int:id>')
def delete_student(id):
    conn = sqlite3.connect('students.db')
    conn.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # import os
    # if os.path.exists("students.db"):
    #     os.remove("students.db")
    init_db()
    app.run(debug=True)

