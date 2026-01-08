const express = require('express');
const { register, login, getMe } = require('../controllers/authController');

// We import our authentication middleware
// const { protect } = require('../middleware/auth'); 
// Note: We'll define 'protect' later. It's used to secure routes.

const router = express.Router();

// @desc    Register a new user
// @route   POST /api/auth/register
// @access  Public
router.post('/register', register);

// @desc    Login a user
// @route   POST /api/auth/login
// @access  Public
router.post('/login', login);

// @desc    Get current logged in user (for profile/dashboard)
// @route   GET /api/auth/me
// @access  Private (We would add 'protect' middleware here)
// Example of a protected route:
// router.get('/me', protect, getMe);

// For now, we'll make a simple one:
router.get('/me', getMe); // This is a placeholder; it should be protected

module.exports = router;

