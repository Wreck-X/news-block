# app.py
from flask import Flask
from routes import bp as routes_bp
from network import find_free_port, try_register_with_bootstrap, other_nodes, initialize_node_url
import logging
import os
import sys
import socket
from flask_cors import CORS

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Register blueprints
app.register_blueprint(routes_bp)
CORS(app)
if __name__ == "__main__":
    # Clear other_nodes to ensure clean state
    other_nodes.clear()
    logger.info("Cleared other_nodes set at startup")

    # Default bootstrap URL
    bootstrap_url = os.getenv('BOOTSTRAP_URL', 'http://localhost:5000')
    
    # Determine if this is the bootstrap node
    port = 5000  # Default for bootstrap
    node_url = os.getenv('NODE_URL', f'http://localhost:{port}')
    
    if bootstrap_url == node_url:
        # First node: Try port 5000 or find a free port
        port = find_free_port(5000)  # Start at 5000, find free port if needed
        node_url = f'http://localhost:{port}'
        if port != 5000:
            logger.warning(f"Default bootstrap port 5000 was in use. Using port {port} instead.")
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
        except OSError as e:
            logger.error(f"Port {port} is already in use. Error: {str(e)}")
            logger.error("Please stop other processes using the port or set a different BOOTSTRAP_URL.")
            sys.exit(1)
    else:
        # Non-bootstrap node: Find a free port
        port = find_free_port(5001)  # Start at 5001 to avoid bootstrap port
        node_url = os.getenv('NODE_URL', f'http://localhost:{port}')
    
    # Initialize this_node_url
    initialize_node_url(port)
    
    # Register with bootstrap node or become bootstrap
    if not try_register_with_bootstrap(bootstrap_url, node_url):
        logger.error("Failed to initialize node. Exiting.")
        sys.exit(1)
    
    logger.info(f"Starting node on {node_url}, other_nodes: {other_nodes}")
    try:
        app.run(host="0.0.0.0", port=port, debug=True)
    except Exception as e:
        logger.error(f"Failed to start Flask server: {str(e)}")
        sys.exit(1)