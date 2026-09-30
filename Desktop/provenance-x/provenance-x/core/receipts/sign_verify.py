import base64
from uuid import uuid4
from datetime import datetime,timezone
from shared.schemas.models import Receipt,Endorsement
from .canonicalize import canonical_json_bytes

def unsigned(r):
    d=r.model_dump(); d["signature_b64"]=""; return d

def create_receipt(manifest_sha256,document_id,issuer_id,provider):
    r=Receipt(receipt_id=str(uuid4()),document_id=document_id,manifest_sha256=manifest_sha256,
             issued_at=datetime.now(timezone.utc).isoformat(),issuer_id=issuer_id,provider=provider.name)
    return r,canonical_json_bytes(unsigned(r))

def sign_receipt(r,private,provider):
    r.signature_b64=base64.b64encode(provider.sign(private,canonical_json_bytes(unsigned(r)))).decode(); return r

def verify_receipt(r,public,provider):
    return provider.verify(public,canonical_json_bytes(unsigned(r)),base64.b64decode(r.signature_b64))

def endorse(r,wid,private,provider):
    payload=canonical_json_bytes({"receipt_id":r.receipt_id,"witness_id":wid,"issued_at":r.issued_at})
    return Endorsement(receipt_id=r.receipt_id,witness_id=wid,issued_at=r.issued_at,
                       signature_b64=base64.b64encode(provider.sign(private,payload)).decode(),provider=provider.name)

def verify_endorsement(e,public,provider):
    payload=canonical_json_bytes({"receipt_id":e.receipt_id,"witness_id":e.witness_id,"issued_at":e.issued_at})
    return provider.verify(public,payload,base64.b64decode(e.signature_b64))
