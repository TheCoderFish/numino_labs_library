const express = require('express');
const router = express.Router();
const { handleGrpcError, handleValidationError } = require('../utils/errorHandler');
const logger = require('../logger');
const config = require('../config');

// Middleware for validation
const validateBookInput = (req, res, next) => {
    const { title, author } = req.body;
    if (!title || typeof title !== 'string' || title.trim().length === 0) {
        return handleValidationError('INVALID_TITLE', 'Title is required and must be a non-empty string', res);
    }
    if (!author || typeof author !== 'string' || author.trim().length === 0) {
        return handleValidationError('INVALID_AUTHOR', 'Author is required and must be a non-empty string', res);
    }
    next();
};

const validateBookId = (req, res, next) => {
    const { id } = req.params;
    if (!id || isNaN(parseInt(id))) {
        return handleValidationError('INVALID_BOOK_ID', 'Valid book ID is required', res);
    }
    next();
};

// Import client from main server
let client;
const setClient = (grpcClient) => {
    client = grpcClient;
};

// Helper function to promisify gRPC calls
function promisifyGrpcCall(clientMethod, request) {
    return new Promise((resolve, reject) => {
        clientMethod.call(client, request, (error, response) => {
            if (error) {
                reject(error);
            } else {
                resolve(response);
            }
        });
    });
}

// Routes
router.get('/', async (req, res) => {
    logger.info('GET /api/books - ListBooks operation started');
    try {
        const response = await promisifyGrpcCall(client.ListBooks, {});
        logger.info(`GET /api/books - ListBooks operation successful, returned ${response.books.length} books`);
        res.json(response.books);
    } catch (error) {
        logger.error(`${config.ERROR_KEYWORD} GET /api/books - ListBooks operation failed: ${error.message}`);
        handleGrpcError(error, res);
    }
});

router.get('/search', async (req, res) => {
    const { q } = req.query;
    logger.info(`GET /api/books/search - SearchBooks operation started with query: ${q}`);
    try {
        if (!q) {
            logger.info('GET /api/books/search - No query provided, returning empty array');
            return res.json([]);
        }
        const response = await promisifyGrpcCall(client.SearchBooks, { query: q });
        logger.info(`GET /api/books/search - SearchBooks operation successful, found ${response.books.length} books`);
        res.json(response.books);
    } catch (error) {
        logger.error(`${config.ERROR_KEYWORD} GET /api/books/search - SearchBooks operation failed for query '${q}': ${error.message}`);
        handleGrpcError(error, res);
    }
});

router.post('/', validateBookInput, async (req, res) => {
    const { title, author } = req.body;
    logger.info(`POST /api/books - CreateBook operation started for title: ${title}, author: ${author}`);
    try {
        const response = await promisifyGrpcCall(client.CreateBook, { title, author });
        logger.info(`POST /api/books - CreateBook operation successful for book ID: ${response.book.id}`);
        res.status(201).json(response);
    } catch (error) {
        logger.error(`${config.ERROR_KEYWORD} POST /api/books - CreateBook operation failed for title '${title}': ${error.message}`);
        handleGrpcError(error, res);
    }
});

router.put('/:id', validateBookId, validateBookInput, async (req, res) => {
    const { id } = req.params;
    const { title, author } = req.body;
    logger.info(`PUT /api/books/${id} - UpdateBook operation started for book ID: ${id}, title: ${title}, author: ${author}`);
    try {
        const response = await promisifyGrpcCall(client.UpdateBook, {
            id: parseInt(id),
            title,
            author
        });
        logger.info(`PUT /api/books/${id} - UpdateBook operation successful for book ID: ${response.book.id}`);
        res.json(response);
    } catch (error) {
        logger.error(`${config.ERROR_KEYWORD} PUT /api/books/${id} - UpdateBook operation failed for ID ${id}: ${error.message}`);
        handleGrpcError(error, res);
    }
});

router.patch('/:id', validateBookId, async (req, res) => {
    const { id } = req.params;
    logger.info(`PATCH /api/books/${id} - PartialUpdateBook operation started for book ID: ${id}`);
    try {
        // Get current book data
        const listResponse = await promisifyGrpcCall(client.ListBooks, {});
        const currentBook = listResponse.books.find(book => book.id === parseInt(id));

        if (!currentBook) {
            logger.warning(`PATCH /api/books/${id} - Book not found for ID: ${id}`);
            return handleValidationError('BOOK_NOT_FOUND', 'Book not found', res, 404);
        }

        // Merge provided fields with current data
        const updatedTitle = req.body.title !== undefined ? req.body.title : currentBook.title;
        const updatedAuthor = req.body.author !== undefined ? req.body.author : currentBook.author;

        // Basic validation for merged data
        if (!updatedTitle || typeof updatedTitle !== 'string' || updatedTitle.trim().length === 0) {
            logger.warning(`PATCH /api/books/${id} - Invalid title provided`);
            return handleValidationError('INVALID_TITLE', 'Title must be a non-empty string', res);
        }
        if (!updatedAuthor || typeof updatedAuthor !== 'string' || updatedAuthor.trim().length === 0) {
            logger.warning(`PATCH /api/books/${id} - Invalid author provided`);
            return handleValidationError('INVALID_AUTHOR', 'Author must be a non-empty string', res);
        }

        // Update the book
        const response = await promisifyGrpcCall(client.UpdateBook, {
            id: parseInt(id),
            title: updatedTitle,
            author: updatedAuthor
        });
        logger.info(`PATCH /api/books/${id} - PartialUpdateBook operation successful for book ID: ${response.book.id}`);
        res.json(response);
    } catch (error) {
        logger.error(`${config.ERROR_KEYWORD} PATCH /api/books/${id} - PartialUpdateBook operation failed for ID ${id}: ${error.message}`);
        handleGrpcError(error, res);
    }
});

module.exports = { router, setClient };