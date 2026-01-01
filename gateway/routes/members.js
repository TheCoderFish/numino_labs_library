const express = require('express');
const router = express.Router();
const { handleGrpcError, handleValidationError } = require('../utils/errorHandler');
const logger = require('../logger');
const config = require('../config');

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
    logger.info('GET /api/members - ListMembers operation started');
    try {
        const response = await promisifyGrpcCall(client.ListMembers, {});
        logger.info(`GET /api/members - ListMembers operation successful, returned ${response.members.length} members`);
        res.json(response.members);
    } catch (error) {
        logger.error(`${config.ERROR_KEYWORD} GET /api/members - ListMembers operation failed: ${error.message}`);
        handleGrpcError(error, res);
    }
});

router.get('/search', async (req, res) => {
    const { q } = req.query;
    logger.info(`GET /api/members/search - SearchMembers operation started with query: ${q}`);
    try {
        if (!q) {
            logger.info('GET /api/members/search - No query provided, returning empty array');
            return res.json([]);
        }
        const response = await promisifyGrpcCall(client.SearchMembers, { query: q });
        logger.info(`GET /api/members/search - SearchMembers operation successful, found ${response.members.length} members`);
        res.json(response.members);
    } catch (error) {
        logger.error(`${config.ERROR_KEYWORD} GET /api/members/search - SearchMembers operation failed for query '${q}': ${error.message}`);
        handleGrpcError(error, res);
    }
});

router.post('/', validateMemberInput, async (req, res) => {
    const { name, email } = req.body;
    logger.info(`POST /api/members - CreateMember operation started for name: ${name}, email: ${email}`);
    try {
        const response = await promisifyGrpcCall(client.CreateMember, { name, email });
        logger.info(`POST /api/members - CreateMember operation successful for member ID: ${response.member.id}`);
        res.status(201).json(response);
    } catch (error) {
        logger.error(`${config.ERROR_KEYWORD} POST /api/members - CreateMember operation failed for name '${name}': ${error.message}`);
        handleGrpcError(error, res);
    }
});

router.put('/:id', validateMemberId, validateMemberInput, async (req, res) => {
    const { id } = req.params;
    const { name, email } = req.body;
    logger.info(`PUT /api/members/${id} - UpdateMember operation started for member ID: ${id}, name: ${name}, email: ${email}`);
    try {
        const response = await promisifyGrpcCall(client.UpdateMember, {
            id: parseInt(id),
            name,
            email
        });
        logger.info(`PUT /api/members/${id} - UpdateMember operation successful for member ID: ${response.member.id}`);
        res.json(response);
    } catch (error) {
        logger.error(`${config.ERROR_KEYWORD} PUT /api/members/${id} - UpdateMember operation failed for ID ${id}: ${error.message}`);
        handleGrpcError(error, res);
    }
});

router.get('/:id/borrowed-books', validateMemberId, async (req, res) => {
    const { id } = req.params;
    logger.info(`GET /api/members/${id}/borrowed-books - ListBorrowedBooks operation started for member ID: ${id}`);
    try {
        const response = await promisifyGrpcCall(client.ListBorrowedBooks, {
            member_id: parseInt(id)
        });
        logger.info(`GET /api/members/${id}/borrowed-books - ListBorrowedBooks operation successful, returned ${response.books.length} books`);
        res.json(response.books);
    } catch (error) {
        logger.error(`${config.ERROR_KEYWORD} GET /api/members/${id}/borrowed-books - ListBorrowedBooks operation failed for member ${id}: ${error.message}`);
        handleGrpcError(error, res);
    }
});

module.exports = { router, setClient };