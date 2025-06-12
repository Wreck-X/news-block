import React, { useEffect, useState } from 'react';
import { Check, X } from 'lucide-react';

function VerifyPage() {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:5000/toverify")
      .then(res => res.json())
      .then(setArticles)
      .catch(err => console.error("Failed to fetch articles:", err))
      .finally(() => setLoading(false));
  }, []);

  const voteOnArticle = (id, action) => {
    fetch(`http://localhost:5000/vote/${id}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action }),
    })
    .then(res => {
      if (res.ok) {
        // Remove article from list after vote
        setArticles(prev => prev.filter(article => article.id !== id));
      } else {
        console.error("Vote failed");
      }
    })
    .catch(err => console.error("Error during vote:", err));
  };

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold mb-4">Content Verification</h1>
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
                  </div>
                  <div className="flex flex-col items-end gap-2 ml-4">
                    <div className="flex gap-2">
                      <button
                        onClick={() => voteOnArticle(article.id, "approve")}
                        className="flex items-center gap-1 bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 transition-colors"
                      >
                        <Check className="h-5 w-5" />
                        Approve
                      </button>
                      <button
                        onClick={() => voteOnArticle(article.id, "disapprove")}
                        className="flex items-center gap-1 bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700 transition-colors"
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

