import requests
import socketio

SERVER_URL = "http://127.0.0.1:5000"

# Initialize Socket.IO client
sio = socketio.Client()

name = input("Enter your name: ")
requests.post(f"{SERVER_URL}/connect", json={"name": name})

@sio.event
def connect():
    print("[Connected to Server]")

@sio.on("new_message")
def receive_message(data):
    if data["receiver"] == name:  # Show only messages meant for this client
        print(f"\n[New Message] {data['sender']} → {data['receiver']}: {data['message']}\n")

sio.connect(SERVER_URL)

def send_message():
    receiver = input("Receiver's name: ")
    message = input("Message: ")
    response = requests.post(f"{SERVER_URL}/send", json={"sender": name, "receiver": receiver, "message": message})
    print(response.json())

while True:
    choice = input("\n1. Send Message\n2. Exit\nChoice: ")
    if choice == "1":
        send_message()
    elif choice == "2":
        break
    else:
        print("Invalid choice, try again.")

sio.disconnect()
