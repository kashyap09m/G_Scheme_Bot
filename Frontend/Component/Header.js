import React from 'react';
import { Link } from 'react-router-dom';

// Simple inline styles for the header
// In a larger app, this would be in a separate .css file
const headerStyle = {
  background: '#004a99',
  color: '#fff',
  padding: '10px 0',
  boxShadow: '0 2px 5px rgba(0,0,0,0.2)',
};

const containerStyle = {
  maxWidth: '1100px',
  margin: 'auto',
  padding: '0 20px',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
};

const navStyle = {
  display: 'flex',
  gap: '20px',
};

const linkStyle = {
  color: '#fff',
  textDecoration: 'none',
  fontWeight: 'bold',
  fontSize: '16px',
};

const logoStyle = {
  ...linkStyle,
  fontSize: '24px',
};

const Header = () => {
  return (
    <header style={headerStyle}>
      <div style={containerStyle}>
        {/* Logo/Title links to the Dashboard */}
        <Link to="/" style={logoStyle}>
          G Scheme Bot
        </Link>

        {/* Navigation Links */}
        <nav style={navStyle}>
          <Link to="/dashboard" style={linkStyle}>
            Dashboard
          </Link>
          <Link to="/schemes/state/Maharashtra" style={linkStyle}>
            State Schemes
          </Link>
          <Link to="/login" style={linkStyle}>
            Login
          </Link>
          <Link to="/register" style={linkStyle}>
            Register
          </Link>
        </nav>
      </div>
    </header>
  );
};

export default Header;
