import sqlite3
import hashlib
import logging
from datetime import datetime

DB_PATH = "news.db"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database with required tables."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute('PRAGMA foreign_keys = ON')
        cursor = conn.cursor()
        
        # Create news table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                headline TEXT NOT NULL,
                body TEXT NOT NULL,
                author TEXT NOT NULL,
                date TEXT NOT NULL,
                approved INTEGER NOT NULL
            )
        ''')

        # Create pending_news table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pending_news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                headline TEXT NOT NULL,
                body TEXT NOT NULL,
                author TEXT NOT NULL,
                date TEXT NOT NULL,
                total_nodes INTEGER NOT NULL,
                approval_votes INTEGER DEFAULT 0,
                approval_rate REAL DEFAULT 0.0
            )
        ''')

        # Create node_votes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS node_votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pending_id INTEGER NOT NULL,
                voter_node TEXT NOT NULL,
                vote INTEGER NOT NULL,
                FOREIGN KEY (pending_id) REFERENCES pending_news(id)
            )
        ''')

        conn.commit()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
    finally:
        conn.close()

def validate_news(news):
    """Validate news item structure."""
    required_fields = ['headline', 'body', 'author']
    return all(field in news and isinstance(news[field], str) and news[field].strip() for field in required_fields)

def generate_news_hash(headline, body, author):
    """Generate a unique hash for a news item."""
    news_string = f"{headline}{body}{author}"
    return hashlib.sha256(news_string.encode()).hexdigest()

def insert_news(headline, body, author, approved=False):
    """Insert a news item into the news table."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        date = datetime.utcnow().isoformat()
        cursor.execute('''
            INSERT INTO news (headline, body, author, date, approved)
            VALUES (?, ?, ?, ?, ?)
        ''', (headline, body, author, date, 1 if approved else 0))
        conn.commit()
        logger.info(f"Inserted news: {headline}")
        return cursor.lastrowid
    except Exception as e:
        logger.error(f"Error inserting news: {str(e)}")
        return None
    finally:
        conn.close()

def insert_pending_news(headline, body, author, total_nodes):
    """Insert a news item into the pending_news table."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        date = datetime.utcnow().isoformat()
        cursor.execute('''
            INSERT INTO pending_news (headline, body, author, date, total_nodes)
            VALUES (?, ?, ?, ?, ?)
        ''', (headline, body, author, date, total_nodes))
        conn.commit()
        pending_id = cursor.lastrowid
        logger.info(f"Inserted pending news: {headline}, pending_id: {pending_id}")
        return pending_id
    except Exception as e:
        logger.error(f"Error inserting pending news: {str(e)}")
        return None
    finally:
        conn.close()

def add_node_vote(pending_id, voter_node, vote):
    """Record a vote from a node for a pending news item."""
    try:
        if not voter_node:
            logger.error(f"voter_node is None for pending_id {pending_id}")
            return False

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Validate pending_id exists
        cursor.execute('SELECT id FROM pending_news WHERE id = ?', (pending_id,))
        if not cursor.fetchone():
            logger.error(f"Invalid pending_id {pending_id} in add_node_vote")
            conn.close()
            return False

        # Check if vote already exists
        cursor.execute('''
            SELECT vote FROM node_votes WHERE pending_id = ? AND voter_node = ?
        ''', (pending_id, voter_node))
        existing_vote = cursor.fetchone()
        if existing_vote:
            logger.info(f"Vote already recorded for pending_id {pending_id}, voter_node {voter_node}, vote {existing_vote[0]}")
            conn.close()
            return False

        # Insert the vote
        cursor.execute('''
            INSERT INTO node_votes (pending_id, voter_node, vote)
            VALUES (?, ?, ?)
        ''', (pending_id, voter_node, vote))
        
        # Update approval_votes in pending_news
        if vote == 1:
            cursor.execute('''
                UPDATE pending_news
                SET approval_votes = approval_votes + 1,
                    approval_rate = (approval_votes + 1) * 1.0 / total_nodes
                WHERE id = ?
            ''', (pending_id,))
        
        conn.commit()
        logger.info(f"Vote recorded: pending_id {pending_id}, voter_node {voter_node}, vote {vote}")
        return True
    except Exception as e:
        logger.error(f"Error adding node vote for pending_id {pending_id}: {str(e)}")
        conn.close()
        return False

def check_approval_threshold(pending_id):
    """Check if a pending news item has reached the approval threshold."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT headline, body, author, total_nodes, approval_votes 
            FROM pending_news WHERE id = ?
        ''', (pending_id,))
        result = cursor.fetchone()
        if not result:
            conn.close()
            logger.error(f"Pending news not found for id {pending_id}")
            return False, None
        headline, body, author, total_nodes, approval_votes = result
        approval_rate = approval_votes / total_nodes if total_nodes > 0 else 0
        threshold_reached = approval_votes >= int(total_nodes * 0.6) + 1
        news_data = {'headline': headline, 'body': body, 'author': author}
        conn.close()
        return threshold_reached, news_data
    except Exception as e:
        logger.error(f"Error checking approval threshold: {str(e)}")
        return False, None

def approve_pending_news(pending_id):
    """Move approved news from pending_news to news table."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT headline, body, author, date 
            FROM pending_news WHERE id = ?
        ''', (pending_id,))
        news = cursor.fetchone()
        if news:
            headline, body, author, date = news
            cursor.execute('''
                INSERT INTO news (headline, body, author, date, approved) 
                VALUES (?, ?, ?, ?, ?)
            ''', (headline, body, author, date, 1))
            cursor.execute('DELETE FROM pending_news WHERE id = ?', (pending_id,))
            cursor.execute('DELETE FROM node_votes WHERE pending_id = ?', (pending_id,))
            conn.commit()
            logger.info(f"Approved pending news with id: {pending_id}")
        conn.close()
        return bool(news)
    except Exception as e:
        logger.error(f"Error approving pending news: {str(e)}")
        return False

def get_pending_news_by_hash(news_hash):
    """Get pending news by its hash."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, headline, body, author 
            FROM pending_news 
            WHERE headline || body || author = ?
        ''', (news_hash,))
        return cursor.fetchone()
    except Exception as e:
        logger.error(f"Error getting pending news by hash: {str(e)}")
        return None
    finally:
        conn.close()

def is_news_approved(headline, body, author):
    """Check if news is already approved."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id FROM news 
            WHERE headline = ? AND body = ? AND author = ? AND approved = 1
        ''', (headline, body, author))
        exists = cursor.fetchone()
        conn.close()
        return bool(exists)
    except Exception as e:
        logger.error(f"Error checking if news is approved: {str(e)}")
        return False

def get_all_approved_news():
    """Get all approved news items."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT id, headline, body, author, date FROM news WHERE approved = 1')
        news = cursor.fetchall()
        conn.close()
        return news
    except Exception as e:
        logger.error(f"Error fetching approved news: {str(e)}")
        return []

def get_all_pending_news():
    """Get all pending news items."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, headline, body, author, date, total_nodes, approval_votes, approval_rate 
            FROM pending_news
        ''')
        pending = cursor.fetchall()
        conn.close()
        return pending
    except Exception as e:
        logger.error(f"Error fetching pending news: {str(e)}")
        return []

# Initialize database on module import
init_db()