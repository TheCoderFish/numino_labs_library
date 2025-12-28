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

// Import routes
const { router: bookRoutes, setClient: setBookClient } = require('./routes/books');
const { router: memberRoutes, setClient: setMemberClient } = require('./routes/members');
const { router: ledgerRoutes, setClient: setLedgerClient } = require('./routes/ledger');

// Set client for routes
setBookClient(client);
setMemberClient(client);
setLedgerClient(client);

// Use routes
app.use('/api/books', bookRoutes);
app.use('/api/members', memberRoutes);
app.use('/api/books', ledgerRoutes); // Borrow/return routes are under /api/books/:bookId

app.listen(PORT, () => {
    console.log(`API Gateway running on http://localhost:${PORT}`);
});

