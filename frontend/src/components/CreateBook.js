import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { bookService } from '../services/api';

function CreateBook() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    title: '',
    author: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      await bookService.createBook(formData);
      setSuccess(true);
      setFormData({ title: '', author: '' });
      setTimeout(() => {
        navigate('/books');
      }, 1500);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create book');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="row justify-content-center">
      <div className="col-md-6">
        <h2>Add New Book</h2>

        {error && (
          <div className="alert alert-danger" role="alert">
            {error}
          </div>
        )}

        {success && (
          <div className="alert alert-success" role="alert">
            Book created successfully! Redirecting...
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label htmlFor="title" className="form-label">
              Title
            </label>
            <input
              type="text"
              className="form-control"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              required
            />
          </div>

          <div className="mb-3">
            <label htmlFor="author" className="form-label">
              Author
            </label>
            <input
              type="text"
              className="form-control"
              id="author"
              name="author"
              value={formData.author}
              onChange={handleChange}
              required
            />
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                Creating...
              </>
            ) : (
              'Create Book'
            )}
          </button>
        </form>
      </div>
    </div>
  );
}

export default CreateBook;

