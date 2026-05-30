from flask import Flask, render_template_string, request, redirect, session, url_for
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'super_secret_secure_key_aishwarya'

def get_db():
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    with get_db() as conn:
        with open('schema.sql', 'r') as f:
            conn.executescript(f.read())
        
        # Insert default accounts for testing our roles if they don't exist
        try:
            conn.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'Super Admin')")
            conn.execute("INSERT INTO users (username, password, role) VALUES ('librarian', 'lib123', 'Librarian')")
            conn.execute("INSERT INTO users (username, password, role) VALUES ('student', 'student123', 'Student')")
            conn.execute("INSERT INTO books (title, author, total_copies, available_copies) VALUES ('Python Basics', 'Aishwarya', 5, 5)")
            conn.commit()
        except sqlite3.IntegrityError:
            pass

# UI Layer served as an elegant, single-file card matrix
DASHBOARD_UI = """
<!DOCTYPE html>
<html>
<head>
    <title>Library Workspace</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f4f6f9; margin: 0; padding: 40px; color: #333; }
        .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); max-width: 800px; margin: 0 auto 20px; }
        h1, h2 { color: #2c3e50; margin-top: 0; }
        .badge { padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; background: #3498db; color: white; }
        .table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        .table th, .table td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        .table th { background: #f8f9fa; }
        .btn { background: #2c3e50; color: white; padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; text-decoration: none; display: inline-block; }
        .logout { background: #e74c3c; float: right; }
    </style>
</head>
<body>
    <div class="card">
        <a href="/logout" class="btn logout">Logout</a>
        <h1>📚 Library Operations Center</h1>
        <p>Active Session Identity: <strong>{{ user['username'] }}</strong> <span class="badge">{{ user['role'] }}</span></p>
        
        {% if user['role'] == 'Student' %}
            <h3>Your Account Status</h3>
            <p>Outstanding Fine Balance: <strong style="color: #e74c3c;">${{ user['fine_balance'] }}</strong></p>
        {% endif %}
    </div>

    <div class="card">
        <h2>📖 Active Book Catalog</h2>
        <table class="table">
            <tr><th>ID</th><th>Title</th><th>Author</th><th>Available Stock</th><th>Actions</th></tr>
            {% for book in books %}
            <tr>
                <td>{{ book['id'] }}</td>
                <td>{{ book['title'] }}</td>
                <td>{{ book['author'] }}</td>
                <td>{{ book['available_copies'] }} / {{ book['total_copies'] }}</td>
                <td>
                    {% if user['role'] == 'Student' %}
                        {% if user['fine_balance'] > 0 %}
                            <span style="color: red; font-size: 12px;">Borrowing Blocked (Outstanding Fine)</span>
                        {% else %}
                            <a href="/borrow/{{ book['id'] }}" class="btn">Request Loan</a>
                        {% endif %}
                    {% else %}
                        <span style="color: #7f8c8d; font-size: 13px;">Management Control Only</span>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

@app.route('/')
def dashboard():
    if 'user_id' not in session:
        return "<h3>System Locked. Please simulate authentication by accessing <a href='/login-as/student'>Student Session</a>, <a href='/login-as/librarian'>Librarian Session</a>, or <a href='/login-as/admin'>Admin Session</a>.</h3>"
    
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    books = conn.execute("SELECT * FROM books").fetchall()
    conn.close()
    
    return render_template_string(DASHBOARD_UI, user=user, books=books)

@app.route('/login-as/<role_type>')
def auto_login(role_type):
    conn = get_db()
    if role_type == 'admin':
        user = conn.execute("SELECT * FROM users WHERE role = 'Super Admin'").fetchone()
    elif role_type == 'librarian':
        user = conn.execute("SELECT * FROM users WHERE role = 'Librarian'").fetchone()
    else:
        user = conn.execute("SELECT * FROM users WHERE role = 'Student'").fetchone()
    
    session['user_id'] = user['id']
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/borrow/<int:book_id>')
def borrow_book(book_id):
    if 'user_id' not in session:
        return redirect(url_for('dashboard'))
        
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    
    # Advanced Business Barrier: Check if student has fines before inserting row
    if user['role'] == 'Student' and user['fine_balance'] > 0:
        conn.close()
        return "Transaction Aborted: Borrowing privileges revoked due to fine models.", 403
        
    book = conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    if book and book['available_copies'] > 0:
        # Decrement stock tracking layout
        conn.execute("UPDATE books SET available_copies = available_copies - 1 WHERE id = ?", (book_id,))
        # Set a clear 14-day due date
        due = datetime.now() + timedelta(days=14)
        conn.execute("INSERT INTO borrow_records (user_id, book_id, due_date) VALUES (?, ?, ?)", 
                     (user['id'], book_id, due.strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)