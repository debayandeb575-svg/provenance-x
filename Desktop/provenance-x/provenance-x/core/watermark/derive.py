import hmac,hashlib
def derive_watermark(secret,document_hash,recipient_id,length=24):
    return hmac.new(secret,f"provenance-x|{document_hash}|{recipient_id}".encode(),hashlib.sha256).hexdigest()[:length]
def commitment(secret,token):
    return hmac.new(secret,token.encode(),hashlib.sha256).hexdigest()
