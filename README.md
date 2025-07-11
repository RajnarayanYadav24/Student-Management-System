# 🎓 Flask Student Management System

A simple **Student Management System** built with **Flask** and **SQLite3**, featuring login/logout authentication, CRUD operations, search, and CSV export.

---

## 🚀 Features

✅ **Login / Logout system**  
- Only registered users can access the system.
- Sessions maintained for secure access.

✅ **Manage Students**  
- Add new student records.
- Update existing student information.
- Delete student records.

✅ **Search**  
- Search students by **name** or **course**.

✅ **Export**  
- Export student data as a **CSV file**.

✅ **Bootstrap UI**  
- Clean and responsive interface with Bootstrap.

---

## 🗄 Database Schema

### 📌 `users` table
| Column    | Type    | Description           |
|-----------|---------|-----------------------|
| id        | INTEGER | Primary Key           |
| username  | TEXT    | Unique user name      |
| password  | TEXT    | Password (plain text) |

### 📌 `students` table
| Column    | Type    | Description               |
|-----------|---------|---------------------------|
| id        | INTEGER | Primary Key               |
| name      | TEXT    | Student name              |
| age       | INTEGER | Age                       |
| course    | TEXT    | Course enrolled           |
| roll_no   | TEXT    | Roll number               |
| email     | TEXT    | Email address             |
| phone     | TEXT    | Contact phone number      |
| address   | TEXT    | Address                   |
| year      | TEXT    | Academic year / semester  |
| remarks   | TEXT    | Additional remarks        |

---

## ⚙️ Setup Instructions

### 🐍 1. Create a virtual environment
    python -m venv venv_name
### ▶️ 2. Activate it
   Windows
   venv_name\Scripts\activate

    Linux / Mac
    source venv_name/bin/activate
### 📦 3. Install dependencies
    pip install flask

### 🚀 Run the application
     python app.py
     Visit your app at: http://127.0.0.1:5000/

### 🛠 Technologies Used

  Python 3.11+
  Flask
  SQLite3
  Bootstrap 5

# 📧 Contact
 ✍️ Developed by Rajnarayan Yadav
 📧 rajnarayannit22@gmail.com



    


