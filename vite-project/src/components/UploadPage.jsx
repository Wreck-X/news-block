import React, { useState } from 'react';

function UploadPage() {
  const [headline, setHeadline] = useState('');
  const [articleBody, setArticleBody] = useState('');
  const [attachedFile, setAttachedFile] = useState(null);

  const handleFileChange = (e) => {
    setAttachedFile(e.target.files[0]);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Send headline, articleBody, attachedFile to backend here
    console.log('Headline:', headline);
    console.log('Article Body:', articleBody);
    console.log('Attached File:', attachedFile);
    alert('Article queued for verification!');
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

        {/* File attachment
        <div className="mb-4">
          <label className="block mb-2 text-sm font-medium text-gray-700">
            Attach related images:
          </label>
          <input
            type="file"
            onChange={handleFileChange}
            className="w-full text-sm text-gray-700"
            accept="image/*"
          />
          {attachedFile && (
            <p className="mt-2 text-sm text-gray-500">{attachedFile.name}</p>
          )}
        </div> */}

        {/* Submit button */}
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
