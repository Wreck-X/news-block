import React, { useEffect, useState } from 'react';
import { Check, X } from 'lucide-react';

function VerifyPage() {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [voting, setVoting] = useState({});

  const BACKEND_URL = "http://localhost:5000";

  const fetchArticles = () => {
    setLoading(true);
    setError(null);
    fetch(`${BACKEND_URL}/toverify`)
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch articles');
        return res.json();
      })
      .then(data => {
        setArticles(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch articles:", err);
        setError("Failed to load articles. Please try again.");
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchArticles();
  }, []);

  const voteOnArticle = (id, action) => {
    if (voting[id]) return;
    setVoting(prev => ({ ...prev, [id]: true }));
    setError(null);

    fetch(`${BACKEND_URL}/vote/${id}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action }),
    })
      .then(res => {
        if (!res.ok) {
          return res.json().then(data => {
            throw new Error(data.error || "Vote failed");
          });
        }
        return res.json();
      })
      .then(() => {
        setArticles(prev => prev.filter(article => article.id !== id));
        fetchArticles();
      })
      .catch(err => {
        console.error("Error during vote:", err);
        setError(err.message);
        fetchArticles();
      })
      .finally(() => {
        setVoting(prev => ({ ...prev, [id]: false }));
      });
  };

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold mb-4">Content Verification</h1>
        {error && (
          <div className="text-red-600 mb-4">
            <p>{error}</p>
            <button
              onClick={fetchArticles}
              className="mt-2 bg-blue-600 text-white px-4 py-1 rounded text-sm hover:bg-blue-700"
            >
              Retry
            </button>
          </div>
        )}
        {loading ? (
          <p className="text-gray-600">Loading articles for verification...</p>
        ) : articles.length === 0 ? (
          <p className="text-gray-600">No articles found for verification.</p>
        ) : (
          <ul className="space-y-4">
            {articles.map((article) => (
              <li key={article.id} className="p-6 bg-white rounded shadow">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <p className="text-sm text-gray-500 mb-2">
                      {new Date(article.publishedAt).toLocaleDateString()}
                    </p>
                    <h2 className="text-xl font-semibold mb-2">{article.title}</h2>
                    <p className="text-gray-700 mb-2">{article.description}</p>
                    <p className="text-sm text-gray-600">By {article.author}</p>
                    <p className="text-sm text-gray-600 mt-1">
                      Approval Rate: {article.approval_rate}%
                    </p>
                  </div>
                  <div className="flex flex-col items-end gap-2 ml-4">
                    <div className="flex gap-2">
                      <button
                        onClick={() => voteOnArticle(article.id, "approve")}
                        disabled={voting[article.id]}
                        className={`flex items-center gap-1 bg-green-600 text-white px-3 py-1 rounded text-sm transition-colors ${
                          voting[article.id] ? 'opacity-50 cursor-not-allowed' : 'hover:bg-green-700'
                        }`}
                      >
                        <Check className="h-5 w-5" />
                        Approve
                      </button>
                      <button
                        onClick={() => voteOnArticle(article.id, "disapprove")}
                        disabled={voting[article.id]}
                        className={`flex items-center gap-1 bg-red-600 text-white px-3 py-1 rounded text-sm transition-colors ${
                          voting[article.id] ? 'opacity-50 cursor-not-allowed' : 'hover:bg-red-700'
                        }`}
                      >
                        <X className="h-5 w-5" />
                        Disapprove
                      </button>
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default VerifyPage;