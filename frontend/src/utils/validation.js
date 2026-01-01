/**
 * Validation utilities for form inputs
 */

/**
 * Trims whitespace from a string
 */
export const trimWhitespace = (value) => {
  if (typeof value !== 'string') return value;
  return value.trim();
};

/**
 * Validates that a string is not empty after trimming
 */
export const isNotEmpty = (value) => {
  if (typeof value !== 'string') return false;
  return trimWhitespace(value).length > 0;
};

/**
 * Enhanced email validation
 * Validates email format beyond native HTML5 validation
 */
export const isValidEmail = (email) => {
  if (!email || typeof email !== 'string') return false;
  
  const trimmed = trimWhitespace(email);
  if (trimmed.length === 0) return false;
  
  // RFC 5322 compliant regex (simplified but comprehensive)
  const emailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
  
  return emailRegex.test(trimmed);
};

/**
 * Validates book title (non-empty, reasonable length)
 */
export const validateBookTitle = (title) => {
  const trimmed = trimWhitespace(title);
  if (!isNotEmpty(trimmed)) {
    return { valid: false, error: 'Title is required' };
  }
  if (trimmed.length > 500) {
    return { valid: false, error: 'Title must be less than 500 characters' };
  }
  return { valid: true };
};

/**
 * Validates book author (non-empty, reasonable length)
 */
export const validateBookAuthor = (author) => {
  const trimmed = trimWhitespace(author);
  if (!isNotEmpty(trimmed)) {
    return { valid: false, error: 'Author is required' };
  }
  if (trimmed.length > 200) {
    return { valid: false, error: 'Author name must be less than 200 characters' };
  }
  return { valid: true };
};

/**
 * Validates member name (non-empty, reasonable length)
 */
export const validateMemberName = (name) => {
  const trimmed = trimWhitespace(name);
  if (!isNotEmpty(trimmed)) {
    return { valid: false, error: 'Name is required' };
  }
  if (trimmed.length > 200) {
    return { valid: false, error: 'Name must be less than 200 characters' };
  }
  return { valid: true };
};

/**
 * Validates member email
 */
export const validateMemberEmail = (email) => {
  const trimmed = trimWhitespace(email);
  if (!isNotEmpty(trimmed)) {
    return { valid: false, error: 'Email is required' };
  }
  if (!isValidEmail(trimmed)) {
    return { valid: false, error: 'Please enter a valid email address' };
  }
  return { valid: true };
};

/**
 * Validates book form data
 */
export const validateBookForm = (formData) => {
  const errors = {};
  
  const titleValidation = validateBookTitle(formData.title);
  if (!titleValidation.valid) {
    errors.title = titleValidation.error;
  }
  
  const authorValidation = validateBookAuthor(formData.author);
  if (!authorValidation.valid) {
    errors.author = authorValidation.error;
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

/**
 * Validates member form data
 */
export const validateMemberForm = (formData) => {
  const errors = {};
  
  const nameValidation = validateMemberName(formData.name);
  if (!nameValidation.valid) {
    errors.name = nameValidation.error;
  }
  
  const emailValidation = validateMemberEmail(formData.email);
  if (!emailValidation.valid) {
    errors.email = emailValidation.error;
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

