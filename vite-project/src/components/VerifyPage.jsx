import React, { useEffect, useState } from 'react';
import { Check, X } from 'lucide-react';

function VerifyPage() {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);

  // Placeholder data for verification
  const placeholderArticles = [
    {
      id: 1,
      title: "The Impact of Climate Change on Ocean Ecosystems",
      description: "A comprehensive study examining how rising sea temperatures and acidification are affecting marine biodiversity and ecosystem stability.",
      publishedAt: "2024-03-15T10:30:00Z",
      url: "#",
      author: "Dr. Sarah Johnson",
      source: "Environmental Science Journal",
      status: "pending"
    },
    {
      id: 2,
      title: "Machine Learning Applications in Healthcare",
      description: "Exploring the revolutionary applications of artificial intelligence and machine learning in medical diagnosis and treatment planning.",
      publishedAt: "2024-03-14T14:45:00Z",
      url: "#",
      author: "Prof. Michael Chen",
      source: "Medical Technology Review",
      status: "pending"
    },
    {
      id: 3,
      title: "Sustainable Urban Development Strategies",
      description: "Analyzing effective approaches to creating environmentally sustainable cities while maintaining economic growth and social equity.",
      publishedAt: "2024-03-13T09:15:00Z",
      url: "#",
      author: "Dr. Emily Rodriguez",
      source: "Urban Planning Quarterly",
      status: "pending"
    },
    {
      id: 4,
      title: "Quantum Computing: Future Perspectives",
      description: "An in-depth look at the current state of quantum computing technology and its potential applications in various industries.",
      publishedAt: "2024-03-12T16:20:00Z",
      url: "#",
      author: "Dr. David Kim",
      source: "Technology Today",
      status: "pending"
    },
    {
      id: 5,
      title: "Biodiversity Conservation in Tropical Forests",
      description: "Research findings on effective conservation strategies for protecting endangered species in tropical rainforest ecosystems.",
      publishedAt: "2024-03-11T11:30:00Z",
      url: "#",
      author: "Dr. Maria Santos",
      source: "Conservation Biology",
      status: "pending"
    }
  ];

  useEffect(() => {
    // Simulate loading delay
    setTimeout(() => {
      setArticles(placeholderArticles);
      setLoading(false);
    }, 1000);
  }, []);

  const handleApprove = (id) => {
    setArticles(prev => 
      prev.map(article => 
        article.id === id ? { ...article, status: 'approved' } : article
      )
    );
  };

  const handleDisapprove = (id) => {
    setArticles(prev => 
      prev.map(article => 
        article.id === id ? { ...article, status: 'disapproved' } : article
      )
    );
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'approved':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'disapproved':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'approved':
        return 'Approved';
      case 'disapproved':
        return 'Disapproved';
      default:
        return 'Pending Review';
    }
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
              <li
                key={article.id}
                className="p-6 bg-white rounded shadow hover:shadow-md transition"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <p className="text-sm text-gray-500 mb-2">
                      {new Date(article.publishedAt).toLocaleDateString()} • {article.source}
                    </p>
                    <h2 className="text-xl font-semibold mb-2">
                      <a href={article.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                        {article.title}
                      </a>
                    </h2>
                    <p className="text-gray-700 mb-2">{article.description}</p>
                    <p className="text-sm text-gray-600">By {article.author}</p>
                  </div>
                  
                  <div className="flex flex-col items-end gap-2 ml-4">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getStatusColor(article.status)}`}>
                      {getStatusText(article.status)}
                    </span>
                    
                    {article.status === 'pending' && (
                      <div className="flex gap-2 mt-2">
                        <button
                          onClick={() => handleApprove(article.id)}
                          className="flex items-center gap-1 bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 transition-colors"
                        >
                          <Check className="h-10 w-10" />
                          Approve
                        </button>
                        <button
                          onClick={() => handleDisapprove(article.id)}
                          className="flex items-center gap-1 bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700 transition-colors"
                        >
                          <X className="h-10 w-10" />
                          Disapprove
                        </button>
                      </div>
                    )}
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
