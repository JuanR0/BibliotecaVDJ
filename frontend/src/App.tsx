import React, { useEffect, useState } from 'react';
import { libraryAPI } from './api';
import './App.css';

function App() {
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Test connection to FastAPI backend
    libraryAPI.getHealth()
      .then(response => {
        setMessage(`Backend status: ${response.data.status}`);
        setLoading(false);
      })
      .catch(error => {
        setMessage('Failed to connect to backend');
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="App">
      <h1>Library Management System</h1>
      <p>{message}</p>
      <p>Frontend is working! 🎉</p>
    </div>
  );
}

export default App;