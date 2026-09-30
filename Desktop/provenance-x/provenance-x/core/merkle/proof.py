from shared.schemas.models import MerkleProof
from .log import H
def make_proof(log,index):
    level=log.leaves[:]; idx=index; sib=[]
    while len(level)>1:
        s=idx-1 if idx%2 else idx+1
        if s>=len(level): s=idx
        sib.append(level[s].hex())
        level=[H(b"node:"+level[i]+(level[i+1] if i+1<len(level) else level[i])) for i in range(0,len(level),2)]
        idx//=2
    return MerkleProof(leaf_index=index,leaf_hash=log.leaves[index].hex(),siblings=sib,root=log.root().hex())
def verify_proof(p):
    cur=bytes.fromhex(p.leaf_hash); idx=p.leaf_index
    for sh in p.siblings:
        s=bytes.fromhex(sh); cur=H(b"node:"+s+cur) if idx%2 else H(b"node:"+cur+s); idx//=2
    return cur.hex()==p.root
