import React from 'react';
import { Link } from 'react-router-dom';

const SchemeCard = ({ scheme }) => {
  return (
    <div style={styles.card}>
      <h3 style={styles.cardTitle}>{scheme.title}</h3>
      <p style={styles.cardDescription}>{scheme.description}</p>
      <Link to={`/schemes/${scheme._id}`} style={styles.cardLink}>
        View Details
      </Link>
    </div>
  );
};

// --- Styles ---
const styles = {
  card: {
    background: '#fff',
    border: '1px solid #ddd',
    borderRadius: '8px',
    padding: '20px',
    boxShadow: '0 2px 5px rgba(0,0,0,0.05)',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-between',
  },
  cardTitle: {
    margin: '0 0 10px 0',
    fontSize: '18px',
    color: '#004a99',
  },
  cardDescription: {
    fontSize: '14px',
    color: '#555',
    flexGrow: 1, // Makes the description take up available space
    marginBottom: '15px',
  },
  cardLink: {
    backgroundColor: '#f4f7f6',
    color: '#004a99',
    padding: '8px 12px',
    borderRadius: '5px',
    textDecoration: 'none',
    fontWeight: 'bold',
    textAlign: 'center',
    transition: 'background-color 0.2s',
  },
};

export default SchemeCard;