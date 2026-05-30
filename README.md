# 📚 Multi-Tenant Role-Based Library Management System

A robust, enterprise-grade Python backend system featuring complete Role-Based Access Control (RBAC) across multiple tenants. The application isolates user spaces into three computational tiers (Super Admin, Librarian, and Student), tracks book inventory, implements transactional borrowing workflows, and programmatically computes live fine frameworks utilizing relational database logic.

---

## 🛠️ Tech Stack

* **Backend Engine:** `Python 3.x` with `Flask` (For modular routing, session tracking, and authentication middlewares)
* **Relational Database Management System:** `SQLite3` (Enforcing strict schema constraints, foreign key mappings, and automated calculations)
* **Environment Sandboxing:** `venv` (Python Virtual Environments for isolated dependency management)
* **Frontend UI Matrix:** Modern `HTML5` templates styled with semantic `CSS3` grid systems

---

## 📁 Project Structure

```plaintext
LIBRARY MANAGEMENT SYSTEM/
│
├── README.md               # System architectural documentation
├── app.py                  # Primary Flask controller handling Authentication & Logic
├── schema.sql              # Relational SQL structure containing tables and foreign keys
├── library.db              # Live SQLite database instance (Auto-generated)
├── .gitignore              # Defines local environment elements ignored by Git
│
└── venv/                   # Sandbox package block