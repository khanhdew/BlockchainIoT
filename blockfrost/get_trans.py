from blockfrost import BlockFrostApi, ApiError, ApiUrls
from blockfrost.api.cardano.transactions import transaction

from wallet.config import project_key
api = BlockFrostApi(
    project_id=f'{project_key}',  # or export environment variable BLOCKFROST_PROJECT_ID
    # optional: pass base_url or export BLOCKFROST_API_URL to use testnet, defaults to ApiUrls.mainnet.value
    base_url=ApiUrls.preview.value,
)
with open("wallet/payment.skey", "r") as f:
    payment_signing_key = f.read()
    print(payment_signing_key)
def get_latest_tx():
    try:
        response = api.address_transactions("")
        print(response)
    except ApiError as e:
        print(f"API error: {e}")
    except Exception as e:
        print(f"Exception: {e}")

def get_metadata_from_tx(tx_hash):
    try:
        response = api.transaction(tx_hash)
        print(response)
    except ApiError as e:
        print(f"API error: {e}")
    except Exception as e:
        print(f"Exception: {e}")