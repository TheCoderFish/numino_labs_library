import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const bookService = {
  listBooks: (params = {}) => api.get('/books', { params }),
  listRecentBooks: (limit = 20) => api.get('/books/recent', { params: { limit } }),
  createBook: (data) => api.post('/books', data),
  updateBook: (id, data) => api.put(`/books/${id}`, data),
  searchBooks: (query) => api.get('/books/search', { params: { q: query } }),
};

export const memberService = {
  listMembers: (params = {}) => api.get('/members', { params }),
  createMember: (data) => api.post('/members', data),
  updateMember: (id, data) => api.put(`/members/${id}`, data),
  searchMembers: (query) => api.get('/members/search', { params: { q: query } }),
};

export const borrowService = {
  borrowBook: (bookId, memberId) => api.post(`/books/${bookId}/borrow`, { member_id: memberId }),
  returnBook: (bookId, memberId) => api.post(`/books/${bookId}/return`, { member_id: memberId }),
  getBorrowedBooks: (memberId) => api.get(`/members/${memberId}/borrowed-books`),
};

export default api;

