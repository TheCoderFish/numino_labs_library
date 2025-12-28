-- Neighborhood Library Service Database Schema

-- 1. Members: Basic identification
CREATE TABLE member (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Books: Tracking state for O(1) lookups
CREATE TABLE book (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    is_borrowed BOOLEAN DEFAULT FALSE,
    current_member_id INTEGER REFERENCES member(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Transaction Ledger: Tracking history and return deltas
CREATE TABLE ledger (
    id SERIAL PRIMARY KEY,
    book_id INTEGER REFERENCES book(id),
    member_id INTEGER REFERENCES member(id),
    action_type TEXT NOT NULL, -- 'BORROW' or 'RETURN'
    log_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date_snapshot DATE -- Added for O(1) delay calculation
);

-- Create indexes for better query performance
CREATE INDEX idx_book_is_borrowed ON book(is_borrowed);
CREATE INDEX idx_book_current_member ON book(current_member_id);
CREATE INDEX idx_ledger_book_id ON ledger(book_id);
CREATE INDEX idx_ledger_member_id ON ledger(member_id);
CREATE INDEX idx_ledger_action_type ON ledger(action_type);

