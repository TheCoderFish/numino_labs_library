import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import { borrowService } from '../services/api';

function MemberBorrowedBooks() {
  const { id } = useParams();
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [memberName, setMemberName] = useState('');

  useEffect(() => {
    loadBorrowedBooks();
  }, [id]);

  const loadBorrowedBooks = async () => {
    try {
      setLoading(true);
      const response = await borrowService.getBorrowedBooks(id);
      setBooks(response.data);
      // For now, we'll just show the ID, but you could fetch member details if needed
      setMemberName(`Member ${id}`);
      setError(null);
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'Failed to load borrowed books';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Books Borrowed by {memberName}</h2>
        <Link to="/members" className="btn btn-secondary">
          Back to Members
        </Link>
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
              </tr>
            </thead>
            <tbody>
              {books.length === 0 ? (
                <tr>
                  <td colSpan="3" className="text-center">
                    <div className="alert alert-info mb-0">No books currently borrowed by this member.</div>
                  </td>
                </tr>
              ) : (
                books.map((book) => (
                  <tr key={book.id}>
                    <td>{book.id}</td>
                    <td>{book.title}</td>
                    <td>{book.author}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default MemberBorrowedBooks;