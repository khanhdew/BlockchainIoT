from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import random
letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']

class EncryptModel:
    key = ""
    def __init__(self):
        self.gen_key()
        self.write_key()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(EncryptModel, cls).__new__(cls)
        return cls.instance

    def write_key(self):
        with open("key.key", "wb") as f:
            f.write(self.key.encode('utf-8'))

    def gen_key(self):
        # Generate a strong key with 16 characters
        key = ""
        # Random order of letters, numbers and symbols
        order = letters + numbers + symbols
        random.shuffle(order)
        for i in range(32):
            key += random.choice(order)
        print(key)
        self.key = key

    def encrypt(self,data):
        cipher = AES.new(self.key.encode('utf-8'), AES.MODE_CTR)
        encrypted_data = cipher.encrypt(data.encode('utf-8'))
        return base64.b64encode(cipher.nonce + encrypted_data).decode('utf-8')

    def decrypt(self,encrypted_data):
        encrypted_data = base64.b64decode(encrypted_data)
        nonce = encrypted_data[:16]
        cipher = AES.new(self.key.encode('utf-8'), AES.MODE_CTR, nonce=nonce)
        decrypted_data = cipher.decrypt(encrypted_data[16:])
        return decrypted_data.decode('utf-8')

    def get_key(self):
        return self.key
