const fs = require('fs');
const path = require('path');
const config = require('./config');

class Logger {
  constructor() {
    this.levels = {
      error: 0,
      warn: 1,
      info: 2,
      debug: 3
    };
    this.currentLevel = this.levels[config.LOG_LEVEL.toLowerCase()] || 2;
  }

  log(level, message) {
    if (this.levels[level] > this.currentLevel) return;

    const timestamp = new Date().toISOString();
    const logMessage = `${timestamp} - ${level.toUpperCase()} - ${message}\n`;

    // Console
    console.log(logMessage.trim());

    // File
    try {
      fs.appendFileSync(path.resolve(config.LOG_FILE), logMessage);
    } catch (err) {
      console.error('Failed to write to log file:', err);
    }
  }

  error(message) {
    this.log('error', message);
  }

  warn(message) {
    this.log('warn', message);
  }

  info(message) {
    this.log('info', message);
  }

  debug(message) {
    this.log('debug', message);
  }
}

const logger = new Logger();
module.exports = logger;