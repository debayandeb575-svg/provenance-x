import hashlib
def H(x): return hashlib.sha256(x).digest()
class MerkleLog:
    def __init__(self): self.leaves=[]
    def append(self,value): self.leaves.append(H(b"leaf:"+value)); return len(self.leaves)-1
    def root(self):
        if not self.leaves:return H(b"empty")
        level=self.leaves[:]
        while len(level)>1:
            nxt=[]
            for i in range(0,len(level),2):
                r=level[i+1] if i+1<len(level) else level[i]
                nxt.append(H(b"node:"+level[i]+r))
            level=nxt
        return level[0]
