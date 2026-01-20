import axios from 'axios';

import { ENDPOINTS } from './endpoints';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Extract cursor parameter from a paginated URL
 * @param {string} url - Full URL with cursor parameter
 * @returns {string|null} - Cursor value or null
 */
const extractCursor = (url) => {
  if (!url) return null;
  try {
    const urlObj = new URL(url);
    return urlObj.searchParams.get('cursor');
  } catch (e) {
    return null;
  }
};

/**
 * Transform DRF paginated response to frontend format
 * @param {object} response - Axios response with DRF pagination
 * @returns {object} - Transformed response {data, next_cursor, has_more}
 */
const transformPaginatedResponse = (response) => {
  // Check if response has pagination structure
  if (response.data && typeof response.data === 'object' && 'results' in response.data) {
    return {
      data: response.data.results || [],
      next_cursor: extractCursor(response.data.next),
      has_more: !!response.data.next
    };
  }
  // Fallback for non-paginated responses
  return {
    data: Array.isArray(response.data) ? response.data : [],
    next_cursor: null,
    has_more: false
  };
};

export const bookService = {
  listBooks: async (params = {}) => {
    const response = await api.get(ENDPOINTS.BOOKS, { params });
    return transformPaginatedResponse(response);
  },
  listRecentBooks: async (limit = 20) => {
    const response = await api.get(ENDPOINTS.BOOKS, { params: { page_size: limit } });
    return transformPaginatedResponse(response);
  },
  createBook: (data) => api.post(ENDPOINTS.BOOKS, data),
  updateBook: (id, data) => api.put(`${ENDPOINTS.BOOKS}${id}/`, data),
  searchBooks: async (query, additionalParams = {}) => {
    const response = await api.get(ENDPOINTS.BOOKS, { params: { search: query, ...additionalParams } });
    return transformPaginatedResponse(response);
  },
};

export const memberService = {
  listMembers: async (params = {}) => {
    const response = await api.get(ENDPOINTS.MEMBERS, { params });
    return transformPaginatedResponse(response);
  },
  createMember: (data) => api.post(ENDPOINTS.MEMBERS, data),
  updateMember: (id, data) => api.put(`${ENDPOINTS.MEMBERS}${id}/`, data),
  searchMembers: async (query) => {
    const response = await api.get(ENDPOINTS.MEMBERS, { params: { search: query } });
    return transformPaginatedResponse(response);
  },
  checkEmail: async (email) => {
    const response = await api.get(`${ENDPOINTS.MEMBERS}check-email/`, { params: { email } });
    return response.data;
  },
};

export const borrowService = {
  borrowBook: (bookId, memberId) => api.post(`${ENDPOINTS.BOOKS}${bookId}/borrow/`, { member_id: memberId }),
  returnBook: (bookId, memberId) => api.post(`${ENDPOINTS.BOOKS}${bookId}/return/`, { member_id: memberId }),
  getBorrowedBooks: (memberId) => api.get(`${ENDPOINTS.MEMBERS}${memberId}/borrowed-books/`),
};

export default api;
