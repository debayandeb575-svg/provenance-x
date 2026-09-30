import json,hashlib
def canonical_json_bytes(obj): return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def canonical_sha256(obj): return hashlib.sha256(canonical_json_bytes(obj)).hexdigest()
