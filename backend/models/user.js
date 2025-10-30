const mongoose = require('mongoose');
const bcrypt = require('bcryptjs'); // We'll use this for password hashing

const UserSchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, 'Please provide a name'],
  },
  email: {
    type: String,
    required: [true, 'Please provide an email'],
    unique: true,
    match: [
      /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/,
      'Please add a valid email',
    ],
  },
  password: {
    type: String,
    required: [true, 'Please add a password'],
    minlength: 6,
    select: false, // This will hide the password from default queries
  },
  age: {
    type: Number,
    required: [true, 'Please provide your age'],
  },
  gender: {
    type: String,
    enum: ['Male', 'Female', 'Other'],
    required: [true, 'Please provide your gender'],
  },
  profession: {
    type: String,
    enum: ['Student', 'Farmer', 'Businessman', 'Housewife', 'Fisherman', 'Other'],
    required: [true, 'Please provide your profession'],
  },
  salary: {
    type: Number,
    required: [true, 'Please provide your approximate annual salary'],
    default: 0,
  },
  state: {
    type: String,
    required: [true, 'Please provide your state'],
  },
  // This array will store the names of documents the user has
  uploaded_documents: {
    type: [String],
    default: [],
  },
  createdAt: {
    type: Date,
    default: Date.now,
  },
});

// --- Mongoose Middleware ---

// Encrypt password using bcrypt before saving a new user
UserSchema.pre('save', async function (next) {
  // Only run this function if password was actually modified
  if (!this.isModified('password')) {
    next();
  }

  // Generate salt
  const salt = await bcrypt.genSalt(10);
  // Hash the password
  this.password = await bcrypt.hash(this.password, salt);
  next();
});

// Method to compare entered password with the hashed password in the database
UserSchema.methods.matchPassword = async function (enteredPassword) {
  // 'this.password' has the hashed password (because we'll 'select' it in the controller)
  return await bcrypt.compare(enteredPassword, this.password);
};

module.exports = mongoose.model('User', UserSchema);
