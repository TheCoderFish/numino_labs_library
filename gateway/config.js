require('dotenv').config();

module.exports = {
  // Server
  PORT: process.env.PORT || 3001,

  // Backend gRPC
  BACKEND_HOST: process.env.BACKEND_HOST || 'localhost',
  BACKEND_PORT: process.env.BACKEND_PORT || '50051',

  // Logging
  LOG_LEVEL: process.env.LOG_LEVEL || 'info',
  LOG_FILE: process.env.LOG_FILE || 'logs/gateway.log',

  // Email/SQS keyword
  ERROR_KEYWORD: process.env.ERROR_KEYWORD || '[GATEWAY_ERROR]',
};