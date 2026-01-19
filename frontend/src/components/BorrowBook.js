import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { useNavigate } from 'react-router-dom';
import { bookService, memberService, borrowService } from '../services/api';

function BorrowBook() {
  const navigate = useNavigate();
  const [books, setBooks] = useState([]);
  const [members, setMembers] = useState([]);
  const [filteredBooks, setFilteredBooks] = useState([]);
  const [filteredMembers, setFilteredMembers] = useState([]);
  const [bookSearch, setBookSearch] = useState('');
  const [memberSearch, setMemberSearch] = useState('');
  const [showBookDropdown, setShowBookDropdown] = useState(false);
  const [showMemberDropdown, setShowMemberDropdown] = useState(false);
  const [formData, setFormData] = useState({
    book_id: '',
    book_title: '',
    member_id: '',
    member_name: '',
  });
  const [loading, setLoading] = useState(false);
  const [booksLoading, setBooksLoading] = useState(false);
  const [membersLoading, setMembersLoading] = useState(false);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (!event.target.closest('.position-relative')) {
        setShowBookDropdown(false);
        setShowMemberDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Search books via API when bookSearch changes
  useEffect(() => {
    const searchBooks = async () => {
      // Don't search if a book is already selected (bookSearch contains " by ")
      if (formData.book_id && bookSearch.includes(' by ')) {
        setFilteredBooks([]);
        return;
      }

      if (bookSearch && bookSearch.length > 0) {
        setBooksLoading(true);
        try {
          // Add is_borrowed=false filter to only get available books
          const response = await bookService.searchBooks(bookSearch, { is_borrowed: 'false' });
          // Response is already transformed by API service: {data, next_cursor, has_more}
          const books = response.data || [];
          const filtered = books.slice(0, 10);
          setFilteredBooks(filtered);
          // Ensure dropdown shows if we have results
          if (filtered.length > 0) {
            setShowBookDropdown(true);
          }
        } catch (err) {
          console.error('Book search error:', err);
          setFilteredBooks([]);
        } finally {
          setBooksLoading(false);
        }
      } else {
        setFilteredBooks([]);
      }
    };

    const debounceTimer = setTimeout(() => {
      searchBooks();
    }, 300); // Debounce for 300ms

    return () => clearTimeout(debounceTimer);
  }, [bookSearch, formData.book_id]);

  // Search members via API when memberSearch changes
  useEffect(() => {
    const searchMembers = async () => {
      if (memberSearch && memberSearch.length > 0) {
        setMembersLoading(true);
        try {
          const response = await memberService.searchMembers(memberSearch);
          // Response is already transformed: {data, next_cursor, has_more}
          const members = response.data || [];
          setFilteredMembers(members.slice(0, 10));
        } catch (err) {
          console.error('Member search error:', err);
          setFilteredMembers([]);
        } finally {
          setMembersLoading(false);
        }
      } else {
        setFilteredMembers([]);
      }
    };

    const debounceTimer = setTimeout(() => {
      searchMembers();
    }, 300); // Debounce for 300ms

    return () => clearTimeout(debounceTimer);
  }, [memberSearch]);



  const handleBookSelect = (book) => {
    setFormData({
      ...formData,
      book_id: book.id,
      book_title: `${book.title} by ${book.author}`,
    });
    setBookSearch(`${book.title} by ${book.author}`);
    setShowBookDropdown(false);
    setFilteredBooks([]); // Clear filtered books after selection
  };

  const handleMemberSelect = (member) => {
    setFormData({
      ...formData,
      member_id: member.id,
      member_name: `${member.name} (${member.email})`,
    });
    setMemberSearch(`${member.name} (${member.email})`);
    setShowMemberDropdown(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.book_id || !formData.member_id) {
      const errorMsg = 'Please select both a book and a member';
      toast.error(errorMsg);
      return;
    }

    setLoading(true);

    try {
      await borrowService.borrowBook(formData.book_id, formData.member_id);
      toast.success('Book borrowed successfully!');
      // Navigate to member's borrowed books page
      navigate(`/members/${formData.member_id}/borrowed-books`);
    } catch (err) {
      const errorMsg = err.response?.data?.error || 'Failed to borrow book';
      toast.error(errorMsg);
      setLoading(false);
    }
  };

  return (
    <div className="row justify-content-center">
      <div className="col-md-8">
        <h2>Borrow a Book</h2>

        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label htmlFor="book_search" className="form-label">
              Search and Select Book
            </label>
            <div className="position-relative">
              <input
                type="text"
                className="form-control"
                id="book_search"
                value={bookSearch}
                onChange={(e) => {
                  setBookSearch(e.target.value);
                  setShowBookDropdown(true);
                }}
                onFocus={() => setShowBookDropdown(true)}
                placeholder="Type to search books by title or author..."
                required
              />
              {booksLoading && (
                <div className="position-absolute w-100" style={{ zIndex: 1000, background: 'white', padding: '10px' }}>
                  <div className="spinner-border spinner-border-sm" role="status">
                    <span className="visually-hidden">Searching...</span>
                  </div>
                </div>
              )}
              {showBookDropdown && !booksLoading && filteredBooks.length > 0 && (
                <div
                  className="list-group position-absolute w-100"
                  style={{ zIndex: 1000, maxHeight: '200px', overflowY: 'auto', marginTop: '2px' }}
                >
                  {filteredBooks.map((book) => (
                    <button
                      key={book.id}
                      type="button"
                      className="list-group-item list-group-item-action"
                      onClick={() => handleBookSelect(book)}
                    >
                      <strong>{book.title}</strong> by {book.author}
                    </button>
                  ))}
                </div>
              )}
              {showBookDropdown && !booksLoading && bookSearch && bookSearch.length > 0 && !formData.book_id && filteredBooks.length === 0 && (
                <div className="position-absolute w-100" style={{ zIndex: 1000, background: 'white', padding: '10px', border: '1px solid #ddd', marginTop: '2px' }}>
                  <small className="text-muted">No available books found</small>
                </div>
              )}
            </div>
            {formData.book_id && (
              <small className="form-text text-muted">
                Selected: {formData.book_title}
              </small>
            )}
          </div>

          <div className="mb-3">
            <label htmlFor="member_search" className="form-label">
              Search and Select Member
            </label>
            <div className="position-relative">
              <input
                type="text"
                className="form-control"
                id="member_search"
                value={memberSearch}
                onChange={(e) => {
                  setMemberSearch(e.target.value);
                  setShowMemberDropdown(true);
                }}
                onFocus={() => setShowMemberDropdown(true)}
                placeholder="Type to search members by name or email..."
                required
              />
              {membersLoading && (
                <div className="position-absolute w-100" style={{ zIndex: 1000, background: 'white', padding: '10px' }}>
                  <div className="spinner-border spinner-border-sm" role="status">
                    <span className="visually-hidden">Searching...</span>
                  </div>
                </div>
              )}
              {showMemberDropdown && !membersLoading && filteredMembers.length > 0 && (
                <div
                  className="list-group position-absolute w-100"
                  style={{ zIndex: 1000, maxHeight: '200px', overflowY: 'auto' }}
                >
                  {filteredMembers.map((member) => (
                    <button
                      key={member.id}
                      type="button"
                      className="list-group-item list-group-item-action"
                      onClick={() => handleMemberSelect(member)}
                    >
                      <strong>{member.name}</strong> ({member.email})
                    </button>
                  ))}
                </div>
              )}
              {showMemberDropdown && !membersLoading && memberSearch && filteredMembers.length === 0 && (
                <div className="position-absolute w-100" style={{ zIndex: 1000, background: 'white', padding: '10px', border: '1px solid #ddd' }}>
                  <small className="text-muted">No members found</small>
                </div>
              )}
            </div>
            {formData.member_id && (
              <small className="form-text text-muted">
                Selected: {formData.member_name}
              </small>
            )}
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading || !formData.book_id || !formData.member_id}>
            {loading ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                Processing...
              </>
            ) : (
              'Borrow Book'
            )}
          </button>
        </form>

      </div>
    </div>
  );
}

export default BorrowBook;
