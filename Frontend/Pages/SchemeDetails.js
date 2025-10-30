import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../services/api'; // Our API service
import DocumentChecklist from '../components/DocumentChecklist'; // We'll create this next

const SchemeDetail = () => {
  const [scheme, setScheme] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // This mock user would come from localStorage in a real app
  const [mockUser, setMockUser] = useState({
    name: 'Mock User',
    uploaded_documents: ['Aadhaar Card', 'PAN Card'] 
  });
  
  // The 'id' comes from the URL (e.g., /schemes/123)
  const { id } = useParams();

  useEffect(() => {
    // 1. Fetch the specific scheme's details
    const fetchScheme = async () => {
      try {
        setLoading(true);
        setError(null);
        // This hits the GET /api/schemes/:id endpoint
        const res = await api.get(`/schemes/${id}`);
        setScheme(res.data.data);
      } catch (err) {
        console.error("Error fetching scheme:", err);
        setError("Could not load the scheme details.");
      } finally {
        setLoading(false);
      }
    };

    // 2. (Mock) Load user data from localStorage
    // In a real app:
    // const storedUser = JSON.parse(localStorage.getItem('user'));
    // if (storedUser) {
    //   setMockUser(storedUser);
    // }
    
    fetchScheme();
  }, [id]); // Re-run this effect if the 'id' in the URL changes

  // --- Render Functions ---

  if (loading) {
    return <p style={styles.message}>Loading scheme details...</p>;
  }

  if (error) {
    return <p style={styles.errorMessage}>{error}</p>;
  }

  if (!scheme) {
    return <p style={styles.message}>Scheme not found.</p>;
  }

  // Once data is loaded, render the details:
  return (
    <div style={styles.container}>
      {/* 1. Title and Back Link */}
      <Link to="/dashboard" style={styles.backLink}>&larr; Back to Dashboard</Link>
      <h2 style={styles.title}>{scheme.title}</h2>
      
      {/* 2. Full Details */}
      <div style={styles.section}>
        <h3 style={styles.sectionTitle}>Scheme Details</h3>
        <p>{scheme.full_details}</p>
      </div>
      
      {/* 3. Benefits */}
      <div style={styles.section}>
        <h3 style={styles.sectionTitle}>Benefits</h3>
        <p>{scheme.benefits}</p>
      </div>

      {/* 4. Eligibility */}
      <div style={styles.section}>
        <h3 style={styles.sectionTitle}>Eligibility</h3>
        <ul style={styles.list}>
          <li><strong>Age:</strong> {scheme.eligibility.age_min} - {scheme.eligibility.age_max} years</li>
          <li><strong>Gender:</strong> {scheme.eligibility.gender.join(', ')}</li>
          <li><strong>Profession:</strong> {scheme.eligibility.profession.join(', ')}</li>
          <li><strong>State:</strong> {scheme.eligibility.state.join(', ')}</li>
          <li><strong>Max Family Income:</strong> ₹{scheme.eligibility.salary_max.toLocaleString()}</li>
        </ul>
      </div>

      {/* 5. Document Checklist */}
      <div style={styles.section}>
        <h3 style={styles.sectionTitle}>Document Checklist</h3>
        <p>This list compares the required documents with the ones you have on your profile.</p>
        <DocumentChecklist 
          requiredDocs={scheme.required_documents} 
          userDocs={mockUser.uploaded_documents} 
        />
      </div>

      {/* 6. Official Link */}
      <a href={scheme.website_link} style={styles.applyButton} target="_blank" rel="noopener noreferrer">
        Go to Official Website
      </a>
    </div>
  );
};

// --- Styles ---
const styles = {
  container: {
    padding: '20px',
    background: '#fff',
    borderRadius: '8px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    margin: '20px 0',
  },
  title: {
    color: '#004a99',
    borderBottom: '2px solid #eee',
    paddingBottom: '10px',
  },
  section: {
    marginBottom: '25px',
  },
  sectionTitle: {
    color: '#333',
    borderBottom: '1px solid #ddd',
    paddingBottom: '5px',
    fontSize: '18px',
  },
  list: {
    listStyleType: 'disc',
    paddingLeft: '20px',
  },
  backLink: {
    display: 'inline-block',
    marginBottom: '15px',
    color: '#007bff',
    textDecoration: 'none',
  },
  applyButton: {
    display: 'inline-block',
    padding: '12px 25px',
    backgroundColor: '#28a745',
    color: 'white',
    textDecoration: 'none',
    fontWeight: 'bold',
    borderRadius: '5px',
    fontSize: '16px',
  },
  message: {
    textAlign: 'center',
    fontSize: '18px',
    padding: '20px',
  },
  errorMessage: {
    textAlign: 'center',
    fontSize: '18px',
    padding: '20px',
    color: 'red',
  }
};

export default SchemeDetail;