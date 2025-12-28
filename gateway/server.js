const express = require('express');
const cors = require('cors');
const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');

const app = express();
const PORT = 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Load proto file
const PROTO_PATH = __dirname + '/../backend/proto/library.proto';
const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
    keepCase: true,
    longs: String,
    enums: String,
    defaults: true,
    oneofs: true
});

const libraryProto = grpc.loadPackageDefinition(packageDefinition).library;

// Create gRPC client
const client = new libraryProto.LibraryService(
    'localhost:50051',
    grpc.credentials.createInsecure()
);

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

// REST API Routes

// Books
app.get('/api/books', async (req, res) => {
    try {
        const response = await promisifyGrpcCall(client.ListBooks, {});
        res.json(response.books);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.get('/api/books/search', async (req, res) => {
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

app.post('/api/books', async (req, res) => {
    try {
        const { title, author } = req.body;
        const response = await promisifyGrpcCall(client.CreateBook, { title, author });
        res.status(201).json(response);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.put('/api/books/:id', async (req, res) => {
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

// Members
app.post('/api/members', async (req, res) => {
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

app.put('/api/members/:id', async (req, res) => {
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

// Borrow/Return
app.post('/api/books/:bookId/borrow', async (req, res) => {
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

app.post('/api/books/:bookId/return', async (req, res) => {
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

app.get('/api/members', async (req, res) => {
    try {
        const response = await promisifyGrpcCall(client.ListMembers, {});
        res.json(response.members);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.get('/api/members/search', async (req, res) => {
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

app.get('/api/members/:memberId/borrowed-books', async (req, res) => {
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

app.listen(PORT, () => {
    console.log(`API Gateway running on http://localhost:${PORT}`);
});

