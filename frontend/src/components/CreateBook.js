import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { toast } from 'react-toastify';
import { bookService } from '../services/api';
import { validateBookForm, trimWhitespace } from '../utils/validation';

function CreateBook() {
  const navigate = useNavigate();
  const location = useLocation();
  const { id } = useParams();
  const isEditMode = !!id;
  const [formData, setFormData] = useState({
    title: '',
    author: '',
  });
  const [formErrors, setFormErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [loadingBook, setLoadingBook] = useState(isEditMode);

  useEffect(() => {
    if (isEditMode) {
      // Try to get book data from navigation state first
      if (location.state?.book) {
        setFormData({
          title: location.state.book.title || '',
          author: location.state.book.author || '',
        });
        setLoadingBook(false);
      } else {
        loadBook();
      }
    }
  }, [id, location.state]);

  const loadBook = async () => {
    try {
      setLoadingBook(true);
      // Fetch all books and find the one with matching ID
      // Since there's no GET by ID endpoint, we'll fetch a reasonable number
      const response = await bookService.listBooks({ limit: 1000 });
      const books = response.data.books || [];
      const book = books.find(b => b.id === parseInt(id));
      
      if (book) {
        setFormData({
          title: book.title || '',
          author: book.author || '',
        });
      } else {
        toast.error('Book not found');
        navigate('/books');
      }
    } catch (err) {
      const errorMessage = err.response?.data?.error?.message || err.response?.data?.error || 'Failed to load book';
      toast.error(errorMessage);
      navigate('/books');
    } finally {
      setLoadingBook(false);
    }
  };

  const handleChange = (e) => {
    const value = e.target.value;
    const name = e.target.name;
    
    // Clear error for this field when user starts typing
    if (formErrors[name]) {
      setFormErrors({
        ...formErrors,
        [name]: null
      });
    }
    
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Trim whitespace from all fields
    const trimmedData = {
      title: trimWhitespace(formData.title),
      author: trimWhitespace(formData.author),
    };

    // Validate form
    const validation = validateBookForm(trimmedData);
    if (!validation.isValid) {
      setFormErrors(validation.errors);
      toast.error('Please fix the form errors');
      return;
    }

    setLoading(true);
    setFormErrors({});

    try {
      if (isEditMode) {
        await bookService.updateBook(id, trimmedData);
        toast.success('Book updated successfully!');
      } else {
        await bookService.createBook(trimmedData);
        toast.success('Book created successfully!');
        setFormData({ title: '', author: '' });
      }
      
      setTimeout(() => {
        navigate('/books');
      }, 1000);
    } catch (err) {
      const errorMessage = err.response?.data?.error?.message || err.response?.data?.error || `Failed to ${isEditMode ? 'update' : 'create'} book`;
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  if (loadingBook) {
    return (
      <div className="row justify-content-center">
        <div className="col-md-6">
          <div className="text-center">
            <div className="spinner-border" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="row justify-content-center">
      <div className="col-md-6">
        <h2>{isEditMode ? 'Edit Book' : 'Add New Book'}</h2>

        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label htmlFor="title" className="form-label">
              Title <span className="text-danger">*</span>
            </label>
            <input
              type="text"
              className={`form-control ${formErrors.title ? 'is-invalid' : ''}`}
              id="title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              required
            />
            {formErrors.title && (
              <div className="invalid-feedback">{formErrors.title}</div>
            )}
          </div>

          <div className="mb-3">
            <label htmlFor="author" className="form-label">
              Author <span className="text-danger">*</span>
            </label>
            <input
              type="text"
              className={`form-control ${formErrors.author ? 'is-invalid' : ''}`}
              id="author"
              name="author"
              value={formData.author}
              onChange={handleChange}
              required
            />
            {formErrors.author && (
              <div className="invalid-feedback">{formErrors.author}</div>
            )}
          </div>

          <div className="d-flex gap-2">
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  {isEditMode ? 'Updating...' : 'Creating...'}
                </>
              ) : (
                isEditMode ? 'Update Book' : 'Create Book'
              )}
            </button>
            <button 
              type="button" 
              className="btn btn-outline-secondary" 
              onClick={() => navigate('/books')}
              disabled={loading}
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreateBook;

