from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import x25519, ed25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.exceptions import InvalidSignature
from .provider import CryptoProvider, KeyPair

class ClassicalFallbackProvider(CryptoProvider):
    name = "DEV FALLBACK: X25519 + Ed25519"

    def generate_kem_keypair(self):
        sk=x25519.X25519PrivateKey.generate(); pk=sk.public_key()
        return KeyPair(pk.public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw),
                       sk.private_bytes(serialization.Encoding.Raw,serialization.PrivateFormat.Raw,serialization.NoEncryption()))

    def encapsulate(self, recipient_public_key):
        r=x25519.X25519PublicKey.from_public_bytes(recipient_public_key)
        eph=x25519.X25519PrivateKey.generate()
        shared=eph.exchange(r)
        key=HKDF(algorithm=hashes.SHA256(),length=32,salt=None,info=b"provenance-x-envelope").derive(shared)
        ct=eph.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
        return ct,key

    def decapsulate(self, private_key, ciphertext):
        sk=x25519.X25519PrivateKey.from_private_bytes(private_key)
        shared=sk.exchange(x25519.X25519PublicKey.from_public_bytes(ciphertext))
        return HKDF(algorithm=hashes.SHA256(),length=32,salt=None,info=b"provenance-x-envelope").derive(shared)

    def generate_signing_keypair(self):
        sk=ed25519.Ed25519PrivateKey.generate(); pk=sk.public_key()
        return KeyPair(pk.public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw),
                       sk.private_bytes(serialization.Encoding.Raw,serialization.PrivateFormat.Raw,serialization.NoEncryption()))

    def sign(self, private_key, message):
        return ed25519.Ed25519PrivateKey.from_private_bytes(private_key).sign(message)

    def verify(self, public_key, message, signature):
        try:
            ed25519.Ed25519PublicKey.from_public_bytes(public_key).verify(signature,message); return True
        except InvalidSignature: return False
