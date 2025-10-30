import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api'; // Our API service
import SchemeCard from '../components/SchemeCard'; // We will create this next

const Dashboard = () => {
  const [recommendedSchemes, setRecommendedSchemes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // We'll use a mock user name for the greeting
  // In a real app, you'd get this from localStorage
  const [userName, setUserName] = useState('User'); 
  
  const navigate = useNavigate();

  // useEffect runs once when the component loads
  useEffect(() => {
    // 1. Fetch recommended schemes
    const fetchRecommendations = async () => {
      try {
        setLoading(true);
        setError(null);
        // This hits the GET /api/schemes/recommend endpoint
        const res = await api.get('/schemes/recommend');
        setRecommendedSchemes(res.data.data);
      } catch (err) {
        console.error("Error fetching recommendations:", err);
        setError("Could not load your recommendations. Please try again later.");
      } finally {
        setLoading(false);
      }
    };

    // 2. Load user's name (mocked)
    // In a real app:
    // const user = JSON.parse(localStorage.getItem('user'));
    // if (user) {
    //   setUserName(user.name);
    // }
    setUserName('Valued User'); // Mock name

    fetchRecommendations();
  }, []); // The empty array [] means this runs only once on mount

  const goToChat = () => {
    navigate('/chat');
  };

  // Helper function to render content
  const renderContent = () => {
    if (loading) {
      return <p>Loading your recommendations...</p>;
    }
    if (error) {
      return <p style={{ color: 'red' }}>{error}</p>;
    }
    if (recommendedSchemes.length === 0) {
      return <p>No recommendations found for your profile. Try updating your profile details.</p>;
    }
    return (
      <div style={styles.schemesList}>
        {recommendedSchemes.map((scheme) => (
          <SchemeCard key={scheme._id} scheme={scheme} />
        ))}
      </div>
    );
  };

  return (
    <div style={styles.dashboardContainer}>
      <div style={styles.header}>
        <h2 style={styles.greeting}>Welcome, {userName}!</h2>
        <button onClick={goToChat} style={styles.chatButton}>
          💬 Chat with Me
        </button>
      </div>

      <h3 style={styles.sectionTitle}>Your Recommended Schemes</h3>
      
      {renderContent()}

      <hr style={styles.divider} />

      <h3 style={styles.sectionTitle}>Browse All Schemes</h3>
      <p>Not what you're looking for? You can also browse schemes by state.</p>
      <div style={styles.browseLinks}>
        {/* Placeholder links for state-wise browsing */}
        <a href="/schemes/state/Maharashtra">Maharashtra</a>
        <a href="/schemes/state/Delhi">Delhi</a>
        <a href="/schemes/state/Gujarat">Gujarat</a>
      </div>
    </div>
  );
};

// --- Styles ---
// Using inline styles to keep the file self-contained
const styles = {
  dashboardContainer: {
    padding: '20px',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: '15px',
    marginBottom: '20px',
  },
  greeting: {
    margin: 0,
    color: '#333',
  },
  chatButton: {
    padding: '10px 20px',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: 'bold',
  },
  sectionTitle: {
    borderBottom: '2px solid #004a99',
    paddingBottom: '5px',
    marginTop: '30px',
  },
  schemesList: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', // Responsive grid
    gap: '20px',
  },
  divider: {
    border: 0,
    borderTop: '1px solid #eee',
    margin: '40px 0',
  },
  browseLinks: {
    display: 'flex',
    gap: '15px',
  }
};

export default Dashboard;
