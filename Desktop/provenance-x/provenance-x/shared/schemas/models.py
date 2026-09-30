from pydantic import BaseModel, Field

class Manifest(BaseModel):
    version:str="1"; document_id:str; filename:str; sha256:str; size:int
    created_at:str; watermark_token:str; provider:str; recipients:list[str]=Field(default_factory=list)

class Receipt(BaseModel):
    receipt_id:str; document_id:str; manifest_sha256:str; issued_at:str
    issuer_id:str; signature_b64:str=""; provider:str

class Endorsement(BaseModel):
    receipt_id:str; witness_id:str; issued_at:str; signature_b64:str; provider:str

class MerkleProof(BaseModel):
    leaf_index:int; leaf_hash:str; siblings:list[str]; root:str
