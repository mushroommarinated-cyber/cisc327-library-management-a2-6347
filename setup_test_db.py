import sqlite3
from datetime import datetime, timedelta
import os

def setup_db():
    db_path = os.environ.get("DATABASE", "library_test.db")
    conn = sqlite3.connect(db_path)
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

    cursor.execute('DELETE FROM borrow_records')
    cursor.execute('DELETE FROM books')

    books = [
        ('Sample Book 1', 'Author 1', '1111111111111', 3, 3),
        ('Sample Book 2', 'Author 2', '2222222222222', 2, 2),
        ('Sample Book 3', 'Author 3', '3333333333333', 1, 0),
        ('Sample Book 4', 'Author 4', '4444444444444', 5, 5),
        ('Sample Book 5', 'Author 5', '5555555555555', 5, 5),
        ('Sample Book 6', 'Author 6', '6666666666666', 5, 5),
    ]
    for title, author, isbn, total, available in books:
        cursor.execute('''
            INSERT INTO books (title, author, isbn, total_copies, available_copies)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, author, isbn, total, available))

    today = datetime.now()
    borrow_records = [
        ('123456', 1, today - timedelta(days=1), today + timedelta(days=13)),
        ('123456', 2, today - timedelta(days=2), today + timedelta(days=12)),
        ('123456', 3, today - timedelta(days=20), today - timedelta(days=6)),
        ('123456', 4, today - timedelta(days=3), today + timedelta(days=11)),
        ('123456', 5, today - timedelta(days=4), today + timedelta(days=10)),
        ('123456', 6, today - timedelta(days=5), today + timedelta(days=9)),
    ]
    for patron_id, book_id, borrow_date, due_date in borrow_records:
        cursor.execute('''
            INSERT INTO borrow_records (patron_id, book_id, borrow_date, due_date)
            VALUES (?, ?, ?, ?)
        ''', (patron_id, book_id, borrow_date.isoformat(), due_date.isoformat()))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_db()
