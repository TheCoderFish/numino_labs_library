const express = require('express');
const router = express.Router();

// Middleware for validation
const validateBookInput = (req, res, next) => {
    const { title, author } = req.body;
    if (!title || typeof title !== 'string' || title.trim().length === 0) {
        return res.status(400).json({ error: 'Title is required and must be a non-empty string' });
    }
    if (!author || typeof author !== 'string' || author.trim().length === 0) {
        return res.status(400).json({ error: 'Author is required and must be a non-empty string' });
    }
    next();
};

const validateBookId = (req, res, next) => {
    const { id } = req.params;
    if (!id || isNaN(parseInt(id))) {
        return res.status(400).json({ error: 'Valid book ID is required' });
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
        res.status(500).json({ error: error.message });
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
        res.status(500).json({ error: error.message });
    }
});

router.post('/', validateBookInput, async (req, res) => {
    try {
        const { title, author } = req.body;
        const response = await promisifyGrpcCall(client.CreateBook, { title, author });
        res.status(201).json(response);
    } catch (error) {
        res.status(500).json({ error: error.message });
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
        if (error.code === 5) { // NOT_FOUND
            res.status(404).json({ error: error.message });
        } else {
            res.status(500).json({ error: error.message });
        }
    }
});

router.patch('/:id', validateBookId, async (req, res) => {
    try {
        const { id } = req.params;

        // Get current book data
        const listResponse = await promisifyGrpcCall(client.ListBooks, {});
        const currentBook = listResponse.books.find(book => book.id === parseInt(id));

        if (!currentBook) {
            return res.status(404).json({ error: 'Book not found' });
        }

        // Merge provided fields with current data
        const updatedTitle = req.body.title !== undefined ? req.body.title : currentBook.title;
        const updatedAuthor = req.body.author !== undefined ? req.body.author : currentBook.author;

        // Basic validation for merged data
        if (!updatedTitle || typeof updatedTitle !== 'string' || updatedTitle.trim().length === 0) {
            return res.status(400).json({ error: 'Title must be a non-empty string' });
        }
        if (!updatedAuthor || typeof updatedAuthor !== 'string' || updatedAuthor.trim().length === 0) {
            return res.status(400).json({ error: 'Author must be a non-empty string' });
        }

        // Update the book
        const response = await promisifyGrpcCall(client.UpdateBook, {
            id: parseInt(id),
            title: updatedTitle,
            author: updatedAuthor
        });
        res.json(response);
    } catch (error) {
        if (error.code === 5) { // NOT_FOUND
            res.status(404).json({ error: error.message });
        } else {
            res.status(500).json({ error: error.message });
        }
    }
});

module.exports = { router, setClient };