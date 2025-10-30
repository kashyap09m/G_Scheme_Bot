import React from 'react';

const DocumentChecklist = ({ requiredDocs = [], userDocs = [] }) => {
  // Create a Set from the user's documents for efficient lookups.
  // A Set provides a very fast way to check if an item exists (userDocSet.has(item)).
  const userDocSet = new Set(userDocs);

  return (
    <ul style={styles.list}>
      {/* Loop over every document the scheme requires */}
      {requiredDocs.map((doc, index) => {
        // Check if the user has this specific document
        const userHasDoc = userDocSet.has(doc);

        return (
          // Apply different styles based on whether the user has the doc
          <li key={index} style={userHasDoc ? styles.itemHave : styles.itemMissing}>
            {userHasDoc ? '✓' : '✗'}{' '}
            {doc}{' '}
            {userHasDoc ? <span>(You have this)</span> : <span>(Missing)</span>}
          </li>
        );
      })}
    </ul>
  );
};

// --- Styles ---
const styles = {
  list: {
    listStyleType: 'none',
    paddingLeft: '0',
  },
  item: {
    padding: '8px',
    margin: '5px 0',
    borderRadius: '4px',
    border: '1px solid #ddd',
  },
  // Green style for documents the user has
  itemHave: {
    padding: '8px',
    margin: '5px 0',
    borderRadius: '4px',
    border: '1px solid #d4edda',
    backgroundColor: '#f0fff4',
    color: '#155724',
    fontWeight: 'bold',
  },
  // Red style for documents the user is missing
  itemMissing: {
    padding: '8px',
    margin: '5px 0',
    borderRadius: '4px',
    border: '1px solid #f5c6cb',
    backgroundColor: '#fff8f8',
    color: '#721c24',
  },
};

export default DocumentChecklist;