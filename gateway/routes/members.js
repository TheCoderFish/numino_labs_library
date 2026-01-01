const express = require('express');
const router = express.Router();
const { handleGrpcError, handleValidationError } = require('../utils/errorHandler');

// Middleware for validation
const validateMemberInput = (req, res, next) => {
    const { name, email } = req.body;
    if (!name || typeof name !== 'string' || name.trim().length === 0) {
        return handleValidationError('INVALID_NAME', 'Name is required and must be a non-empty string', res);
    }
    if (!email || typeof email !== 'string' || !email.includes('@')) {
        return handleValidationError('INVALID_EMAIL', 'Valid email is required', res);
    }
    next();
};

const validateMemberId = (req, res, next) => {
    const { id } = req.params;
    if (!id || isNaN(parseInt(id))) {
        return handleValidationError('INVALID_MEMBER_ID', 'Valid member ID is required', res);
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
router.get('/', async (req, res) => {
    try {
        const response = await promisifyGrpcCall(client.ListMembers, {});
        res.json(response.members);
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
        const response = await promisifyGrpcCall(client.SearchMembers, { query: q });
        res.json(response.members);
    } catch (error) {
        handleGrpcError(error, res);
    }
});

router.post('/', validateMemberInput, async (req, res) => {
    try {
        const { name, email } = req.body;
        const response = await promisifyGrpcCall(client.CreateMember, { name, email });
        res.status(201).json(response);
    } catch (error) {
        handleGrpcError(error, res);
    }
});

router.put('/:id', validateMemberId, validateMemberInput, async (req, res) => {
    try {
        const { id } = req.params;
        const { name, email } = req.body;
        const response = await promisifyGrpcCall(client.UpdateMember, {
            id: parseInt(id),
            name,
            email
        });
        res.json(response);
    } catch (error) {
        handleGrpcError(error, res);
    }
});

router.get('/:id/borrowed-books', validateMemberId, async (req, res) => {
    try {
        const { id } = req.params;
        const response = await promisifyGrpcCall(client.ListBorrowedBooks, {
            member_id: parseInt(id)
        });
        res.json(response.books);
    } catch (error) {
        handleGrpcError(error, res);
    }
});

module.exports = { router, setClient };