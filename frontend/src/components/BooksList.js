import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import { bookService, borrowService } from '../services/api';
import ConfirmationModal from './ConfirmationModal';

function BooksList() {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [returning, setReturning] = useState(null);
  const [bookToReturn, setBookToReturn] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filter, setFilter] = useState('all');
  const [currentCursor, setCurrentCursor] = useState('');
  const [cursorHistory, setCursorHistory] = useState([]);
  const [hasNextPage, setHasNextPage] = useState(false);
  const [hasPreviousPage, setHasPreviousPage] = useState(false);

  useEffect(() => {
    loadBooks(true);
  }, [searchQuery, filter]);

  const loadBooks = async (resetPagination = false, direction = null) => {
    try {
      setLoading(true);

      let cursorToUse = '';
      if (direction === 'next' && currentCursor) {
        cursorToUse = currentCursor;
      } else if (direction === 'prev' && cursorHistory.length > 0) {
        // For previous, we need to go back to the previous cursor
        const newHistory = [...cursorHistory];
        cursorToUse = newHistory.pop() || '';
        setCursorHistory(newHistory);
      } else if (resetPagination) {
        setCurrentCursor('');
        setCursorHistory([]);
      }

      const params = {
        limit: 20,
        search: searchQuery,
        filter: filter
      };

      if (cursorToUse) {
        params.cursor = cursorToUse;
      }

      const response = await bookService.listBooks(params);

      if (direction === 'next') {
        // Save current cursor to history for potential previous navigation
        setCursorHistory(prev => [...prev, currentCursor]);
      }

      setBooks(response.data.books);
      setCurrentCursor(response.data.next_cursor || '');
      setHasNextPage(response.data.has_more);
      setHasPreviousPage(cursorHistory.length > 0 || (direction === 'next'));
      setError(null);
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'Failed to load books';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleReturnClick = (book) => {
    if (!book.is_borrowed || !book.current_member_id) {
      return;
    }
    setBookToReturn(book);
  };

  const handleReturnConfirm = async () => {
    if (!bookToReturn) return;

    try {
      setReturning(bookToReturn.id);
      await borrowService.returnBook(bookToReturn.id, bookToReturn.current_member_id);
      toast.success(`"${bookToReturn.title}" returned successfully!`);
      setBookToReturn(null);
      // Reload current page
      loadBooks(false);
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to return book');
    } finally {
      setReturning(null);
    }
  };

  const handleReturnCancel = () => {
    setBookToReturn(null);
  };

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };

  const handleFilterChange = (e) => {
    setFilter(e.target.value);
  };

  const handleNextPage = () => {
    if (hasNextPage) {
      loadBooks(false, 'next');
    }
  };

  const handlePreviousPage = () => {
    if (hasPreviousPage) {
      loadBooks(false, 'prev');
    }
  };

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Books</h2>
        <div>
          <Link to="/create-book" className="btn btn-primary me-2">
            Add Book
          </Link>
          <button className="btn btn-outline-secondary" onClick={() => loadBooks(true)}>
            Refresh
          </button>
        </div>
      </div>

      {/* Search and Filter Controls */}
      <div className="row mb-3">
        <div className="col-md-6">
          <input
            type="text"
            className="form-control"
            placeholder="Search by title or author..."
            value={searchQuery}
            onChange={handleSearchChange}
          />
        </div>
        <div className="col-md-3">
          <select
            className="form-select"
            value={filter}
            onChange={handleFilterChange}
          >
            <option value="all">All Books</option>
            <option value="available">Available</option>
            <option value="borrowed">Borrowed</option>
          </select>
        </div>
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
        <div className="table-responsive">
          <table className="table table-striped table-hover">
            <thead>
              <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Author</th>
                <th>Status</th>
                <th>Borrowed By</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {books.length === 0 ? (
                <tr>
                  <td colSpan="6" className="text-center">
                    <div className="alert alert-info mb-0">No books found. Add some books to get started!</div>
                  </td>
                </tr>
              ) : (
                books.map((book) => (
                  <tr key={book.id}>
                    <td>{book.id}</td>
                    <td>{book.title}</td>
                    <td>{book.author}</td>
                    <td>
                      <span className={`badge ${book.is_borrowed ? 'bg-danger' : 'bg-success'}`}>
                        {book.is_borrowed ? 'Borrowed' : 'Available'}
                      </span>
                    </td>
                    <td>{book.current_member_name || '-'}</td>
                    <td>
                      <div className="d-flex gap-2">
                        <Link
                          to={`/books/${book.id}/edit`}
                          state={{ book }}
                          className="btn btn-sm btn-outline-secondary"
                        >
                          Edit
                        </Link>
                        {book.is_borrowed ? (
                          <button
                            className="btn btn-sm btn-outline-primary"
                            onClick={() => handleReturnClick(book)}
                            disabled={returning === book.id}
                          >
                            {returning === book.id ? (
                              <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                            ) : (
                              'Return'
                            )}
                          </button>
                        ) : (
                          <span className="text-muted">-</span>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>

          {/* Pagination Controls */}
          {(hasPreviousPage || hasNextPage) && (
            <div className="d-flex justify-content-center mt-3">
              <nav aria-label="Books pagination">
                <ul className="pagination">
                  <li className={`page-item ${!hasPreviousPage ? 'disabled' : ''}`}>
                    <button
                      className="page-link"
                      onClick={handlePreviousPage}
                      disabled={!hasPreviousPage}
                    >
                      Previous
                    </button>
                  </li>
                  <li className={`page-item ${!hasNextPage ? 'disabled' : ''}`}>
                    <button
                      className="page-link"
                      onClick={handleNextPage}
                      disabled={!hasNextPage}
                    >
                      Next
                    </button>
                  </li>
                </ul>
              </nav>
            </div>
          )}
        </div>
      )}

      <ConfirmationModal
        show={!!bookToReturn}
        onConfirm={handleReturnConfirm}
        onCancel={handleReturnCancel}
        title="Return Book"
        message={bookToReturn ? `Are you sure you want to return "${bookToReturn.title}"?` : ''}
        confirmText="Return"
        cancelText="Cancel"
        confirmVariant="primary"
        isProcessing={returning === bookToReturn?.id}
      />
    </div>
  );
}

export default BooksList;

