from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import random
import json
from Crypto.Util.Padding import pad, unpad  # Sử dụng padding PKCS7 từ thư viện Crypto

# Danh sách các ký tự để tạo key ngẫu nhiên
letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
           'w', 'x', 'y', 'z',
           'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
           'W', 'X', 'Y', 'Z']
numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']


def gen_key():
    # Tạo khóa ngẫu nhiên với độ dài 32 ký tự (AES-256)
    key = ""
    order = letters + numbers + symbols
    random.shuffle(order)  # Xáo trộn thứ tự các ký tự
    for i in range(32):  # AES-256 yêu cầu khóa 32 bytes
        key += random.choice(order)
    return key

try:
    with open("key.key", "rb") as f:
        key = f.read().decode('utf-8')
        if not key:  # Kiểm tra nếu file rỗng
            raise ValueError("File is empty")
except (FileNotFoundError, ValueError):
    key = gen_key()
    with open("key.key", "wb") as f:
        f.write(key.encode('utf-8'))


class EncryptModel:
    key = ""  # Khóa sẽ được tạo ngẫu nhiên

    def __init__(self):
        global key
        self.key = key # Tạo khóa ngẫu nhiên

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(EncryptModel, cls).__new__(cls)
        return cls.instance

    def encrypt(self, data: str) -> list:
        """ Mã hóa dữ liệu với AES-256, trả về chuỗi đã mã hóa dưới dạng Base64 chia nhỏ thành nhiều phần """
        cipher = AES.new(self.key.encode('utf-8'), AES.MODE_CBC)  # Sử dụng chế độ CBC với IV ngẫu nhiên
        padded_data = pad(data.encode('utf-8'), AES.block_size)  # Padding PKCS7
        encrypted_data = cipher.encrypt(padded_data)  # Mã hóa dữ liệu
        # Kết hợp IV và dữ liệu đã mã hóa
        encrypted_message = base64.b64encode(cipher.iv + encrypted_data).decode('utf-8')

        # Cắt nhỏ chuỗi mã hóa thành các phần có kích thước tối đa 64 bytes
        chunk_size = 64
        chunks = [encrypted_message[i:i + chunk_size] for i in range(0, len(encrypted_message), chunk_size)]
        return chunks

    def decrypt(self, encrypted_chunks: list) -> str:
        """ Giải mã dữ liệu đã mã hóa, yêu cầu danh sách các chuỗi mã hóa đã chia nhỏ """
        # Ghép các chuỗi nhỏ lại thành một chuỗi mã hóa đầy đủ
        encrypted_message = ''.join(encrypted_chunks)
        encrypted_data = base64.b64decode(encrypted_message)  # Giải mã Base64
        iv = encrypted_data[:AES.block_size]  # Lấy IV từ đầu chuỗi đã mã hóa
        cipher = AES.new(self.key.encode('utf-8'), AES.MODE_CBC, iv)  # Khởi tạo AES với IV
        decrypted_data = unpad(cipher.decrypt(encrypted_data[AES.block_size:]),
                               AES.block_size)  # Giải mã và bỏ padding PKCS7
        return decrypted_data.decode('utf-8')

    def get_key(self) -> str:
        """ Lấy khóa hiện tại """
        return self.key
