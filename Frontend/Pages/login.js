import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api'; // Our centralized axios instance

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate(); // Hook to redirect user after login

  const { email, password } = formData;

  // This function updates the state when the user types
  const onChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // This function is called when the form is submitted
  const onSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      // Send the login data to our backend's /auth/login endpoint
      const res = await api.post('/auth/login', formData);

      console.log('Login successful:', res.data);
      
      // --- IMPORTANT ---
      // This is where you would save the user's token and data
      // localStorage.setItem('token', res.data.token);
      // localStorage.setItem('user', JSON.stringify(res.data.data));

      // For now, we'll just show an alert and redirect
      alert('Login successful!');
      navigate('/dashboard'); // Redirect to the user's dashboard

    } catch (err) {
      console.error('Login error:', err.response ? err.response.data : err.message);
      // Set the error message to display to the user
      setError(err.response?.data?.error || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false); // Re-enable the button
    }
  };

  return (
    <div>
      <h2 style={{ textAlign: 'center', margin: '20px 0' }}>Account Login</h2>
      
      <form onSubmit={onSubmit}>
        {error && <div style={{ color: 'red', marginBottom: '10px', textAlign: 'center' }}>{error}</div>}
        
        <div>
          <label>Email:</label>
          <input
            type="email"
            name="email"
            value={email}
            onChange={onChange}
            required
            disabled={loading}
          />
        </div>
        
        <div>
          <label>Password:</label>
          <input
            type="password"
            name="password"
            value={password}
            onChange={onChange}
            required
            disabled={loading}
          />
        </div>
        
        <button type="submit" disabled={loading}>
          {loading ? 'Logging in...' : 'Login'}
        </button>

        <p style={{ textAlign: 'center' }}>
          Don't have an account? <Link to="/register">Register here</Link>
        </p>
      </form>
    </div>
  );
};

export default Login;