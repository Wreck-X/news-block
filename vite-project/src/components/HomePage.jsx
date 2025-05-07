import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function HomePage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const navigate = useNavigate();

  const handleSearch = (e) => {
    e.preventDefault();
    navigate(`/articles?search=${encodeURIComponent(searchTerm)}`);
  };

  const handleNavigate = (path) => {
    navigate(path);
    setDropdownOpen(false); // close dropdown on mobile after click
  };

  return (
    <div className="relative flex flex-col items-center justify-center min-h-screen bg-gray-100">
      
      {/* Top-right buttons (desktop) */}
      <div className="absolute top-4 right-4 hidden sm:flex space-x-2">
        <button
          className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
          onClick={() => handleNavigate('/verify')}
        >
          Verify
        </button>
        <button
          className="bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600"
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
              className="bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600"
            >
              Upload
            </button>
          </div>
        )}
      </div>

      {/* Search form */}
      <form onSubmit={handleSearch} className="w-full max-w-md p-4">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Search..."
          className="w-full p-2 border border-gray-300 rounded"
        />
        <button
          type="submit"
          className="bg-blue-500 text-white px-4 py-2 rounded mt-4 hover:bg-blue-600 w-full"
        >
          Search
        </button>
      </form>
    </div>
  );
}

export default HomePage;
