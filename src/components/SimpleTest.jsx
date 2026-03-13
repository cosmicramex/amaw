import React from 'react';

const SimpleTest = () => {
  return (
    <div style={{ 
      padding: '20px', 
      backgroundColor: '#e3f2fd', 
      border: '2px solid #2196f3', 
      borderRadius: '8px',
      margin: '20px',
      color: '#1976d2'
    }}>
      <h1>✅ React is Working!</h1>
      <p>If you can see this, React is rendering correctly.</p>
      <p>Current time: {new Date().toLocaleTimeString()}</p>
    </div>
  );
};

export default SimpleTest;
