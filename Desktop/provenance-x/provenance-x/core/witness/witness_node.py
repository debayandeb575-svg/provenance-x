from dataclasses import dataclass
from core.receipts.sign_verify import endorse,verify_endorsement
@dataclass
class WitnessNode:
    witness_id:str; provider:object; keys:object
    @classmethod
    def create(cls,wid,provider): return cls(wid,provider,provider.generate_signing_keypair())
    def endorse(self,receipt): return endorse(receipt,self.witness_id,self.keys.private_key,self.provider)
    def verify(self,e,receipt): return e.receipt_id==receipt.receipt_id and verify_endorsement(e,self.keys.public_key,self.provider)
