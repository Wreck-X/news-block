# News-Block: Distributed News Verification Platform

A decentralized news platform that uses community-driven voting to verify article authenticity before publication. [1](#0-0)  Articles must achieve a 60% approval rating to appear in search results. [2](#0-1) 

## Features

- **Community Verification**: Articles require community approval before becoming searchable [3](#0-2) 
- **P2P Network**: Gossip protocol for distributed news sharing [4](#0-3) 
- **Voting System**: Users can approve or disapprove articles [5](#0-4) 
- **Search Functionality**: Find verified articles by headline [6](#0-5) 
- **React Frontend**: Modern web interface for article management [7](#0-6) 

## Architecture

### Backend (Flask)
- **Database**: SQLite with `news` and `approvals` tables [8](#0-7) 
- **API Routes**: RESTful endpoints for news operations [9](#0-8) 
- **Network Layer**: P2P gossip protocol for news distribution [10](#0-9) 

### Frontend (React + Vite)
- **Home Page**: Search interface with typewriter effect [11](#0-10) 
- **Upload Page**: Article submission form [12](#0-11) 
- **Verification System**: Community voting interface [13](#0-12) 

## Installation

### Backend Setup
```bash
# Install Python dependencies
pip install flask sqlite3

# Initialize database
python -c "from blockchain.news import init_db; init_db()"

# Start Flask server
python app.py
```

### Frontend Setup
```bash
cd vite-project
npm install
npm run dev
```

## API Endpoints

- `POST /news` - Submit new article [14](#0-13) 
- `POST /vote/<article_id>` - Vote on article (approve/disapprove) [5](#0-4) 
- `GET /search?q=<query>` - Search verified articles [6](#0-5) 
- `GET /toverify` - Get articles pending verification [15](#0-14) 
- `POST /gossip` - Receive gossip from peers [10](#0-9) 

## Database Schema

### News Table
- `id`: Primary key [16](#0-15) 
- `headline`: Article title [17](#0-16) 
- `body`: Article content [18](#0-17) 
- `author`: Article author [19](#0-18) 
- `date`: Publication timestamp [20](#0-19) 

### Approvals Table
- `article_id`: Foreign key to news table [21](#0-20) 
- `approved`: Boolean vote (true/false) [22](#0-21) 

## Usage

1. **Submit Article**: Use the upload page to submit news articles [23](#0-22) 
2. **Community Voting**: Articles appear in `/toverify` for community review [24](#0-23) 
3. **Search Verified News**: Only articles with ≥60% approval appear in search results [25](#0-24) 

## Notes

The system uses a SQLite database (`news.db`) that initializes automatically on startup. [26](#0-25)  The voting threshold is hardcoded to 60% but could be made configurable. [1](#0-0)  The frontend communicates with the backend via REST API calls to `localhost:5000`. [27](#0-26) 

Wiki pages you might want to explore:
- [Database Schema (Wreck-X/news-block)](/wiki/Wreck-X/news-block#4)

### Citations

**File:** blockchain/routes.py (L3-3)
```python
from network import gossip_news, other_nodes, sync_news_with_peer
```

**File:** blockchain/routes.py (L7-7)
```python
bp = Blueprint('routes', __name__)
```

**File:** blockchain/routes.py (L9-22)
```python
@bp.route('/news', methods=['POST'])
def receive_news():
    """Receive news, validate it, store it, and start gossiping it."""
    news = request.get_json()
    if not news:
        return jsonify({"message": "No JSON data provided!"}), 400

    if validate_news(news):
        if news not in get_all_news():  # Avoid duplicates
            insert_news(news['headline'], news['body'], news['author']) # Store the news in the database
            gossip_news(news)  # Spread the news to peers
        return jsonify({"message": "News received and gossip started!", "news": news}), 200

    return jsonify({"message": "Invalid news format!"}), 400
```

**File:** blockchain/routes.py (L24-37)
```python
@bp.route('/gossip', methods=['POST'])
def receive_gossip():
    """Receive gossip from another node, validate it, and store it."""
    news = request.get_json()
    if not news:
        return jsonify({"message": "No JSON data provided!"}), 400

    if validate_news(news):
        if news not in get_all_news():  # Avoid duplicates
            insert_news(news['headline'], news['body'], news['author'])  # Store the news in the database
            gossip_news(news)  # Continue gossiping
        return jsonify({"message": "Gossip received!"}), 200

    return jsonify({"message": "Invalid gossip format!"}), 400
```

**File:** blockchain/routes.py (L80-106)
```python
@bp.route("/search")
def search_articles():
    query = request.args.get("q", "")
    threshold = 0.6  # approval threshold

    conn = sqlite3.connect("news.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT n.id, n.headline, n.body, n.author
        FROM news n
        JOIN (
            SELECT article_id, SUM(CASE WHEN approved THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS rating
            FROM approvals
            GROUP BY article_id
            HAVING rating >= ?
        ) a ON n.id = a.article_id
        WHERE n.headline LIKE ?
    """, (threshold, f"%{query}%"))

    results = [
        {"id": row[0], "headline": row[1], "body": row[2], "author": row[3]}
        for row in cursor.fetchall()
    ]

    conn.close()
    return jsonify({"results": results})
```

**File:** blockchain/routes.py (L109-128)
```python
@bp.route("/vote/<int:article_id>", methods=["POST"])
def vote_article(article_id):
    data = request.get_json()
    action = data.get("action")

    if action not in ["approve", "disapprove"]:
        return jsonify({"error": "Invalid action. Use 'approve' or 'disapprove'."}), 400

    approved = True if action == "approve" else False

    conn = sqlite3.connect("news.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO approvals (article_id, approved) VALUES (?, ?)", 
        (article_id, approved)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": f"{'Approval' if approved else 'Disapproval'} recorded."}), 200
```

**File:** blockchain/routes.py (L131-168)
```python
@bp.route("/toverify", methods=["GET"])
def get_pending_news():
    conn = sqlite3.connect("news.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT n.id, n.headline, n.body, n.author, n.date
        FROM news n
        LEFT JOIN (
            SELECT article_id,
                   SUM(CASE WHEN approved THEN 1 ELSE 0 END) as approvals,
                   COUNT(*) as total_votes
            FROM approvals
            GROUP BY article_id
        ) a ON n.id = a.article_id
        WHERE 
            n.approved = 0 AND 
            (
                a.total_votes IS NULL OR 
                (1.0 * a.approvals / a.total_votes) < 0.6
            )
    """)
    
    rows = cursor.fetchall()
    conn.close()

    articles = [
        {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "author": row[3],
            "publishedAt": row[4]
        }
        for row in rows
    ]

    return jsonify(articles)
```

**File:** vite-project/src/App.jsx (L1-20)
```javascript
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
```

**File:** blockchain/news.py (L10-28)
```python
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            headline TEXT NOT NULL,
            body TEXT NOT NULL,
            author TEXT NOT NULL,
            date TEXT NOT NULL,
            approved INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('''
       CREATE TABLE IF NOT EXISTS approvals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER,
            approved BOOLEAN,
            FOREIGN KEY(article_id) REFERENCES news(id)
        );
    ''')
```

**File:** blockchain/news.py (L67-67)
```python
init_db()
```

**File:** vite-project/src/components/HomePage.jsx (L6-33)
```javascript
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
```

**File:** vite-project/src/components/UploadPage.jsx (L3-38)
```javascript
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
```