const express = require('express');
const router = express.Router();
const { handleGrpcError, handleValidationError } = require('../utils/errorHandler');
const logger = require('../logger');
const config = require('../config');

// Middleware for validation
const validateBookId = (req, res, next) => {
    const { bookId } = req.params;
    if (!bookId || isNaN(parseInt(bookId))) {
        return handleValidationError('INVALID_BOOK_ID', 'Valid book ID is required', res);
    }
    next();
};

const validateBorrowInput = (req, res, next) => {
    const { member_id } = req.body;
    if (!member_id || isNaN(parseInt(member_id))) {
        return handleValidationError('INVALID_MEMBER_ID', 'Valid member ID is required', res);
    }
    next();
};

const validateReturnInput = (req, res, next) => {
    const { member_id } = req.body;
    if (!member_id || isNaN(parseInt(member_id))) {
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

// Helper function to convert protobuf timestamp to ISO string
function timestampToISOString(ts) {
    if (!ts || !ts.seconds) return null;
    return new Date(ts.seconds * 1000 + (ts.nanos || 0) / 1000000).toISOString();
}

// Helper function to convert ledger entry to plain object
function convertLedgerEntry(entry) {
    if (!entry) return null;
    return {
        id: entry.id,
        book_id: entry.book_id,
        member_id: entry.member_id,
        action_type: entry.action_type,
        log_date: timestampToISOString(entry.log_date),
        due_date_snapshot: timestampToISOString(entry.due_date_snapshot)
    };
}

// Routes
router.post('/:bookId/borrow', validateBookId, validateBorrowInput, async (req, res) => {
    const { bookId } = req.params;
    const { member_id } = req.body;
    logger.info(`POST /api/books/${bookId}/borrow - BorrowBook operation started for book ID: ${bookId}, member ID: ${member_id}`);
    try {
        const response = await promisifyGrpcCall(client.BorrowBook, {
            book_id: parseInt(bookId),
            member_id: parseInt(member_id)
        });
        const plainResponse = {
            success: response.success,
            message: response.message,
            ledger_entry: convertLedgerEntry(response.ledger_entry)
        };
        logger.info(`POST /api/books/${bookId}/borrow - BorrowBook operation successful, ledger entry ID: ${response.ledger_entry.id}`);
        res.json(plainResponse);
    } catch (error) {
        logger.error(`${config.ERROR_KEYWORD} POST /api/books/${bookId}/borrow - BorrowBook operation failed for book ${bookId}, member ${member_id}: ${error.message}`);
        handleGrpcError(error, res);
    }
});

router.post('/:bookId/return', validateBookId, validateReturnInput, async (req, res) => {
    const { bookId } = req.params;
    const { member_id } = req.body;
    logger.info(`POST /api/books/${bookId}/return - ReturnBook operation started for book ID: ${bookId}, member ID: ${member_id}`);
    try {
        const response = await promisifyGrpcCall(client.ReturnBook, {
            book_id: parseInt(bookId),
            member_id: parseInt(member_id)
        });
        const plainResponse = {
            success: response.success,
            message: response.message,
            ledger_entry: convertLedgerEntry(response.ledger_entry)
        };
        logger.info(`POST /api/books/${bookId}/return - ReturnBook operation successful, ledger entry ID: ${response.ledger_entry.id}`);
        res.json(plainResponse);
    } catch (error) {
        logger.error(`${config.ERROR_KEYWORD} POST /api/books/${bookId}/return - ReturnBook operation failed for book ${bookId}, member ${member_id}: ${error.message}`);
        handleGrpcError(error, res);
    }
});

module.exports = { router, setClient };