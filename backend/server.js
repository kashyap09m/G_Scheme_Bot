const express = require('express');
const dotenv = require('dotenv');
const cors = require('cors');
const connectDB = require('./config/db'); // We will create this file next

// Load environment variables (like MONGO_URI) from config.env
dotenv.config({ path: './config/config.env' });

// --- Connect to Database ---
// This function will be in ./config/db.js
// We'll call it to connect to MongoDB.
// connectDB();
console.log("--- MOCK: Database connection would be initiated here. ---");
console.log("--- Make sure to set MONGO_URI in a .env file later. ---");


// Initialize the Express app
const app = express();

// --- Middleware ---

// 1. Enable CORS (Cross-Origin Resource Sharing)
// This allows your React frontend (on localhost:3000)
// to make requests to this backend (on localhost:5000)
app.use(cors());

// 2. Body Parser
// This allows us to read JSON data from the request body (e.g., from req.body)
app.use(express.json());


// --- API Routes ---
// We link our route files to specific URL paths.
// All requests to '/api/auth' will be handled by the 'auth.js' router.
// All requests to '/api/schemes' will be handled by the 'schemes.js' router.
app.use('/api/auth', require('./routes/auth'));
app.use('/api/schemes', require('./routes/schemes'));


// --- Server Setup ---
const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
  console.log(`Backend server is running on port ${PORT}`);
});

// Handle unhandled promise rejections (good practice for database errors)
process.on('unhandledRejection', (err, promise) => {
  console.log(`Error: ${err.message}`);
  // In a real app, you'd close the server
  // server.close(() => process.exit(1));
});