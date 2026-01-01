const express = require('express');
const router = express.Router();
const { handleGrpcError, handleValidationError } = require('../utils/errorHandler');

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
    try {
        const response = await promisifyGrpcCall(client.ListBooks, {});
        res.json(response.books);
    } catch (error) {
        handleGrpcError(error, res);
    }
});

router.get('/search', async (req, res) => {
    try {
        const { q } = req.query;
        if (!q) {
            return res.json([]);
        }
        const response = await promisifyGrpcCall(client.SearchBooks, { query: q });
        res.json(response.books);
    } catch (error) {
        handleGrpcError(error, res);
    }
});

router.post('/', validateBookInput, async (req, res) => {
    try {
        const { title, author } = req.body;
        const response = await promisifyGrpcCall(client.CreateBook, { title, author });
        res.status(201).json(response);
    } catch (error) {
        handleGrpcError(error, res);
    }
});

router.put('/:id', validateBookId, validateBookInput, async (req, res) => {
    try {
        const { id } = req.params;
        const { title, author } = req.body;
        const response = await promisifyGrpcCall(client.UpdateBook, {
            id: parseInt(id),
            title,
            author
        });
        res.json(response);
    } catch (error) {
        handleGrpcError(error, res);
    }
});

router.patch('/:id', validateBookId, async (req, res) => {
    try {
        const { id } = req.params;

        // Get current book data
        const listResponse = await promisifyGrpcCall(client.ListBooks, {});
        const currentBook = listResponse.books.find(book => book.id === parseInt(id));

        if (!currentBook) {
            return handleValidationError('BOOK_NOT_FOUND', 'Book not found', res, 404);
        }

        // Merge provided fields with current data
        const updatedTitle = req.body.title !== undefined ? req.body.title : currentBook.title;
        const updatedAuthor = req.body.author !== undefined ? req.body.author : currentBook.author;

        // Basic validation for merged data
        if (!updatedTitle || typeof updatedTitle !== 'string' || updatedTitle.trim().length === 0) {
            return handleValidationError('INVALID_TITLE', 'Title must be a non-empty string', res);
        }
        if (!updatedAuthor || typeof updatedAuthor !== 'string' || updatedAuthor.trim().length === 0) {
            return handleValidationError('INVALID_AUTHOR', 'Author must be a non-empty string', res);
        }

        // Update the book
        const response = await promisifyGrpcCall(client.UpdateBook, {
            id: parseInt(id),
            title: updatedTitle,
            author: updatedAuthor
        });
        res.json(response);
    } catch (error) {
        handleGrpcError(error, res);
    }
});

module.exports = { router, setClient };