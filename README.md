# 🔗 Advanced URL Shortener & Analytics Dashboard

A feature-rich, coding-heavy Python backend web application that maps long URLs into clean, short links, auto-generates custom QR code assets, and logs detailed visitor telemetry data into a relational database.

---

## 🛠️ Tech Stack

This project is built from scratch using a robust, lightweight backend stack:

* **Backend Framework:** `Python 3.x` with `Flask` (A lightweight, WSGI web application framework)
* **Database Management:** `SQLite3` (A fast, serverless, self-contained relational SQL database engine)
* **Asset Generation Engine:** `qrcode` & `Pillow (PIL)` (Libraries for dynamically building and rendering high-quality visual QR matrix codes)
* **Environment Isolated Block:** `venv` (Python Virtual Environments to ensure clean, sandboxed package management)
* **Frontend UI Layer:** Inline `HTML5` & `CSS3` with a modern, responsive card-based layout

---

## 📁 Project Structure

```plaintext
URL SHORTNER/
│
├── README.md               # Project documentation and guide
├── app.py                  # The primary Python engine (Routes, Analytics, Logic)
├── schema.sql              # Relational database table blueprints
├── url_shortener.db        # Live local SQL database file (Generated automatically)
├── .gitignore              # Tells Git which system files to skip uploading
│
├── venv/                   # Sandbox environment containing project dependencies
└── static/                 # Folder for public visual elements
    └── qrcodes/            # Saved auto-generated .png QR code files