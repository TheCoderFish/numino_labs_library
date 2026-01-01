const grpc = require('@grpc/grpc-js');

function handleGrpcError(error, res) {
    let status = 500;
    let code = 'INTERNAL_ERROR';
    let message = 'An internal server error occurred';

    if (error.code !== undefined) {
        // Map gRPC status codes to HTTP status codes
        switch (error.code) {
            case grpc.status.NOT_FOUND:
                status = 404;
                code = 'NOT_FOUND';
                message = 'Resource not found';
                break;
            case grpc.status.INVALID_ARGUMENT:
                status = 400;
                code = 'INVALID_ARGUMENT';
                message = 'Invalid request parameters';
                break;
            case grpc.status.ALREADY_EXISTS:
                status = 409;
                code = 'ALREADY_EXISTS';
                message = 'Resource already exists';
                break;
            case grpc.status.FAILED_PRECONDITION:
                status = 412;
                code = 'FAILED_PRECONDITION';
                message = 'Precondition failed';
                break;
            case grpc.status.PERMISSION_DENIED:
                status = 403;
                code = 'PERMISSION_DENIED';
                message = 'Permission denied';
                break;
            case grpc.status.UNAVAILABLE:
                status = 503;
                code = 'SERVICE_UNAVAILABLE';
                message = 'Service unavailable';
                break;
            default:
                status = 500;
                code = 'INTERNAL_ERROR';
                message = 'An internal error occurred';
        }
    }

    // Try to parse structured details from gRPC error
    if (error.details) {
        try {
            const details = JSON.parse(error.details);
            code = details.code || code;
            message = details.message || message;
        } catch (e) {
            // If not JSON, use as message
            message = error.details;
        }
    }

    res.status(status).json({
        error: {
            code: code,
            message: message
        }
    });
}

function handleValidationError(code, message, res, status = 400) {
    res.status(status).json({
        error: {
            code: code,
            message: message
        }
    });
}

module.exports = { handleGrpcError, handleValidationError };