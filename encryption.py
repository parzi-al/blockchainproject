from Cryptodome.Cipher import AES  # Instead of 'Crypto.Cipher'
import base64
import os

class AESCipher:
    def __init__(self, key):
        self.key = key.ljust(32)[:32].encode()  # Ensure key is 32 bytes

    def encrypt(self, message):
        cipher = AES.new(self.key, AES.MODE_ECB)
        padded_message = message.ljust(32)[:32]  # Padding to 32 bytes
        encrypted = cipher.encrypt(padded_message.encode())
        return base64.b64encode(encrypted).decode()

    def decrypt(self, encrypted_message):
        cipher = AES.new(self.key, AES.MODE_ECB)
        decrypted = cipher.decrypt(base64.b64decode(encrypted_message))
        return decrypted.decode().strip()
