import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './components/HomePage';
import ArticlesPage from './components/ArticlesPage';
import UploadPage from './components/UploadPage';
import VerifyPage from './components/VerifyPage';
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/articles" element={<ArticlesPage />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/verify" element={<VerifyPage />} /> 
      </Routes>
    </Router>
  );
}

export default App;
