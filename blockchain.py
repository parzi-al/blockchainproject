import hashlib
import json
import time

class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block(previous_hash="0", proof=1, message="Genesis Block")

    def create_block(self, proof, previous_hash, sender="", receiver="", message=""):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'sender': sender,
            'receiver': receiver,
            'message': message,
            'proof': proof,
            'previous_hash': previous_hash
        }
        self.chain.append(block)
        return block

    def get_last_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        while True:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == "0000":
                return new_proof
            new_proof += 1

    def hash(self, block):
        return hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()

    def add_message(self, sender, receiver, message):
        last_block = self.get_last_block()
        proof = self.proof_of_work(last_block['proof'])
        previous_hash = self.hash(last_block)
        return self.create_block(proof, previous_hash, sender, receiver, message)
