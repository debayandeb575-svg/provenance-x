from core.merkle.log import MerkleLog
from core.merkle.proof import make_proof,verify_proof
def test_proof():
    l=MerkleLog(); [l.append(x) for x in (b"a",b"b",b"c")]; assert verify_proof(make_proof(l,1))
