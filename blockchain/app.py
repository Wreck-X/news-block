from flask import Flask
from routes import bp
from network import find_free_port, try_register_with_bootstrap, other_nodes
from config import START_PORT, MAX_PORT_TRIES

app = Flask(__name__)
app.register_blueprint(bp)

if __name__ == '__main__':
    port = find_free_port(START_PORT, MAX_PORT_TRIES)
    try_register_with_bootstrap(port)

    print(f"Node started at http://localhost:{port}")

    app.run(host='localhost', port=port)

