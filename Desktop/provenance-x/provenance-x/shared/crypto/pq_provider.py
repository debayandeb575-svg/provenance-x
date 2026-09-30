class PQProvider:
    # Optional liboqs adapter. API details differ between liboqs-python releases.
    # This class deliberately fails instead of pretending the fallback is PQ-secure.
    name = "PQ: ML-KEM-768 + ML-DSA-65"
    def __init__(self):
        try: import oqs
        except ImportError as e:
            raise RuntimeError("Compatible liboqs-python is required for PQProvider") from e
        self.oqs=oqs
        if not hasattr(oqs,"KeyEncapsulation") or not hasattr(oqs,"Signature"):
            raise RuntimeError("Unsupported liboqs-python API")
    def _unsupported(self): raise NotImplementedError("Adapt this adapter to your installed liboqs-python API")
    generate_kem_keypair=_unsupported
    encapsulate=_unsupported
    decapsulate=_unsupported
    generate_signing_keypair=_unsupported
    sign=_unsupported
    verify=_unsupported
