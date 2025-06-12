import sqlite3
import random
import requests
import socket 
import time

from config import BOOTSTRAP_URL
from news import insert_news

other_nodes = set()

def get_local_ip():
    """Returns the IP address of this machine on the LAN."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def gossip_news(news, fanout=2):
    """Spread news to a random subset of peers, ensuring the news is synced across nodes."""
    peers = list(other_nodes)
    selected_peers = random.sample(peers, min(fanout, len(peers)))

    for peer in selected_peers:
        try:
            response = requests.post(f"{peer}/gossip", json=news, timeout=3)
            if response.status_code == 200:
                insert_news(news['headline'], news['body'], news['author'])
        except requests.exceptions.RequestException:
            continue

def sync_news_with_peer(peer_url):
    """Synchronize news with a peer by getting their news."""
    try:
        response = requests.get(f"{peer_url}/nodes")
        if response.status_code == 200:
            all_news = response.json().get('news', [])
            for news_item in all_news:
                if not is_news_in_db(news_item):
                    insert_news(news_item['headline'], news_item['body'], news_item['author'])
    except requests.exceptions.RequestException:
        pass

def is_news_in_db(news_item):
    """Check if a news item is already in the local database."""
    conn = sqlite3.connect('news.db')
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM news WHERE content = ?', (news_item['content'],))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def find_free_port(start_port, max_tries):
    """Find a free port to run the node on."""
    for port in range(start_port, start_port + max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', port))  # binds to all interfaces (0.0.0.0)
                s.listen(1)
                return port
            except OSError:
                continue
    raise RuntimeError("No free ports found in range.")

def try_register_with_bootstrap(port):
    """Try registering the node with the bootstrap node."""
    global this_node_url
    ip = get_local_ip()
    this_node_url = f"http://{ip}:{port}"

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
            print("Failed to connect to bootstrap node.")
    except requests.exceptions.RequestException:
        print("Bootstrap node not reachable, starting new network.")

