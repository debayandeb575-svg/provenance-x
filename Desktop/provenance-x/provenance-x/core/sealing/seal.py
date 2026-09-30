import os,base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
def b64(x): return base64.b64encode(x).decode()
def ub64(x): return base64.b64decode(x)

def seal_package(data,manifest,provider,recipients):
    key=AESGCM.generate_key(bit_length=256); nonce=os.urandom(12)
    aad=manifest.model_dump_json().encode()
    ct=AESGCM(key).encrypt(nonce,data,aad); env=[]
    for rid,pub in recipients.items():
        kem,wrap=provider.encapsulate(pub); wn=os.urandom(12)
        wrapped=AESGCM(wrap).encrypt(wn,key,manifest.document_id.encode())
        env.append({"recipient_id":rid,"kem":b64(kem),"wrapped":b64(wrapped),"nonce":b64(wn)})
    return {"manifest":manifest.model_dump(),"nonce":b64(nonce),"ciphertext":b64(ct),"envelopes":env}

def decrypt_package(pkg,rid,private,provider):
    from shared.schemas.models import Manifest
    m=Manifest.model_validate(pkg["manifest"])
    e=next(x for x in pkg["envelopes"] if x["recipient_id"]==rid)
    wrap=provider.decapsulate(private,ub64(e["kem"]))
    key=AESGCM(wrap).decrypt(ub64(e["nonce"]),ub64(e["wrapped"]),m.document_id.encode())
    return AESGCM(key).decrypt(ub64(pkg["nonce"]),ub64(pkg["ciphertext"]),m.model_dump_json().encode())
