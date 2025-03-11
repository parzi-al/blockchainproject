import hashlib
import json
import time
import rsa

# Generate RSA keys for encryption/decryption
(pubkey, privkey) = rsa.newkeys(512)

class Block:
    def __init__(self, index, timestamp, sender, receiver, message, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.sender = sender
        self.receiver = receiver
        self.message = message  # Encrypted message
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, time.time(), "Genesis", "Genesis", "First Block", "0")
        self.chain.append(genesis_block)

    def add_block(self, sender, receiver, message):
        encrypted_msg = rsa.encrypt(message.encode(), pubkey)  # Encrypt message
        previous_block = self.chain[-1]
        new_block = Block(len(self.chain), time.time(), sender, receiver, encrypted_msg.hex(), previous_block.hash)
        self.chain.append(new_block)

    def is_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True

    def display_chain(self):
        for block in self.chain:
            print(f"\nBlock {block.index}:")
            print(f"  Sender: {block.sender}")
            print(f"  Receiver: {block.receiver}")
            print(f"  Encrypted Message: {block.message}")
            print(f"  Hash: {block.hash}")
            print("-" * 50)

# Initialize blockchain
blockchain = Blockchain()

while True:
    sender = input("Enter sender name: ")
    receiver = input("Enter receiver name: ")
    message = input("Enter message: ")

    blockchain.add_block(sender, receiver, message)

    # Display the blockchain
    blockchain.display_chain()

    # Option to continue or stop
    cont = input("Do you want to add another message? (yes/no): ").strip().lower()
    if cont != "yes":
        break

# Decrypt the last message
last_block = blockchain.chain[-1]
decrypted_msg = rsa.decrypt(bytes.fromhex(last_block.message), privkey).decode()
print(f"\nDecrypted Last Message:\n  {last_block.sender} -> {last_block.receiver}: {decrypted_msg}")
