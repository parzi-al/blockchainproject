from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO
import json, os, time, base64, hashlib
from Cryptodome.Cipher import AES
from web3 import Web3

# Connect to Ganache (Local Blockchain)
GANACHE_URL = "http://127.0.0.1:7545"
CONTRACT_ADDRESS = "0xE49cC01d306279743A4075DB76B9aFD44E68Fa1d"
PRIVATE_KEY = "0x4be21f19aa1319825a5a270df42251874ab75fb73e60d8c8c35b18bda9cb6e6c"
ACCOUNT_ADDRESS = "0xc277768203cB66A3672C190b52B0BB7037a3eEA4"

web3 = Web3(Web3.HTTPProvider(GANACHE_URL))

with open("MessageStoreABI.json") as f:
    contract_abi = json.load(f)

contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

BLOCKCHAIN_FILE = "blockchain.json"
clients = {}  # Store connected clients

# AES-GCM Encryption
class AESCipher:
    def __init__(self, key="SecureKey123456"):
        self.key = key.ljust(32)[:32].encode()

    def encrypt(self, message):
        cipher = AES.new(self.key, AES.MODE_GCM)
        nonce, ciphertext, tag = cipher.nonce, *cipher.encrypt_and_digest(message.encode())
        return base64.b64encode(nonce + tag + ciphertext).decode()

    def decrypt(self, encrypted_message):
        raw = base64.b64decode(encrypted_message)
        nonce, tag, ciphertext = raw[:16], raw[16:32], raw[32:]
        return AES.new(self.key, AES.MODE_GCM, nonce=nonce).decrypt_and_verify(ciphertext, tag).decode()

aes = AESCipher()

# Blockchain with Persistent Storage
class Blockchain:
    def __init__(self):
        self.chain = self.load_blockchain()

    def add_message(self, sender, receiver, message):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'sender': sender,
            'receiver': receiver,
            'message': message,
            'previous_hash': self.chain[-1]['hash'] if self.chain else "0",
            'hash': hashlib.sha256(json.dumps(message).encode()).hexdigest()
        }
        self.chain.append(block)
        self.save_blockchain()

    def save_blockchain(self):
        with open(BLOCKCHAIN_FILE, "w") as f:
            json.dump(self.chain, f, indent=4)

    def load_blockchain(self):
        return json.load(open(BLOCKCHAIN_FILE)) if os.path.exists(BLOCKCHAIN_FILE) else []

blockchain = Blockchain()

@app.route("/")
def dashboard():
    return render_template("dashboard.html")
@app.route("/disconnect", methods=["POST"])
def disconnect_client():
    data = request.json
    client_name = data.get("name")

    if client_name in clients:
        del clients[client_name]
        socketio.emit("update_clients", clients)  # Notify all clients
        return jsonify({"status": "Disconnected"}), 200
    return jsonify({"error": "Client not found"}), 404

@app.route("/connect", methods=["POST"])
def connect_client():
    data = request.json
    client_name = data.get("name")
    client_ip = request.remote_addr

    if not client_name:
        return jsonify({"error": "Name is required"}), 400

    clients[client_name] = client_ip
    socketio.emit("update_clients", clients)
    return jsonify({"status": "Connected", "clients": clients})

@app.route("/send", methods=["POST"])
def send_message():
    data = request.json
    sender, receiver, message = data.get("sender"), data.get("receiver"), data.get("message")

    if not all([sender, receiver, message]):
        return jsonify({"error": "Missing data"}), 400

    encrypted_message = aes.encrypt(message)
    blockchain.add_message(sender, receiver, encrypted_message)

    # Send transaction to smart contract on Ganache
    txn = contract.functions.storeMessage(receiver, encrypted_message).build_transaction({
        "from": ACCOUNT_ADDRESS,
        "nonce": web3.eth.get_transaction_count(ACCOUNT_ADDRESS),
        "gas": 2000000,
        "gasPrice": web3.to_wei('5', 'gwei')
    })

    signed_txn = web3.eth.account.sign_transaction(txn, PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)

    socketio.emit("new_message", {
        "sender": sender, "receiver": receiver, "message": message, "tx_hash": tx_hash.hex()
    })

    return jsonify({"status": "Message stored", "tx_hash": tx_hash.hex()})


@app.route("/messages", methods=["GET"])
def get_messages():
    return jsonify(blockchain.chain)

@app.route("/clients", methods=["GET"])
def get_clients():
    return jsonify(clients)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
