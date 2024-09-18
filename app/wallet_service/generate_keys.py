from pycardano import PaymentSigningKey, PaymentVerificationKey
def load_keys():
    keys = []
    try:
        payment_signing_key = PaymentSigningKey.load("payment.skey")
        payment_verification_key = PaymentVerificationKey.load("payment.vkey")
        keys.append(payment_verification_key)
        keys.append(payment_signing_key)
        return keys
    except FileNotFoundError:
            payment_signing_key = PaymentSigningKey.generate()
            payment_verification_key = PaymentVerificationKey.from_signing_key(payment_signing_key)
            payment_signing_key.save("payment.skey")
            payment_verification_key.save("payment.vkey")
            return load_keys()