import React from 'react';
import { Routes, Route } from 'react-router-dom';

// Import Layout Component
import Header from './components/Header';

// Import Page Components
import Dashboard from './pages/Dashboard';
import Register from './pages/Register';
import Login from './pages/Login';
import SchemeDetail from './pages/SchemeDetail';
import ChatbotPage from './pages/ChatbotPage';
import StateSchemes from './pages/StateSchemes';

// This is the main component for your application
function App() {
  return (
    <div className="App">
      {/* The Header component will appear on every page */}
      <Header />

      {/* The 'container' class adds padding and centers the content */}
      <div className="container">
        {/*
          <Routes> defines all the possible pages (routes)
          The 'element' prop is the component that will be rendered
          for that specific 'path'.
        */}
        <Routes>
          {/* Default page (e.g., http://localhost:3000/) */}
          <Route path="/" element={<Dashboard />} />

          {/* Page for http://localhost:3000/login */}
          <Route path="/login" element={<Login />} />

          {/* Page for http://localhost:3000/register */}
          <Route path="/register" element={<Register />} />

          {/* Page for http://localhost:3000/dashboard */}
          <Route path="/dashboard" element={<Dashboard />} />

          {/* Dynamic route for state-wise schemes */}
          {/* :stateName is a URL parameter */}
          {/* e.g., http://localhost:3000/schemes/state/Maharashtra */}
          <Route path="/schemes/state/:stateName" element={<StateSchemes />} />

          {/* Dynamic route for a single scheme's details */}
          {/* :id is a URL parameter */}
          {/* e.g., http://localhost:3000/schemes/60c72b965f1b2c001f8e4d3a */}
          <Route path="/schemes/:id" element={<SchemeDetail />} />

          {/* Page for http://localhost:3000/chat */}
          <Route path="/chat" element={<ChatbotPage />} />

          {/* A simple "Not Found" page for any other URL */}
          <Route path="*" element={<h2>404 - Page Not Found</h2>} />
        </Routes>
      </div>
    </div>
  );
}

export default App;