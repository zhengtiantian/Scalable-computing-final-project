"""
Symmetric Encryption and decryption fuction using SHA 256
"""
__author__ = "JIACHUAN WANG(IAN)"
__email__ = "wangj3@tcd.ie"
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
password_provided = '123'
password = password_provided.encode()

salt = b"\xb9\x1f|}'S\xa1\x96\xeb\x154\x04\x88\xf3\xdf\x05"

kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
                 length=32,
                 salt=salt,
                 iterations=100000,
                 backend=default_backend())

key = base64.urlsafe_b64encode(kdf.derive(password))
fernet = Fernet(key)



def encrypted(data):
    encrypted_data = fernet.encrypt(data)
    print('Encrypted data from {} to {}'.format(data, encrypted_data))
    return encrypted_data

def decrypted(data):
    decrypted_data = fernet.decrypt(data)
    print('Decrypted data: {}'.format(decrypted_data))
    return decrypted_data

if __name__ == '__main__':
    print(key)

    data = 'hello'.encode()
    fernet = Fernet(key)
    decrypted(encrypted(data))