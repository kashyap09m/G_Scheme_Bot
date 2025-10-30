import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api'; // Our centralized axios instance

const Register = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    age: '',
    gender: 'Male',
    profession: 'Student',
    state: 'Maharashtra',
    district: '',
    familyIncome: '', // Changed from 'salary'
    category: 'General', // Social Category
    isPwD: 'No', // Disability Status
  });

  // State for the document checkboxes
  const [documents, setDocuments] = useState({
    "Aadhaar Card": false,
    "PAN Card": false,
    "Ration Card": false,
    "Voter ID Card": false,
    "Birth Certificate": false,
    "Domicile Certificate": false,
  });

  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate(); // Hook to redirect user

  const {
    name, email, password, confirmPassword, age, gender,
    profession, state, district, familyIncome, category, isPwD
  } = formData;

  // This function updates the main form state
  const onChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // This function updates the document checkbox state
  const onDocChange = (e) => {
    setDocuments({ ...documents, [e.target.name]: e.target.checked });
  };

  // This function is called when the form is submitted
  const onSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    // 1. Check if passwords match
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return; // Stop the submission
    }
    
    setLoading(true); // Disable form

    // 2. Process the document checkboxes into an array of names
    const uploaded_documents = Object.keys(documents).filter(doc => documents[doc]);
    
    // 3. Combine all data for submission
    const registrationData = {
      name, email, password, age, gender, profession,
      state, district, familyIncome, category, isPwD,
      uploaded_documents // Add the documents array
    };

    try {
      // 4. Send the data to the backend
      const res = await api.post('/auth/register', registrationData);

      console.log('Registration successful:', res.data);
      
      alert('Registration successful! You can now log in.');
      navigate('/login'); // Redirect to the login page

    } catch (err) {
      console.error('Registration error:', err.response ? err.response.data : err.message);
      setError(err.response?.data?.error || 'Registration failed. Please try again.');
    } finally {
      setLoading(false); // Re-enable form
    }
  };

  return (
    <div>
      <h2 style={{ textAlign: 'center', margin: '20px 0' }}>Create Your Account</h2>
      
      <form onSubmit={onSubmit}>
        {error && <div style={{ color: 'red', marginBottom: '10px', textAlign: 'center' }}>{error}</div>}
        
        {/* --- Basic Info --- */}
        <fieldset style={fieldSetStyle}>
          <legend>Basic Information</legend>
          <div>
            <label>Full Name:</label>
            <input type="text" name="name" value={name} onChange={onChange} required disabled={loading} />
          </div>
          <div>
            <label>Email:</label>
            <input type="email" name="email" value={email} onChange={onChange} required disabled={loading} />
          </div>
          <div>
            <label>Password (min 6 characters):</label>
            <input type="password" name="password" value={password} onChange={onChange} minLength="6" required disabled={loading} />
          </div>
          <div>
            <label>Confirm Password:</label>
            <input type="password" name="confirmPassword" value={confirmPassword} onChange={onChange} minLength="6" required disabled={loading} />
          </div>
        </fieldset>

        {/* --- Profile Details (for Recommendations) --- */}
        <fieldset style={fieldSetStyle}>
          <legend>Profile Details</legend>
          <div>
            <label>Age:</label>
            <input type="number" name="age" value={age} onChange={onChange} required disabled={loading} />
          </div>
          <div>
            <label>Gender:</label>
            <select name="gender" value={gender} onChange={onChange} disabled={loading}>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
            </select>
          </div>
          <div>
            <label>Profession:</label>
            <select name="profession" value={profession} onChange={onChange} disabled={loading}>
              <option value="Student">Student</option>
              <option value="Farmer">Farmer</option>
              <option value="Businessman">Businessman</option>
              <option value="Housewife">Housewife</option>
              <option value="Fisherman">Fisherman</option>
              <option value="Other">Other</option>
            </select>
          </div>
          <div>
            <label>Annual Family Income (in Rupees):</label>
            <input type="number" name="familyIncome" value={familyIncome} onChange={onChange} required disabled={loading} />
          </div>
          <div>
            <label>Social Category:</label>
            <select name="category" value={category} onChange={onChange} disabled={loading}>
              <option value="General">General</option>
              <option value="OBC">OBC</option>
              <option value="SC">SC</option>
              <option value="ST">ST</option>
              <option value="EWS">EWS</option>
            </select>
          </div>
          <div>
            <label>Are you a Person with Disability?</label>
            <select name="isPwD" value={isPwD} onChange={onChange} disabled={loading}>
              <option value="No">No</option>
              <option value="Yes">Yes</option>
            </select>
          </div>
          <div>
            <label>State:</label>
            <input type="text" name="state" value={state} onChange={onChange} placeholder="e.g., Maharashtra" required disabled={loading} />
          </div>
          <div>
            <label>District:</label>
            <input type="text" name="district" value={district} onChange={onChange} placeholder="e.g., Pune" required disabled={loading} />
          </div>
        </fieldset>
        
        {/* --- Document Checklist --- */}
        <fieldset style={fieldSetStyle}>
          <legend>My Documents</legend>
          <p style={{marginTop: 0, color: '#555'}}>Which of these documents do you have?</p>
          {Object.keys(documents).map((docName) => (
            <div key={docName} style={checkboxStyle}>
              <input
                type="checkbox"
                id={docName}
                name={docName}
                checked={documents[docName]}
                onChange={onDocChange}
                disabled={loading}
              />
              <label htmlFor={docName}>{docName}</label>
            </div>
          ))}
        </fieldset>

        <button type="submit" disabled={loading}>
          {loading ? 'Registering...' : 'Register'}
        </button>

        <p style={{ textAlign: 'center' }}>
          Already have an account? <Link to="/login">Login here</Link>
        </p>
      </form>
    </div>
  );
};

// Simple styles for the new elements
const fieldSetStyle = {
  border: '1px solid #ccc',
  borderRadius: '5px',
  padding: '15px',
  margin: '10px 0',
};

const checkboxStyle = {
  flexDirection: 'row',
  alignItems: 'center',
  gap: '10px',
  margin: '5px 0'
};

export default Register;