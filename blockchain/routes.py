from flask import Blueprint, request, jsonify
from news import validate_news, news_db
from network import gossip_news, other_nodes

bp = Blueprint('routes', __name__)

@bp.route('/news', methods=['POST'])
def receive_news():
    news = request.json
    if validate_news(news):
        if news not in news_db:
            news_db.append(news)
            gossip_news(news)  # spread it through gossip
        return jsonify({"message": "News received and gossip started!", "news": news}), 200
    return jsonify({"message": "Invalid news format!"}), 400

@bp.route('/gossip', methods=['POST'])
def receive_gossip():
    news = request.json
    if validate_news(news):
        if news not in news_db:
            news_db.append(news)
            gossip_news(news)  # continue spreading gossip
        return jsonify({"message": "Gossip received!"}), 200
    return jsonify({"message": "Invalid gossip format!"}), 400

@bp.route('/validate', methods=['POST'])
def validate_news_from_peer():
    news = request.json
    if validate_news(news):
        return jsonify({"message": "News validated."}), 200
    return jsonify({"message": "Invalid news format!"}), 400

@bp.route('/register', methods=['POST'])
def register_new_node():
    data = request.json
    node_url = data.get('node_url')
    if node_url and node_url not in other_nodes:
        other_nodes.add(node_url)
        return jsonify({"message": "Node registered successfully.", "all_nodes": list(other_nodes)}), 200
    return jsonify({"message": "Invalid node URL or already registered."}), 400

@bp.route('/nodes', methods=['GET'])
def get_nodes():
    return jsonify({"nodes": list(other_nodes)}), 200
