from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class KeyPair:
    public_key: bytes
    private_key: bytes

class CryptoProvider(ABC):
    name = "abstract"
    @abstractmethod
    def generate_kem_keypair(self): ...
    @abstractmethod
    def encapsulate(self, recipient_public_key): ...
    @abstractmethod
    def decapsulate(self, private_key, ciphertext): ...
    @abstractmethod
    def generate_signing_keypair(self): ...
    @abstractmethod
    def sign(self, private_key, message): ...
    @abstractmethod
    def verify(self, public_key, message, signature): ...
