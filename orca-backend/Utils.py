from cryptography.fernet import Fernet
import base64

def encrypt_secret(secret, encryption_key):
    suite = Fernet(encryption_key.encode())
    return suite.encrypt(secret.encode())

def decrypt_secret(encrypted_secret, decryption_key):
    suite = Fernet(decryption_key.encode())
    return suite.decrypt(encrypted_secret).decode()

