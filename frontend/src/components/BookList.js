import React, { useState, useEffect } from 'react';
import { bookService } from '../services/api';

function BookList() {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadBooks();
  }, []);

  const loadBooks = async () => {
    try {
      setLoading(true);
      const response = await bookService.listBooks();
      setBooks(response.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load books');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Book Catalog</h2>
        <button className="btn btn-primary" onClick={loadBooks}>
          Refresh
        </button>
      </div>

      {error && (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      ) : (
        <div className="row">
          {books.length === 0 ? (
            <div className="col-12">
              <div className="alert alert-info">No books found. Add some books to get started!</div>
            </div>
          ) : (
            books.map((book) => (
              <div key={book.id} className="col-md-6 col-lg-4 mb-4">
                <div className="card h-100">
                  <div className="card-body">
                    <h5 className="card-title">{book.title}</h5>
                    <p className="card-text">
                      <strong>Author:</strong> {book.author}
                    </p>
                    <p className="card-text">
                      <span className={`badge ${book.is_borrowed ? 'bg-danger' : 'bg-success'}`}>
                        {book.is_borrowed ? 'Borrowed' : 'Available'}
                      </span>
                    </p>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

export default BookList;

