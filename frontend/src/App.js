import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import UploadPage from './components/UploadPage';
import FormPage from './components/FormPage';
import ResultsPage from './components/ResultsPage';
import Navbar from './components/Navbar';
import Chatbot from './components/Chatbot';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-100">
        <Navbar />
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/form" element={<FormPage />} />
          <Route path="/results" element={<ResultsPage />} />
        </Routes>
        
        {/* Global Floating Chatbot - Available on all pages */}
        <Chatbot />
      </div>
    </Router>
  );
}

export default App;
