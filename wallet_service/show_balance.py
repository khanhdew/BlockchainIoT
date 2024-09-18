import requests

from wallet_service.config import project_key

# Thay thế bằng API Key của bạn và địa chỉ ví cần kiểm tra
API_KEY = project_key
ADDRESS = 'addr_test1vzv4dx2g096tlq8f5l60le4p79unlny36h04tedc07d09eq0udqsz'
BLOCKFROST_API_URL = 'https://cardano-preview.blockfrost.io/api/v0'  # Thay đổi nếu bạn dùng mainnet

headers = {
    'project_id': API_KEY
}

def get_balance(address):
    url = f"{BLOCKFROST_API_URL}/addresses/{address}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        balance = data['amount'][0]['quantity']
        print(f"Số dư ADA của địa chỉ {address} là: {int(balance) / 1000000} ADA")  # Balance trả về là satoshis, chia cho 1 triệu để chuyển sang ADA
    else:
        print(f"Error: {response.status_code} - {response.text}")

get_balance(ADDRESS)
