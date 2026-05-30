import os
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'super_secret_library_key_secure'
DATABASE = 'library.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database structure and injects foundational testing data."""
    conn = get_db_connection()
    
    # 1. Users Table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('Super Admin', 'Librarian', 'Student')),
            fine_balance REAL DEFAULT 0.0
        )
    ''')
    
    # 2. Books Inventory Table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            total_copies INTEGER NOT NULL,
            available_copies INTEGER NOT NULL
        )
    ''')
    
    # 3. Borrow Records Table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS borrow_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            borrow_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            due_date TIMESTAMP NOT NULL,
            return_date TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(book_id) REFERENCES books(id)
        )
    ''')
    
    # Inject Mock Data for testing
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role, fine_balance) VALUES ('student1', 'pass123', 'Student', 0.0)")
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role, fine_balance) VALUES ('librarian1', 'pass456', 'Librarian', 0.0)")
    
    cursor.execute("SELECT COUNT(*) FROM books")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO books (title, author, total_copies, available_copies) VALUES ('Python Basics for Beginners', 'Saurabh Kumar', 5, 5)")
        cursor.execute("INSERT INTO books (title, author, total_copies, available_copies) VALUES ('Database Management Systems', 'Aishwarya R.', 3, 3)")
        cursor.execute("INSERT INTO books (title, author, total_copies, available_copies) VALUES ('Web Systems Engine Design', 'Flask Guru', 2, 2)")
    
    conn.commit()
    conn.close()

# ---------------- APPLICATION WORKFLOW CONTROLLERS ----------------

@app.route('/')
def index():
    """Fallback entry point redirecting to default student view."""
    return redirect(url_for('login_simulation', role_type='student'))

@app.route('/login-as/<role_type>')
def login_simulation(role_type):
    """Simulates instant profile switching using session injection."""
    role = role_type.lower()
    conn = get_db_connection()
    
    if role == 'student':
        user_row = conn.execute("SELECT * FROM users WHERE role='Student' LIMIT 1").fetchone()
        session['user'] = {'id': user_row['id'], 'username': user_row['username'], 'role': 'Student', 'fine': user_row['fine_balance']}
    elif role == 'librarian':
        user_row = conn.execute("SELECT * FROM users WHERE role='Librarian' LIMIT 1").fetchone()
        session['user'] = {'id': user_row['id'], 'username': user_row['username'], 'role': 'Librarian', 'fine': 0.0}
    else:
        conn.close()
        return "Access Violation: Target security group unauthorized.", 403

    # Pull dashboard statistics
    books = conn.execute('SELECT * FROM books').fetchall()
    
    # Fetch tracking history
    history_query = '''
        SELECT br.id, b.title, u.username, br.borrow_date, br.due_date, br.return_date 
        FROM borrow_records br
        JOIN books b ON br.book_id = b.id
        JOIN users u ON br.user_id = u.id
    '''
    if session['user']['role'] == 'Student':
        history = conn.execute(history_query + " WHERE br.user_id = ?", (session['user']['id'],)).fetchall()
    else:
        history = conn.execute(history_query).fetchall()
        
    conn.close()
    return render_template('dashboard.html', books=books, history=history, user=session['user'])

@app.route('/borrow/<int:book_id>', methods=['POST'])
def borrow_book(book_id):
    """Handles the book borrowing pipeline logic."""
    if 'user' not in session or session['user']['role'] != 'Student':
        return "Security block: Librarians are unauthorized to borrow inventory.", 403

    conn = get_db_connection()
    book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()

    if book and book['available_copies'] > 0:
        # Deduct an available copy
        conn.execute('UPDATE books SET available_copies = available_copies - 1 WHERE id = ?', (book_id,))
        
        # Calculate dates
        borrow_dt = datetime.now()
        due_dt = borrow_dt + timedelta(days=14)
        
        conn.execute('''
            INSERT INTO borrow_records (user_id, book_id, borrow_date, due_date)
            VALUES (?, ?, ?, ?)
        ''', (session['user']['id'], book_id, borrow_dt.strftime('%Y-%m-%d %H:%M:%S'), due_dt.strftime('%Y-%m-%d %H:%M:%S')))
        
        conn.commit()
    
    conn.close()
    return redirect(url_for('login_simulation', role_type='student'))

@app.route('/return/<int:record_id>', methods=['POST'])
def return_book(record_id):
    """Processes inventory returns."""
    conn = get_db_connection()
    record = conn.execute('SELECT * FROM borrow_records WHERE id = ?', (record_id,)).fetchone()

    if record and record['return_date'] is None:
        # Return book copy to inventory
        conn.execute('UPDATE books SET available_copies = available_copies + 1 WHERE id = ?', (record['book_id'],))
        
        # Timestamp the return
        return_dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn.execute('UPDATE borrow_records SET return_date = ? WHERE id = ?', (return_dt, record_id))
        
        conn.commit()
        
    conn.close()
    current_role = session.get('user', {}).get('role', 'Student').lower()
    return redirect(url_for('login_simulation', role_type=current_role))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)