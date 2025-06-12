import React, { useState } from 'react';

function UploadPage() {
  const [headline, setHeadline] = useState('');
  const [articleBody, setArticleBody] = useState('');
  const [author, setAuthor] = useState('');


const handleSubmit = async (e) => {
  e.preventDefault();

  const article = {
    headline,
    body: articleBody,
    author
  };

  try {
    const response = await fetch('http://localhost:5000/news', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(article)
    });

    const data = await response.json();
    if (response.ok) {
      alert('Article queued for verification!');
      console.log(data);
    } else {
      alert(`Error: ${data.message}`);
    }
  } catch (error) {
    console.error('Error submitting article:', error);
    alert('Failed to submit article.');
  }
}; 


  return (
    <div className="min-h-screen bg-gray-100 p-4 flex items-center justify-center">
      <form
        onSubmit={handleSubmit}
        className="bg-white w-full max-w-2xl p-6 rounded shadow"
      >
        <h1 className="text-xl font-bold mb-4">New Article</h1>

        {/* Headline input */}
        <input
          type="text"
          value={headline}
          onChange={(e) => setHeadline(e.target.value)}
          placeholder="Headline"
          className="w-full p-2 mb-4 border border-gray-300 rounded"
        />

        {/* Article body input */}
        <textarea
          value={articleBody}
          onChange={(e) => setArticleBody(e.target.value)}
          placeholder="Write the article body here..."
          rows={6}
          className="w-full p-2 mb-4 border border-gray-300 rounded"
        />
        
        <input
          type='text'
          value={author}
          onChange={(e) => setAuthor(e.target.value)}
          placeholder="Author"
          className='w-full p-2 mb-4 border border-gray-300 rounded'
        />
        <button
          type="submit"
          className="bg-blue-500 text-white px-4 py-2 rounded w-full hover:bg-blue-600"
        >
          Proceed with verification
        </button>
      </form>
    </div>
  );
}

export default UploadPage;
