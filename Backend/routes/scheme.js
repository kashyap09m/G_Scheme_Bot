const express = require('express');
const {
  getSchemes,
  getSchemeById,
  getRecommendedSchemes,
  getSchemesByState
} = require('../controllers/schemeController');

// We import our authentication middleware
// const { protect } = require('../middleware/auth');

const router = express.Router();

// @desc    Get all schemes (can be public)
// @route   GET /api/schemes
// @access  Public
router.get('/', getSchemes);

// @desc    Get recommended schemes for the logged-in user
// @route   GET /api/schemes/recommend
// @access  Private (Should be protected)
// We'll use a placeholder user for now, but this should be protected
router.get('/recommend', getRecommendedSchemes);

// @desc    Get schemes by state name
// @route   GET /api/schemes/state/:stateName
// @access  Public
router.get('/state/:stateName', getSchemesByState);

// @desc    Get a single scheme by its ID
// @route   GET /api/schemes/:id
// @access  Public
router.get('/:id', getSchemeById);

module.exports = router;