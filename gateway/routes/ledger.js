const express = require('express');
const router = express.Router();
const { handleGrpcError, handleValidationError } = require('../utils/errorHandler');

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
    if (!ts) return null;
    return ts.toDate().toISOString();
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
    try {
        const { bookId } = req.params;
        const { member_id } = req.body;
        const response = await promisifyGrpcCall(client.BorrowBook, {
            book_id: parseInt(bookId),
            member_id: parseInt(member_id)
        });
        const plainResponse = {
            success: response.success,
            message: response.message,
            ledger_entry: convertLedgerEntry(response.ledger_entry)
        };
        res.json(plainResponse);
    } catch (error) {
        handleGrpcError(error, res);
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
        const plainResponse = {
            success: response.success,
            message: response.message,
            ledger_entry: convertLedgerEntry(response.ledger_entry)
        };
        res.json(plainResponse);
    } catch (error) {
        handleGrpcError(error, res);
    }
});

module.exports = { router, setClient };