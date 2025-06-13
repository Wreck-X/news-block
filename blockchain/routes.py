# routes.py
from flask import Blueprint, request, jsonify
from news import (
    validate_news, get_all_approved_news, insert_pending_news, 
    add_node_vote, check_approval_threshold, approve_pending_news,
    get_pending_news_by_hash, is_news_approved, generate_news_hash,
    get_all_pending_news
)
from network import gossip_approved_news, other_nodes, sync_approved_news_with_peer, sync_pending_news_with_peer, gossip_vote_request, get_node_url
import logging
import sqlite3
from news import DB_PATH

bp = Blueprint('routes', __name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@bp.route('/news', methods=['POST'])
def submit_news():
    """Submit a news item for network approval."""
    try:
        news = request.get_json()
        if not news or not validate_news(news):
            return jsonify({"error": "Invalid news format"}), 400

        headline, body, author = news['headline'], news['body'], news['author']
        
        if is_news_approved(headline, body, author):
            return jsonify({"message": "News already approved"}), 200
            
        news_hash = generate_news_hash(headline, body, author)
        existing_pending = get_pending_news_by_hash(news_hash)
        if existing_pending:
            return jsonify({"message": "News already pending approval"}), 200

        total_nodes = len(other_nodes) + 1
        
        pending_id = insert_pending_news(headline, body, author, total_nodes)
        if not pending_id:
            return jsonify({"error": "Failed to submit news"}), 500

        vote_request = {
            'type': 'vote_request',
            'pending_id': pending_id,
            'news': news,
            'news_hash': news_hash,
            'total_nodes': total_nodes
        }
        
        gossip_vote_request(vote_request)
        
        logger.info(f"News submitted for approval: {headline}")
        return jsonify({
            "message": "News submitted for network approval",
            "pending_id": pending_id,
            "requires_votes": int(total_nodes * 0.6) + 1
        }), 202
    except Exception as e:
        logger.error(f"Error submitting news: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/vote_request', methods=['POST'])
def receive_vote_request():
    """Receive vote request from another node."""
    try:
        data = request.get_json()
        if not data or data.get('type') != 'vote_request':
            return jsonify({"error": "Invalid vote request"}), 400

        news = data['news']
        news_hash = data['news_hash']
        pending_id = data['pending_id']
        total_nodes = data['total_nodes']

        existing = get_pending_news_by_hash(news_hash)
        if not existing:
            local_pending_id = insert_pending_news(
                news['headline'], news['body'], news['author'], total_nodes
            )
        else:
            local_pending_id = existing[0]

        logger.info(f"Vote request received for pending_id {local_pending_id}. Awaiting manual vote.")

        gossip_vote_request(data)
        
        return jsonify({"message": "Vote request received, awaiting manual vote"}), 200
    except Exception as e:
        logger.error(f"Error processing vote request: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/vote/<int:pending_id>', methods=['POST'])
def manual_vote(pending_id):
    """Allow a user to manually vote on a pending news item."""
    try:
        data = request.get_json()
        if not data or 'action' not in data:
            return jsonify({"error": "Action (approve or disapprove) required"}), 400

        action = data['action'].lower()
        if action not in ['approve', 'disapprove']:
            return jsonify({"error": "Invalid action. Use 'approve' or 'disapprove'"}), 400

        vote = 1 if action == 'approve' else 0
        try:
            voter_node = get_node_url()  # Use safe getter for node URL
        except ValueError as e:
            logger.error(f"Node URL not configured for pending_id: {pending_id}")
            return jsonify({"error": str(e)}), 500

        # Check if pending_id exists
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM pending_news WHERE id = ?', (pending_id,))
        if not cursor.fetchone():
            conn.close()
            logger.error(f"Invalid pending_id: {pending_id} for voter_node: {voter_node}")
            return jsonify({"error": "Invalid pending_id"}), 400

        # Check if vote already recorded
        cursor.execute('SELECT vote FROM node_votes WHERE pending_id = ? AND voter_node = ?', 
                       (pending_id, voter_node))
        existing_vote = cursor.fetchone()
        if existing_vote:
            conn.close()
            logger.info(f"Vote already recorded for pending_id: {pending_id}, voter_node: {voter_node}, existing_vote: {existing_vote[0]}")
            return jsonify({"error": "Vote already recorded"}), 400

        # Record the vote
        success = add_node_vote(pending_id, voter_node, vote)
        conn.close()
        if not success:
            logger.error(f"Failed to record vote for pending_id: {pending_id}, voter_node: {voter_node}")
            return jsonify({"error": "Failed to record vote"}), 500

        # Check approval threshold
        threshold_reached, news_data = check_approval_threshold(pending_id)
        if threshold_reached:
            approve_pending_news(pending_id)
            approved_news = {**news_data, 'approved': True}
            gossip_approved_news(approved_news)
            logger.info(f"News approved: {news_data['headline']}")

        logger.info(f"Vote recorded for pending_id: {pending_id}, voter_node: {voter_node}, vote: {vote}")
        return jsonify({"message": "Vote recorded successfully"}), 200
    except Exception as e:
        logger.error(f"Error processing manual vote for pending_id {pending_id}: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/vote_response', methods=['POST'])
def receive_vote_response():
    """Receive vote response from another node."""
    try:
        data = request.get_json()
        if not data or data.get('type') != 'vote_response':
            return jsonify({"error": "Invalid vote response"}), 400

        pending_id = data['pending_id']
        vote = data['vote']
        voter_node = data['voter_node']

        if not voter_node:
            logger.error(f"Invalid voter_node in vote_response for pending_id: {pending_id}")
            return jsonify({"error": "Invalid voter_node"}), 400

        success = add_node_vote(pending_id, voter_node, vote)
        if not success:
            return jsonify({"message": "Vote already recorded"}), 200

        threshold_reached, news_data = check_approval_threshold(pending_id)
        
        if threshold_reached:
            approve_pending_news(pending_id)
            approved_news = {**news_data, 'approved': True}
            gossip_approved_news(approved_news)
            logger.info(f"News approved: {news_data['headline']}")

        return jsonify({"message": "Vote processed"}), 200
    except Exception as e:
        logger.error(f"Error processing vote response: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/toverify', methods=['GET'])
def get_pending_news_for_verification():
    """Get all pending news items for manual verification."""
    try:
        pending = get_all_pending_news()
        news_list = [
            {
                "id": item[0],
                "title": item[1],
                "description": item[2],
                "author": item[3],
                "publishedAt": item[4],
                "approval_rate": round(item[7] * 100, 1) if item[7] else 0
            }
            for item in pending
        ]
        return jsonify(news_list), 200
    except Exception as e:
        logger.error(f"Error fetching pending news: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/approved_news', methods=['GET'])
def get_approved_news():
    """Get all approved news."""
    try:
        news = get_all_approved_news()
        news_list = [
            {
                "id": item[0],
                "headline": item[1],
                "body": item[2],
                "author": item[3],
                "date": item[4]
            }
            for item in news
        ]
        return jsonify({"news": news_list}), 200
    except Exception as e:
        logger.error(f"Error fetching approved news: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/search', methods=['GET'])
def search_approved_news():
    """Search approved news by headline or body."""
    try:
        search_term = request.args.get('q', '')
        if not search_term:
            return jsonify({"results": []}), 200

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, headline, body, author, date 
            FROM news 
            WHERE approved = 1 AND (headline LIKE ? OR body LIKE ?)
        ''', (f'%{search_term}%', f'%{search_term}%'))
        
        news = cursor.fetchall()
        conn.close()

        news_list = [
            {
                "id": item[0],
                "headline": item[1],
                "body": item[2],
                "author": item[3],
                "date": item[4]
            }
            for item in news
        ]
        return jsonify({"results": news_list}), 200
    except Exception as e:
        logger.error(f"Error searching approved news: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/pending_news', methods=['GET'])
def get_pending_news_status():
    """Get all pending news with approval status."""
    try:
        pending = get_all_pending_news()
        pending_list = [
            {
                "id": item[0],
                "title": item[1],
                "description": item[2],
                "author": item[3],
                "publishedAt": item[4],
                "total_nodes": item[5],
                "approval_votes": item[6],
                "approval_rate": round(item[7] * 100, 1) if item[7] else 0,
                "status": "Approved" if item[7] >= 0.6 else "Pending"
            }
            for item in pending
        ]
        return jsonify({"pending_news": pending_list}), 200
    except Exception as e:
        logger.error(f"Error fetching pending news: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/network_status', methods=['GET'])
def get_network_status():
    """Get current network status."""
    return jsonify({
        "total_nodes": len(other_nodes) + 1,
        "connected_nodes": list(other_nodes),
        "approval_threshold": "60%"
    }), 200

# routes.py (partial update, replace only the register_new_node function)
@bp.route('/register', methods=['POST'])
def register_new_node():
    """Register a new node to the network."""
    try:
        data = request.get_json(silent=True)
        logger.info(f"Received registration request with data: {data}")
        if not data:
            logger.warning("No JSON data provided in registration request")
            return jsonify({"message": "No JSON data provided!"}), 400

        node_url = data.get('node_url')
        if not node_url:
            logger.warning("Missing node_url in registration request")
            return jsonify({"message": "Missing node_url in request"}), 400

        if node_url in other_nodes:
            logger.info(f"Node {node_url} already registered")
            return jsonify({"message": "Node already registered", "all_nodes": list(other_nodes)}), 200

        other_nodes.add(node_url)
        sync_approved_news_with_peer(node_url)
        sync_pending_news_with_peer(node_url)
        logger.info(f"Node {node_url} registered successfully. Current nodes: {other_nodes}")
        return jsonify({"message": "Node registered successfully", "all_nodes": list(other_nodes)}), 200

    except Exception as e:
        logger.error(f"Error registering node: {str(e)}")
        return jsonify({"message": f"Error registering node: {str(e)}"}), 500