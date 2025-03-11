import socket
import threading
from blockchain import Blockchain
from encryption import AESCipher
blockchain = Blockchain()
aes = AESCipher("SecureKey123456")  # Change this key in production

clients = {}  # Store connected clients: {name: (conn, addr)}

def handle_client(conn, addr):
    global blockchain

    conn.send("Enter your device name: ".encode())
    name = conn.recv(1024).decode()
    clients[name] = (conn, addr)

    print(f"[NEW CONNECTION] {name} ({addr}) connected.")

    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break

            sender, receiver, encrypted_message = data.split("|")
            decrypted_message = aes.decrypt(encrypted_message)

            # Store the message in blockchain
            blockchain.add_message(sender, receiver, decrypted_message)

            # Forward the message to the intended receiver
            if receiver in clients:
                receiver_conn, _ = clients[receiver]
                receiver_conn.send(f"From {sender}: {decrypted_message}".encode())

        except Exception as e:
            print(f"Error: {e}")
            break

    conn.close()
    del clients[name]
    print(f"[DISCONNECTED] {name} has left.")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5555))
    server.listen(5)
    print("[SERVER STARTED] Listening on port 5555...")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

start_server()
