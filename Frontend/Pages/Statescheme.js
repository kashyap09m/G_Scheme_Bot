import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from '../services/api';
import SchemeCard from '../components/SchemeCard';

const StateSchemes = () => {
  const [schemes, setSchemes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Get the 'stateName' from the URL (e.g., /schemes/state/Maharashtra)
  const { stateName } = useParams();

  useEffect(() => {
    // This function runs when the component loads or 'stateName' changes
    const fetchSchemesByState = async () => {
      try {
        setLoading(true);
        setError(null);
        // This hits the GET /api/schemes/state/:stateName endpoint
        const res = await api.get(`/schemes/state/${stateName}`);
        setSchemes(res.data.data);
      } catch (err) {
        console.error(`Error fetching schemes for ${stateName}:`, err);
        setError("Could not load schemes for this state.");
      } finally {
        setLoading(false);
      }
    };

    fetchSchemesByState();
  }, [stateName]); // Re-run this effect if the stateName in the URL changes

  // Helper function to render content
  const renderContent = () => {
    if (loading) {
      return <p>Loading schemes...</p>;
    }
    if (error) {
      return <p style={{ color: 'red' }}>{error}</p>;
    }
    if (schemes.length === 0) {
      return <p>No schemes found for {stateName} (this includes National schemes).</p>;
    }
    return (
      <div style={styles.schemesList}>
        {schemes.map((scheme) => (
          <SchemeCard key={scheme._id} scheme={scheme} />
        ))}
      </div>
    );
  };

  return (
    <div style={styles.container}>
      {/* Capitalize the first letter of the state name for the title */}
      <h2 style={styles.title}>
        Showing Schemes for {stateName.charAt(0).toUpperCase() + stateName.slice(1)}
      </h2>
      <p>This list includes both state-specific and national schemes.</p>
      
      {renderContent()}
    </div>
  );
};

// --- Styles ---
const styles = {
  container: {
    padding: '20px',
  },
  title: {
    color: '#333',
    borderBottom: '2px solid #eee',
    paddingBottom: '10px',
  },
  schemesList: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', // Responsive grid
    gap: '20px',
    marginTop: '20px',
  },
};

export default StateSchemes;