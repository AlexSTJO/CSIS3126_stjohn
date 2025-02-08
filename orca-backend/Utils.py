from cryptography.fernet import Fernet
import base64


def encrypt_secret(secret, encryption_key):
    if isinstance(encryption_key, str):
        encryption_key = encryption_key.encode()

    suite = Fernet(encryption_key)
    return suite.encrypt(secret.encode())  

def decrypt_secret(encrypted_secret, decryption_key):
    if isinstance(encrypted_secret, str):
        encrypted_secret = encrypted_secret.encode()  
    suite = Fernet(decryption_key.encode())
    return suite.decrypt(encrypted_secret).decode()
