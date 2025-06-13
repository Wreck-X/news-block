import logging
import os
import socket
import requests
import time
from config import START_PORT, MAX_PORT_TRIES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize node URL and peers
this_node_url = None
other_nodes = set()

def find_free_port(start_port=START_PORT):
    """Find a free port starting from start_port."""
    port = start_port
    tries = 0
    while tries < MAX_PORT_TRIES:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                logger.info(f"Found free port: {port}")
                return port
            except OSError:
                port += 1
                tries += 1
                if port > 65535:
                    raise Exception("No free ports available in valid range")
    raise Exception(f"No free ports found after trying {MAX_PORT_TRIES} ports starting from {start_port}")

def try_register_with_bootstrap(bootstrap_url, node_url):
    """Register this node with a bootstrap node or become bootstrap if none exists."""
    if bootstrap_url == node_url:
        logger.info(f"This node {node_url} is the bootstrap node")
        return True

    try:
        response = requests.post(f"{bootstrap_url}/register", json={"node_url": node_url}, timeout=5)
        response.raise_for_status()
        data = response.json()
        new_nodes = data.get('all_nodes', [])
        other_nodes.update([n for n in new_nodes if n != node_url])
        if bootstrap_url != node_url:
            other_nodes.add(bootstrap_url)
        logger.info(f"Registered with bootstrap {bootstrap_url}, nodes: {other_nodes}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to register with bootstrap {bootstrap_url}: {str(e)}")
        if "Connection refused" in str(e) or "timeout" in str(e):
            logger.info(f"No bootstrap node at {bootstrap_url}. Becoming bootstrap node.")
            return True
        return False

def gossip_vote_request(vote_request_data):
    """Send a vote request to all known peers."""
    if not other_nodes:
        logger.info("No peers to send vote request to")
        return
    for node in other_nodes:
        try:
            response = requests.post(f"{node}/vote_request", json=vote_request_data, timeout=5)
            response.raise_for_status()
            logger.info(f"Vote request sent to {node}")
        except Exception as e:
            logger.error(f"Error sending vote request to {node}: {str(e)}")

def gossip_approved_news(approved_news):
    """Gossip approved news to all known peers."""
    for node in other_nodes:
        try:
            response = requests.post(f"{node}/approved_news", json=approved_news, timeout=5)
            response.raise_for_status()
            logger.info(f"Approved news sent to {node}")
        except Exception as e:
            logger.error(f"Error sending approved news to {node}: {str(e)}")

def sync_approved_news_with_peer(peer_url):
    """Sync approved news with a peer, with retry mechanism."""
    max_retries = 3
    retry_delay = 2  # seconds
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{peer_url}/approved_news", timeout=5)
            response.raise_for_status()
            news_list = response.json().get('news', [])
            from news import insert_news
            for news in news_list:
                insert_news(news['headline'], news['body'], news['author'], approved=True)
            logger.info(f"Synced approved news with {peer_url}")
            return
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1}/{max_retries} failed syncing approved news with {peer_url}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    logger.error(f"Failed to sync approved news with {peer_url} after {max_retries} attempts")

def sync_pending_news_with_peer(peer_url):
    """Sync pending news with a peer, with retry mechanism."""
    max_retries = 3
    retry_delay = 2  # seconds
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{peer_url}/pending_news", timeout=5)
            response.raise_for_status()
            pending_list = response.json().get('pending_news', [])
            from news import insert_pending_news
            for pending in pending_list:
                insert_pending_news(
                    pending['title'],
                    pending['description'],
                    pending['author'],
                    pending['total_nodes']
                )
            logger.info(f"Synced pending news with {peer_url}")
            return
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1}/{max_retries} failed syncing pending news with {peer_url}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    logger.error(f"Failed to sync pending news with {peer_url} after {max_retries} attempts")

def get_node_url():
    """Safely retrieve this_node_url, raising an error if not set."""
    global this_node_url
    if this_node_url is None:
        logger.error("this_node_url is not initialized")
        raise ValueError("Node URL is not configured")
    return this_node_url

def initialize_node_url(port):
    """Set this_node_url based on the chosen port."""
    global this_node_url
    bootstrap_url = os.getenv('BOOTSTRAP_URL', 'http://localhost:5000')
    if bootstrap_url == f'http://localhost:{port}':
        this_node_url = bootstrap_url
    else:
        this_node_url = os.getenv('NODE_URL', f'http://localhost:{port}')
    if not this_node_url:
        this_node_url = f'http://localhost:{port}'
        logger.warning(f"this_node_url set to default: {this_node_url}")
    logger.info(f"this_node_url initialized as: {this_node_url}")