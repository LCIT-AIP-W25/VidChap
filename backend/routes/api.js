const express = require('express');
const router = express.Router();
const { getExample, createExample } = require('../controllers/apiController');

// API Endpoints
router.get('/example', getExample);
router.post('/example', createExample);

module.exports = router;
