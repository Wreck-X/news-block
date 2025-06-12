import sqlite3
from datetime import datetime

DB_PATH = 'news.db'

def init_db():
    """Initialize the database with the news table if not already created."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
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

    print("DB is initialised")
    conn.commit()
    conn.close()


def insert_news(headline, body, author, approved=False):
    """Insert a new news item into the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO news (headline, body, author, date, approved)
        VALUES (?, ?, ?, ?, ?)
    ''', (headline, body, author, date_str, int(approved)))
    conn.commit()
    conn.close()


def get_all_news(approved_only=False):
    """Retrieve all news from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if approved_only:
        cursor.execute('SELECT * FROM news WHERE approved = 1')
    else:
        cursor.execute('SELECT * FROM news')
    news = cursor.fetchall()
    conn.close()
    return news


def validate_news(news):
    """Validate the structure of the news."""
    required_fields = ['headline', 'body', 'author']
    return isinstance(news, dict) and all(field in news for field in required_fields)


init_db()
