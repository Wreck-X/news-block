news_db = []

def validate_news(news):
    return isinstance(news, dict) and 'content' in news
