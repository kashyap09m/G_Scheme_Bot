// const User = require('../models/User'); // We would use this in a real app
// const jwt = require('jsonwebtoken'); // We would use this in a real app

// --- Helper Functions (Placeholders) ---

// In a real app, this would create and sign a JWT token
const getSignedJwtToken = (userId) => {
  // return jwt.sign({ id: userId }, process.env.JWT_SECRET, {
  //   expiresIn: process.env.JWT_EXPIRE,
  // });
  return `mock_jwt_token_for_user_${userId}`;
};

// In a real app, this would send the token in a cookie
const sendTokenResponse = (user, statusCode, res) => {
  const token = getSignedJwtToken(user._id);

  res.status(statusCode).json({
    success: true,
    token,
    data: user, // Send user data back
  });
};

// --- Controller Functions ---

// @desc    Register user
// @route   POST /api/auth/register
exports.register = async (req, res, next) => {
  try {
    const { name, email, password, age, gender, profession, state, salary } = req.body;

    // --- MOCK LOGIC ---
    // In a real app, you would do:
    // const user = await User.create({
    //   name, email, password, age, gender, profession, state, salary
    // });
    //
    // But for now, we'll just create a fake user object
    
    console.log('User registration data received:', req.body);
    
    const fakeUser = {
      _id: 'mockUserId123',
      name,
      email,
      age,
      gender,
      profession,
      state,
      salary,
      uploaded_documents: ['Aadhaar Card'] // Give a default doc
    };

    // Send back a successful response with the fake user and token
    sendTokenResponse(fakeUser, 201, res);

  } catch (err) {
    console.error('Registration error:', err);
    res.status(400).json({ success: false, error: err.message });
  }
};

// @desc    Login user
// @route   POST /api/auth/login
exports.login = async (req, res, next) => {
  try {
    const { email, password } = req.body;

    // 1. Validation
    if (!email || !password) {
      return res.status(400).json({ success: false, error: 'Please provide email and password' });
    }

    // --- MOCK LOGIC ---
    // In a real app, you would find the user and check their password:
    //
    // 1. Find user by email
    // const user = await User.findOne({ email }).select('+password');
    // if (!user) {
    //   return res.status(401).json({ success: false, error: 'Invalid credentials' });
    // }
    //
    // 2. Check if password matches
    // const isMatch = await user.matchPassword(password);
    // if (!isMatch) {
    //   return res.status(401).json({ success: false, error: 'Invalid credentials' });
    // }
    
    console.log('User login attempt:', email);
    
    // 3. Since this is a mock, we'll just create a fake user
    const fakeUser = {
      _id: 'mockUserId123',
      name: 'Mock User',
      email: email,
      age: 25,
      gender: 'Male',
      profession: 'Student',
      state: 'Maharashtra',
      salary: 50000,
      uploaded_documents: ['Aadhaar Card', 'PAN Card']
    };

    // 4. Send token response
    sendTokenResponse(fakeUser, 200, res);

  } catch (err) {
    console.error('Login error:', err);
    res.status(500).json({ success: false, error: 'Server Error' });
  }
};

// @desc    Get current logged in user
// @route   GET /api/auth/me
exports.getMe = async (req, res, next) => {
  // --- MOCK LOGIC ---
  // In a real app, this route would be protected by middleware
  // that decodes the JWT token and attaches the user to `req.user`.
  //
  // const user = await User.findById(req.user.id);
  // res.status(200).json({ success: true, data: user });

  console.log('Fetching mock user profile for /me');
  
  // For now, just return a mock user
  const mockUser = {
    _id: 'mockUserId123',
    name: 'Mock User',
    email: 'mock@example.com',
    age: 25,
    gender: 'Male',
    profession: 'Student',
    state: 'Maharashtra',
    salary: 50000,
    uploaded_documents: ['Aadhaar Card', 'PAN Card']
  };

  res.status(200).json({
    success: true,
    data: mockUser,
  });
};
