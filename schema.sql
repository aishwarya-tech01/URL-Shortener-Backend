<<<<<<< HEAD
DROP TABLE IF EXISTS borrow_records;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS users;

-- User Roles Table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('Super Admin', 'Librarian', 'Student')),
    fine_balance REAL DEFAULT 0.0
);

-- Books Inventory Table
CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    total_copies INTEGER NOT NULL,
    available_copies INTEGER NOT NULL
);

-- Borrow Workflow Table mapping Users to Books
CREATE TABLE borrow_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    borrow_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP NOT NULL,
    return_date TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(book_id) REFERENCES books(id)
=======
DROP TABLE IF EXISTS urls;
CREATE TABLE urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    long_url TEXT NOT NULL,
    short_code TEXT NOT NULL UNIQUE,
    clicks INTEGER NOT NULL DEFAULT 0,
    expires_at TIMESTAMP DEFAULT NULL
);

DROP TABLE IF EXISTS clicks_analytics;
CREATE TABLE clicks_analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url_id INTEGER NOT NULL,
    clicked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    browser TEXT NOT NULL,
    platform TEXT NOT NULL,
    FOREIGN KEY (url_id) REFERENCES urls (id) ON DELETE CASCADE
>>>>>>> d05962079aa0bafac7f8ce3a639094ed95f36a4a
);