import socket
from encryption import AESCipher
aes = AESCipher("SecureKey123456")  # Same key as server

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 5555))  # Replace with the server's IP

name = input("Enter your device name: ")
client.send(name.encode())

def receive_messages():
    while True:
        try:
            message = client.recv(1024).decode()
            print("\n" + message)
        except:
            break

# Start receiving messages in a separate thread
import threading
threading.Thread(target=receive_messages, daemon=True).start()

while True:
    receiver = input("\nEnter receiver's name: ")
    message = input("Enter message: ")

    encrypted_message = aes.encrypt(message)
    client.send(f"{name}|{receiver}|{encrypted_message}".encode())