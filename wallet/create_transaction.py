from importlib.metadata import metadata

from blockfrost import ApiUrls
from from_root import from_root
from pycardano import BlockFrostChainContext, TransactionBuilder, TransactionOutput, Metadata, AuxiliaryData, \
    AlonzoMetadata
from pycardano import PaymentSigningKey, PaymentVerificationKey, Address, Network

from wallet.config import project_key

network = Network.TESTNET
context = BlockFrostChainContext(project_key, base_url=ApiUrls.preview.value)


def create_transaction(sensor_data):
    payment_signing_key = PaymentSigningKey.load(from_root("wallet/payment.skey"))
    payment_verification_key = PaymentVerificationKey.from_signing_key(payment_signing_key)
    from_address = Address(payment_verification_key.hash(), network=network)
    # Metadata follows CIP20 standard
    auxiliary_data = AuxiliaryData(AlonzoMetadata(metadata=Metadata(sensor_data)))
    # Place metadata in AuxiliaryData, the format acceptable by a transaction.
    builder = TransactionBuilder(context)
    builder.auxiliary_data = auxiliary_data
    builder.add_input_address(from_address)
    to_address = from_address
    min_utxo_value = 1000000
    builder.add_output(TransactionOutput(to_address, min_utxo_value))
    signed_tx = builder.build_and_sign([payment_signing_key], change_address=from_address)
    return context.submit_tx(signed_tx)


