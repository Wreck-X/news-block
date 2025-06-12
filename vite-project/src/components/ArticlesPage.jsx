import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';

function ArticlesPage() {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const location = useLocation();

  const searchParams = new URLSearchParams(location.search);
  const searchTerm = searchParams.get('search') || '';

  useEffect(() => {
    if (!searchTerm) return;

    setLoading(true);

    fetch(`http://localhost:5000/search?q=${encodeURIComponent(searchTerm)}`)
      .then((res) => res.json())
      .then((data) => {
        setArticles(data.results || []);
        setLoading(false);
      })
      .catch((error) => {
        console.error('Error fetching articles:', error);
        setLoading(false);
      });
  }, [searchTerm]);

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold mb-4">Search Results for "{searchTerm}"</h1>
        {loading ? (
          <p className="text-gray-600">Loading articles...</p>
        ) : articles.length === 0 ? (
          <p className="text-gray-600">No articles found.</p>
        ) : (
          <ul className="space-y-4">
            {articles.map((article, index) => (
              <li
                key={index}
                className="p-4 bg-white rounded shadow hover:shadow-md transition"
              >
                <p className="text-sm text-gray-500 mb-2">
                  {new Date(article.date).toLocaleDateString()}
                </p>
                <h2 className="text-xl font-semibold mb-2 text-blue-700">
                  {article.headline}
                </h2>
                <p className="text-gray-700">{article.body}</p>
                <p className="text-sm text-gray-600 mt-2">— {article.author}</p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default ArticlesPage;

