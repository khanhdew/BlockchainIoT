from blockfrost import BlockFrostApi, ApiError, ApiUrls
import requests
from from_root import from_root

from app.wallet_service import config
from app.database.connector import Connector

conn = Connector()

api = BlockFrostApi(
    project_id=f'{config.project_key}',  # or export environment variable BLOCKFROST_PROJECT_ID
    # optional: pass base_url or export BLOCKFROST_API_URL to use testnet, defaults to ApiUrls.mainnet.value
    base_url=ApiUrls.preview.value,
)
wallet_address =""
with open(from_root("app/wallet_service","base.addr")) as f:
    wallet_address = f.readline()
async def get_latest_tx():
    try:
        cursor = conn.execute(f"select * from \"transaction\" order by id desc limit 1")
        tx_hash = ""
        for row in cursor:
            tx_hash = row[1]
        return tx_hash
    except ApiError as e:
        print(f"API error: {e}")
    except Exception as e:
        print(f"Exception: {e}")

async def get_metadata_from_tx(tx_hash):
    try:
        response = requests.get("https://cardano-preview.blockfrost.io/api/v0/txs/" + tx_hash +"/metadata",
                                headers={"project_id": config.project_key})
        # print(response.json()[0]['json_metadata'])
        metadata = response.json()[0]['json_metadata']
        return metadata
    except ApiError as e:
        print(f"API error: {e}")
    except Exception as e:
        print(f"Exception: {e}")
    return None
