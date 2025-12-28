const express = require('express');
const router = express.Router();

// Middleware for validation
const validateBookId = (req, res, next) => {
    const { bookId } = req.params;
    if (!bookId || isNaN(parseInt(bookId))) {
        return res.status(400).json({ error: 'Valid book ID is required' });
    }
    next();
};

const validateBorrowInput = (req, res, next) => {
    const { member_id } = req.body;
    if (!member_id || isNaN(parseInt(member_id))) {
        return res.status(400).json({ error: 'Valid member ID is required' });
    }
    next();
};

const validateReturnInput = (req, res, next) => {
    const { member_id } = req.body;
    if (!member_id || isNaN(parseInt(member_id))) {
        return res.status(400).json({ error: 'Valid member ID is required' });
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
};

// Routes
router.post('/:bookId/borrow', validateBookId, validateBorrowInput, async (req, res) => {
    try {
        const { bookId } = req.params;
        const { member_id } = req.body;
        const response = await promisifyGrpcCall(client.BorrowBook, {
            book_id: parseInt(bookId),
            member_id: parseInt(member_id)
        });
        res.json(response);
    } catch (error) {
        if (error.code === 5) { // NOT_FOUND
            res.status(404).json({ error: error.message });
        } else if (error.code === 9) { // FAILED_PRECONDITION
            res.status(400).json({ error: error.message });
        } else {
            res.status(500).json({ error: error.message });
        }
    }
});

router.post('/:bookId/return', validateBookId, validateReturnInput, async (req, res) => {
    try {
        const { bookId } = req.params;
        const { member_id } = req.body;
        const response = await promisifyGrpcCall(client.ReturnBook, {
            book_id: parseInt(bookId),
            member_id: parseInt(member_id)
        });
        res.json(response);
    } catch (error) {
        if (error.code === 5) { // NOT_FOUND
            res.status(404).json({ error: error.message });
        } else if (error.code === 9) { // FAILED_PRECONDITION
            res.status(400).json({ error: error.message });
        } else if (error.code === 7) { // PERMISSION_DENIED
            res.status(403).json({ error: error.message });
        } else {
            res.status(500).json({ error: error.message });
        }
    }
});

module.exports = { router, setClient };