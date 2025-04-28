import socket
import random
import requests
import time
from config import BOOTSTRAP_URL

other_nodes = set()
this_node_url = None

def find_free_port(start_port, max_tries):
    for port in range(start_port, start_port + max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                s.listen(1)
                return port
            except OSError:
                continue
    raise RuntimeError("No free ports found in range.")

def try_register_with_bootstrap(port):
    global this_node_url
    this_node_url = f"http://localhost:{port}"

    if port == 5000:
        print("Bootstrap node, no need to register.")
        return

    try:
        time.sleep(1)
        response = requests.post(f"{BOOTSTRAP_URL}/register", json={"node_url": this_node_url}, timeout=5)
        if response.status_code == 200:
            nodes_info = response.json()
            other_nodes.update(nodes_info.get('all_nodes', []))
            other_nodes.add(BOOTSTRAP_URL)
            other_nodes.discard(this_node_url)
            print(f"Connected to network via {BOOTSTRAP_URL}")
        else:
            print(f"Failed to connect to bootstrap node.")
    except requests.exceptions.RequestException:
        print("Bootstrap node not reachable, starting new network.")

def gossip_news(news, fanout=2):
    """
    Spread news to 'fanout' random peers instead of all peers at once.
    """
    peers = list(other_nodes)
    selected_peers = random.sample(peers, min(fanout, len(peers)))

    for peer in selected_peers:
        try:
            requests.post(f"{peer}/gossip", json=news, timeout=3)
        except requests.exceptions.RequestException:
            continue
