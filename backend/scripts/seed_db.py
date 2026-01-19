#!/usr/bin/env python3
"""
Database seeder for local development.

This script will:
- clear existing data from `ledger`, `book`, `member`
- insert 40 members
- insert 100 books
- mark a subset of books as borrowed by some members

Usage: backend/venv/bin/python backend/scripts/seed_db.py
Ensure environment variables for DB are set (or a .env file in backend/)
"""
import os
import random
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values

load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5435')
DB_NAME = os.getenv('DB_NAME', 'numino_db')
DB_USER = os.getenv('DB_USER', 'numino_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'numino_password')

NUM_MEMBERS = 40
NUM_BOOKS = 100
BORROWED_RATIO = 0.18  # approx 18% of books will be borrowed

def get_conn():
    return psycopg2.connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)

def clear_tables(conn):
    with conn.cursor() as cur:
        # Use TRUNCATE with restart identity to reset serial ids
        cur.execute('TRUNCATE TABLE ledger RESTART IDENTITY CASCADE;')
        cur.execute('TRUNCATE TABLE book RESTART IDENTITY CASCADE;')
        cur.execute('TRUNCATE TABLE member RESTART IDENTITY CASCADE;')
    conn.commit()

def create_members(conn, n):
    members = []
    for i in range(1, n+1):
        name = f"Member {i}"
        email = f"member{i}@example.com"
        members.append((name, email))

    with conn.cursor() as cur:
        execute_values(cur,
            "INSERT INTO member (name, email, created_at, updated_at) VALUES %s RETURNING id, name, email",
            members,
            template="(%s, %s, NOW(), NOW())"
        )
        rows = cur.fetchall()
    conn.commit()
    return rows

def create_books(conn, n):
    books = []
    for i in range(1, n+1):
        title = f"Sample Book {i}"
        author = f"Author {((i-1) % 20) + 1}"
        books.append((title, author, False))

    with conn.cursor() as cur:
        execute_values(cur,
            "INSERT INTO book (title, author, is_borrowed, created_at, updated_at) VALUES %s RETURNING id, title, author",
            [(title, author, is_borrowed) for title, author, is_borrowed in books],
            template="(%s, %s, %s, NOW(), NOW())"
        )
        rows = cur.fetchall()
    conn.commit()
    return rows

def assign_borrows(conn, book_rows, member_rows, ratio=0.15):
    total = len(book_rows)
    to_borrow = max(1, int(total * ratio))
    borrowed_book_ids = random.sample([r[0] for r in book_rows], to_borrow)
    member_ids = [r[0] for r in member_rows]

    updates = []
    ledger_entries = []
    for bid in borrowed_book_ids:
        mid = random.choice(member_ids)
        updates.append((mid, True, bid))
        ledger_entries.append((bid, mid, 'BORROW'))

    with conn.cursor() as cur:
        # Update book rows to mark borrowed
        execute_values(cur,
            "UPDATE book SET current_member_id = data.member_id, is_borrowed = data.is_borrowed, updated_at = CURRENT_TIMESTAMP FROM (VALUES %s) AS data(member_id, is_borrowed, id) WHERE book.id = data.id;",
            updates
        )

        # Insert ledger entries
        execute_values(cur,
            "INSERT INTO ledger (book_id, member_id, action_type, log_date) VALUES %s",
            ledger_entries,
            template="(%s, %s, %s, NOW())"
        )
    conn.commit()

def main():
    print('Connecting to DB at', DB_HOST, DB_PORT, DB_NAME)
    conn = get_conn()
    try:
        print('Clearing tables...')
        clear_tables(conn)

        print(f'Creating {NUM_MEMBERS} members...')
        members = create_members(conn, NUM_MEMBERS)
        print('Members created:', len(members))

        print(f'Creating {NUM_BOOKS} books...')
        books = create_books(conn, NUM_BOOKS)
        print('Books created:', len(books))

        print('Assigning borrowed books...')
        assign_borrows(conn, books, members, ratio=BORROWED_RATIO)
        print('Seeding complete.')

    finally:
        conn.close()

if __name__ == '__main__':
    main()
