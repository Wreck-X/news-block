from flask import Flask
from routes import bp
from network import find_free_port, try_register_with_bootstrap, other_nodes
from config import START_PORT, MAX_PORT_TRIES
from flask_cors import CORS

app = Flask(__name__)
app.register_blueprint(bp)
CORS(app)
if __name__ == '__main__':
    port = find_free_port(START_PORT, MAX_PORT_TRIES)
    try_register_with_bootstrap(port)

    print(f"Node started at http://0.0.0.0:{port}")

    app.run(host='0.0.0.0', port=port)

