from flask import Flask, request, jsonify
import argparse
import requests

# Set up the Flask app
app = Flask(__name__)

# Store the node's local ledger of validated news
news_db = []

# Node's ID
node_id = None
other_nodes = ['http://localhost:5002', 'http://localhost:5003']  # Other node URLs to communicate with

# Simple news validation function
def validate_news(news):
    # Simple validation: check if 'content' field is present
    if isinstance(news, dict) and 'content' in news:
        return True
    return False

# Broadcast news to other nodes for consensus
def broadcast_news(news):
    responses = [node_id]
    for node_url in other_nodes:
        response = requests.post(f"{node_url}/validate", json=news)
        if response.status_code == 200:
            responses.append(node_url)
    return responses

# API to accept incoming news
@app.route('/news', methods=['POST'])
def receive_news():
    news = request.json
    if validate_news(news):
        responses = broadcast_news(news)
        if len(responses) >= len(other_nodes) / 2 + 1:
            news_db.append(news)
            return jsonify({"message": "News validated and added!", "news": news}), 200
        else:
            return jsonify({"message": "Consensus not reached."}), 400
    return jsonify({"message": "Invalid news format!"}), 400

# API to validate news from other nodes
@app.route('/validate', methods=['POST'])
def validate_news_from_peer():
    news = request.json
    if validate_news(news):
        return jsonify({"message": "News validated."}), 200
    return jsonify({"message": "Invalid news format!"}), 400

# Run the node's Flask server
if __name__ == '__main__':
    # Command line argument parsing
    parser = argparse.ArgumentParser(description="Start a node with a specific ID.")
    parser.add_argument('--node_id', type=int, required=True, help="The unique ID of this node.")
    args = parser.parse_args()
    
    # Set node_id based on the command line argument
    node_id = args.node_id

    # Calculate port based on node_id (e.g., 5000 + node_id)
    port = 5000 + node_id

    print(f"Node {node_id} started on port {port}...")

    # Start the Flask server with the dynamic port
    app.run(host='localhost', port=port)
