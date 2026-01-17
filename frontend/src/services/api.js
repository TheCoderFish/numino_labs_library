import axios from 'axios';

import { ENDPOINTS } from './endpoints';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const bookService = {
  listBooks: (params = {}) => api.get(ENDPOINTS.BOOKS, { params }),
  listRecentBooks: (limit = 20) => api.get(ENDPOINTS.BOOKS, { params: { limit, recent: true } }),
  createBook: (data) => api.post(ENDPOINTS.BOOKS, data),
  updateBook: (id, data) => api.put(`${ENDPOINTS.BOOKS}${id}/`, data),
  searchBooks: (query) => api.get(ENDPOINTS.BOOKS, { params: { search: query } }),
};

export const memberService = {
  listMembers: (params = {}) => api.get(ENDPOINTS.MEMBERS, { params }),
  createMember: (data) => api.post(ENDPOINTS.MEMBERS, data),
  updateMember: (id, data) => api.put(`${ENDPOINTS.MEMBERS}${id}/`, data),
  searchMembers: (query) => api.get(ENDPOINTS.MEMBERS, { params: { search: query } }),
};

export const borrowService = {
  borrowBook: (bookId, memberId) => api.post(`${ENDPOINTS.BOOKS}${bookId}/borrow/`, { member_id: memberId }),
  returnBook: (bookId, memberId) => api.post(`${ENDPOINTS.BOOKS}${bookId}/return/`, { member_id: memberId }),
  getBorrowedBooks: (memberId) => api.get(`${ENDPOINTS.MEMBERS}${memberId}/borrowed-books/`),
};

export default api;

