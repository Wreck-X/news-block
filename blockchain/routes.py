from flask import Blueprint, request, jsonify
from news import validate_news, get_all_news, insert_news
from network import gossip_news, other_nodes, sync_news_with_peer

import sqlite3

bp = Blueprint('routes', __name__)

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

@bp.route('/validate', methods=['POST'])
def validate_news_from_peer():
    """Validate news format from peers."""
    news = request.get_json()
    if not news:
        return jsonify({"message": "No JSON data provided!"}), 400

    if validate_news(news):
        return jsonify({"message": "News validated."}), 200

    return jsonify({"message": "Invalid news format!"}), 400

@bp.route('/register', methods=['POST'])
def register_new_node():
    """Register a new node to the network."""
    data = request.get_json()
    if not data:
        return jsonify({"message": "No JSON data provided!"}), 400

    node_url = data.get('node_url')
    if node_url and node_url not in other_nodes:
        other_nodes.add(node_url)

        # Synchronize news with the newly registered node
        sync_news_with_peer(node_url)
        return jsonify({"message": "Node registered successfully.", "all_nodes": list(other_nodes)}), 200

    return jsonify({"message": "Invalid node URL or already registered."}), 400

@bp.route('/nodes', methods=['GET'])
def get_nodes():
    """Get the list of nodes in the network."""
    return jsonify({"nodes": list(other_nodes)}), 200

@bp.route('/sync', methods=['GET'])
def sync_news():
    """Synchronize news with all known peers."""
    for peer in other_nodes:
        sync_news_with_peer(peer)
    return jsonify({"message": "News synchronized with all nodes."}), 200

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

