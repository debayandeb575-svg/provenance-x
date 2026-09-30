from shared.crypto.classical_fallback import ClassicalFallbackProvider
from core.sealing.manifest import build_manifest
from core.sealing.seal import seal_package,decrypt_package
def test_roundtrip():
    p=ClassicalFallbackProvider(); k=p.generate_kem_keypair(); data=b"secret"
    m=build_manifest("a",data,"x"*24,p.name,["a"]); pkg=seal_package(data,m,p,{"a":k.public_key})
    assert decrypt_package(pkg,"a",k.private_key,p)==data
