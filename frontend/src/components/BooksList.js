import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import { bookService, borrowService } from '../services/api';
import ConfirmationModal from './ConfirmationModal';
import DataTable from './DataTable';

function BooksList() {
  const [returning, setReturning] = useState(null);
  const [bookToReturn, setBookToReturn] = useState(null);

  const loadBooks = async (params) => {
    const response = await bookService.listBooks(params);
    return {
      data: response.data.books,
      next_cursor: response.data.next_cursor,
      has_more: response.data.has_more
    };
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
      // Reload will be handled by DataTable refresh
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to return book');
    } finally {
      setReturning(null);
    }
  };

  const handleReturnCancel = () => {
    setBookToReturn(null);
  };

  const columns = [
    { key: 'id', label: 'ID' },
    { key: 'title', label: 'Title' },
    { key: 'author', label: 'Author' },
    {
      key: 'status',
      label: 'Status',
      render: (book) => (
        <span className={`badge ${book.is_borrowed ? 'bg-danger' : 'bg-success'}`}>
          {book.is_borrowed ? 'Borrowed' : 'Available'}
        </span>
      )
    },
    {
      key: 'borrowedBy',
      label: 'Borrowed By',
      render: (book) => book.current_member_name || '-'
    }
  ];

  const actions = (book) => (
    <>
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
    </>
  );

  const filterOptions = [
    { value: 'all', label: 'All Books' },
    { value: 'available', label: 'Available' },
    { value: 'borrowed', label: 'Borrowed' }
  ];

  return (
    <>
      <DataTable
        title="Books"
        columns={columns}
        actions={actions}
        loadData={loadBooks}
        searchPlaceholder="Search by title or author..."
        hasFilter={true}
        filterOptions={filterOptions}
        initialFilter="all"
        addButton={{ text: 'Add Book', to: '/create-book' }}
      />

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
    </>
  );
}

export default BooksList;

