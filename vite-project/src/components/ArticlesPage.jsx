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

    const apiKey = '4cc4b288e6ac4891a71c7cb1252b0bf3'; 

    fetch(`https://newsapi.org/v2/everything?q=${encodeURIComponent(searchTerm)}&apiKey=${apiKey}`)
      .then((res) => res.json())
      .then((data) => {
        setArticles(data.articles);
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
            {articles.map((article) => (
              <li
                key={article.url}
                className="p-4 bg-white rounded shadow hover:shadow-md transition"
              >
                <p className="text-sm text-gray-500 mb-2">{new Date(article.publishedAt).toLocaleDateString()}</p>
                <h2 className="text-xl font-semibold mb-2">
                  <a href={article.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                    {article.title}
                  </a>
                </h2>
                <p className="text-gray-700">{article.description}</p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default ArticlesPage;
