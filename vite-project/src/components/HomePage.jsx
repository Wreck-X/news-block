import React, { useState, useEffect } from 'react';
import {Search} from 'lucide-react';
import ArticlesPage from './ArticlesPage';
import UploadPage from './UploadPage';
import { useNavigate } from 'react-router-dom';
function HomePage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [displayedText, setDisplayedText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);
  
  const fullText = "Millions of works, articles, and collections.";
  
  const navigate = useNavigate();

  useEffect(() => {
    if (currentIndex < fullText.length) {
      const timeout = setTimeout(() => {
        setDisplayedText(prev => prev + fullText[currentIndex]);
        setCurrentIndex(prev => prev + 1);
      }, 50); // Adjust speed here (lower = faster)
      
      return () => clearTimeout(timeout);
    }
  }, [currentIndex, fullText]);

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      // Navigate to /articles?query=your-search-term
      navigate(`/articles?search=${encodeURIComponent(searchTerm)}`);
    }
  };

  const handleNavigate = (path) => {
    
    navigate(path)
    // In a real app, you would navigate here
    console.log('Navigating to:', path);
    setDropdownOpen(false); // close dropdown on mobile after click
  };

  return (
    <div className="relative flex flex-col items-center justify-center min-h-screen bg-gray-50">
      
      {/* Top-left logo and text placeholder */}
      <div className="absolute top-4 left-4 flex items-center space-x-3">
        <img 
          src="/Pinecone-cropped.png" 
          alt="Logo" 
          className="h-20 w-80 object-contain"
                />
      </div>

      {/* Top-right buttons (desktop) */}
      <div className="absolute top-4 right-4 hidden sm:flex space-x-2">
        <button
          className="bg-white text-gray-800 px-8 py-4 rounded-lg border border-gray-200 hover:bg-gray-50 hover:border-gray-300 transition-colors"
          onClick={() => handleNavigate('/verify')}
        >
          Verify
        </button>
        <button
          className="bg-black text-white px-8 py-4 rounded-lg hover:bg-gray-800 transition-colors"
          onClick={() => handleNavigate('/upload')}
        >
          Upload
        </button>
      </div>

      {/* Top-right dropdown (mobile) */}
      <div className="absolute top-4 right-4 sm:hidden">
        <button
          onClick={() => setDropdownOpen(!dropdownOpen)}
          className="bg-gray-700 text-white px-3 py-2 rounded hover:bg-gray-800"
        >
          Menu ☰
        </button>
        {dropdownOpen && (
          <div className="mt-2 bg-white border rounded shadow">
            <button
              onClick={() => handleNavigate('/verify')}
              className="block w-full text-left px-4 py-2 hover:bg-gray-100"
            >
              Verify
            </button>
            <button
              onClick={() => handleNavigate('/upload')}
              className="block w-full text-left px-4 py-2 hover:bg-gray-100"
            >
              Upload
            </button>
          </div>
        )}
      </div>

      {/* Main content */}
      <div className="w-full max-w-3xl px-4">
        {/* Main heading */}
        <h1 className="text-7xl md:text-8xl font-bold text-black mb-3 text-left">
          Search.
        </h1>
        
        {/* Subtitle with typing animation */}
        <p className="text-gray-500 text-lg md:text-xl mb-3 text-left min-h-[1.5rem]">
          {displayedText}
          <span className="animate-pulse">|</span>
        </p>
        
        {/* Search bar */}
        <div className="relative w-full">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <Search className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            placeholder="Search by..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch(e)}
            className="w-full pl-12 pr-4 py-4 text-lg bg-white border border-gray-200 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder-gray-400"
          />
        </div>
      </div>
    </div>
  );
}

export default HomePage;
