const express = require('express');
const router = express.Router();

// Middleware for validation
const validateMemberInput = (req, res, next) => {
    const { name, email } = req.body;
    if (!name || typeof name !== 'string' || name.trim().length === 0) {
        return res.status(400).json({ error: 'Name is required and must be a non-empty string' });
    }
    if (!email || typeof email !== 'string' || !email.includes('@')) {
        return res.status(400).json({ error: 'Valid email is required' });
    }
    next();
};

const validateMemberId = (req, res, next) => {
    const { id } = req.params;
    if (!id || isNaN(parseInt(id))) {
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
router.get('/', async (req, res) => {
    try {
        const response = await promisifyGrpcCall(client.ListMembers, {});
        res.json(response.members);
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
        const response = await promisifyGrpcCall(client.SearchMembers, { query: q });
        res.json(response.members);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

router.post('/', validateMemberInput, async (req, res) => {
    try {
        const { name, email } = req.body;
        const response = await promisifyGrpcCall(client.CreateMember, { name, email });
        res.status(201).json(response);
    } catch (error) {
        if (error.code === 6) { // ALREADY_EXISTS
            res.status(409).json({ error: error.message });
        } else {
            res.status(500).json({ error: error.message });
        }
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
        if (error.code === 5) { // NOT_FOUND
            res.status(404).json({ error: error.message });
        } else if (error.code === 6) { // ALREADY_EXISTS
            res.status(409).json({ error: error.message });
        } else {
            res.status(500).json({ error: error.message });
        }
    }
});

router.get('/:memberId/borrowed-books', validateMemberId, async (req, res) => {
    try {
        const { memberId } = req.params;
        const response = await promisifyGrpcCall(client.ListBorrowedBooks, {
            member_id: parseInt(memberId)
        });
        res.json(response.books);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = { router, setClient };