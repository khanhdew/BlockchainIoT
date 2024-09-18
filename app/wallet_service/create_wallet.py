from pycardano import Address, Network

from app.wallet_service.generate_keys import load_keys

keys = load_keys()

base_address = Address(payment_part=keys[0].hash(),
                       network=Network.TESTNET)

with open("base.addr", "w") as f:
    f.write(str(base_address))
