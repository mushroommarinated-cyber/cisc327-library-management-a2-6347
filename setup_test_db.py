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

    cursor.execute('DELETE FROM borrow_records')
    cursor.execute('DELETE FROM books')

    books = [
        ('Sample Book 1', 'Author 1', '1111111111111', 3, 3),  # id=1
        ('Sample Book 2', 'Author 2', '2222222222222', 2, 2),  # id=2
        ('Sample Book 3', 'Author 3', '3333333333333', 1, 0),  # id=3, no copies
        ('Sample Book 4', 'Author 4', '4444444444444', 5, 5),  # id=4
        ('Sample Book 5', 'Author 5', '5555555555555', 5, 5),  # id=5
        ('Sample Book 6', 'Author 6', '6666666666666', 5, 5),  # id=6
    ]
    for title, author, isbn, total, available in books:
        cursor.execute('''
            INSERT INTO books (title, author, isbn, total_copies, available_copies)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, author, isbn, total, available))

    today = datetime.now() # adds borrow recordz
    borrow_records = [
        # active borrow (id=1)
        ('123456', 1, today - timedelta(days=1), today + timedelta(days=13)),
        # active borrow (id=2)
        ('123456', 2, today - timedelta(days=2), today + timedelta(days=12)),
        # Returned borrow (id=3)
        ('123456', 3, today - timedelta(days=20), today - timedelta(days=6)),
        # Additional borrows to test limit (id=4-6)
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
