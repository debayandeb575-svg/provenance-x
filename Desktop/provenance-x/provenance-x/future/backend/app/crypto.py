from pathlib import Path
import base64
import hashlib

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

from cryptography.hazmat.primitives import serialization

from .config import get_settings


settings = get_settings()


def sha256_bytes(data: bytes) -> str:

    return hashlib.sha256(data).hexdigest()


def canonical_bytes(*parts) -> bytes:

    return "|".join(
        "" if p is None else str(p)
        for p in parts
    ).encode("utf-8")


def _load_or_create_key():

    path = Path(
        settings.signing_key_file
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if path.exists():

        return serialization.load_pem_private_key(
            path.read_bytes(),
            password=None
        )

    key = Ed25519PrivateKey.generate()

    path.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )

    return key


PRIVATE_KEY = _load_or_create_key()

PUBLIC_KEY = PRIVATE_KEY.public_key()


def sign(data: bytes) -> str:

    signature = PRIVATE_KEY.sign(data)

    return base64.b64encode(
        signature
    ).decode("utf-8")


def verify_signature(
    data: bytes,
    signature: str
) -> bool:

    try:

        PUBLIC_KEY.verify(
            base64.b64decode(signature),
            data
        )

        return True

    except Exception:

        return False


def public_key_pem() -> str:

    return PUBLIC_KEY.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")