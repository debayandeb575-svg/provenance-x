from shared.crypto.classical_fallback import ClassicalFallbackProvider
from core.receipts.sign_verify import *
def test_receipt():
    p=ClassicalFallbackProvider(); k=p.generate_signing_keypair(); r,_=create_receipt("h","d","i",p)
    sign_receipt(r,k.private_key,p); assert verify_receipt(r,k.public_key,p)
