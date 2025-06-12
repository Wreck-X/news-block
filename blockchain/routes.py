from flask import Blueprint, request, jsonify
from news import validate_news, get_all_news, insert_news
from network import gossip_news, other_nodes, sync_news_with_peer

bp = Blueprint('routes', __name__)

@bp.route('/news', methods=['POST'])
def receive_news():
    """Receive news, validate it, store it, and start gossiping it."""
    news = request.json
    if validate_news(news):
        if news not in get_all_news():  # Avoid duplicates
            insert_news(news['content'])  # Store the news in the database
            gossip_news(news)  # Spread the news to peers
        return jsonify({"message": "News received and gossip started!", "news": news}), 200
    return jsonify({"message": "Invalid news format!"}), 400

@bp.route('/gossip', methods=['POST'])
def receive_gossip():
    """Receive gossip from another node, validate it, and store it."""
    news = request.json
    if validate_news(news):
        if news not in get_all_news():  # Avoid duplicates
            insert_news(news['content'])  # Store the news in the database
            gossip_news(news)  # Continue gossiping
        return jsonify({"message": "Gossip received!"}), 200
    return jsonify({"message": "Invalid gossip format!"}), 400

@bp.route('/validate', methods=['POST'])
def validate_news_from_peer():
    """Validate news format from peers."""
    news = request.json
    if validate_news(news):
        return jsonify({"message": "News validated."}), 200
    return jsonify({"message": "Invalid news format!"}), 400

@bp.route('/register', methods=['POST'])
def register_new_node():
    """Register a new node to the network."""
    data = request.json
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

