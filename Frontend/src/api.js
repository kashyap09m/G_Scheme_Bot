import axios from 'axios';

// Create an instance of axios for our backend API
const api = axios.create({
  // The base URL for all requests will be your Node.js server
  baseURL: 'http://localhost:5000/api',
});

/*
  --- Optional: Interceptor to add Auth Token ---
  
  This is a more advanced (but correct) way to handle authentication.
  Once a user logs in, you would save their JWT token to localStorage.
  This 'interceptor' will automatically grab that token and add it
  to the 'Authorization' header for every single request you make.
*/

api.interceptors.request.use(
  (config) => {
    // Get the token from localStorage (or wherever you store it)
    const token = localStorage.getItem('token');

    if (token) {
      // If the token exists, add it to the request headers
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    // Handle any request errors
    return Promise.reject(error);
  }
);

export default api;