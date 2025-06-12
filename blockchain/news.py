import sqlite3

DB_PATH = 'news.db'

def init_db():
    """Initialize the database with the news table if not already created."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL
        )
    ''')

    print("DB is initialised")
    conn.commit()
    conn.close()

def insert_news(content):
    """Insert a new news item into the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO news (content) VALUES (?)', (content,))
    conn.commit()
    conn.close()

def get_all_news():
    """Retrieve all news from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM news')
    news = cursor.fetchall()
    conn.close()
    return news

def validate_news(news):
    """Validate the structure of the news."""
    return isinstance(news, dict) and 'content' in news

init_db()  # Initialize the DB when the application starts