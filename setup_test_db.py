import sqlite3
from datetime import datetime, timedelta

def setup_db():
    conn = sqlite3.connect("library_test.db")
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT UNIQUE NOT NULL,
            total_copies INTEGER NOT NULL,
            available_copies INTEGER NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS borrow_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patron_id TEXT NOT NULL,
            book_id INTEGER NOT NULL,
            borrow_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            return_date TEXT
        )
    ''')

    cursor.execute('''
        INSERT INTO books (title, author, isbn, total_copies, available_copies)
        VALUES ('Sample Book', 'Author Name', '1234567890123', 3, 3)
    ''')
    borrow_date = datetime.now() - timedelta(days=1)
    due_date = datetime.now() + timedelta(days=13)
    cursor.execute('''
        INSERT INTO borrow_records (patron_id, book_id, borrow_date, due_date)
        VALUES ('123456', 1, ?, ?)
    ''', (borrow_date.isoformat(), due_date.isoformat()))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_db()
