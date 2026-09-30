import hashlib,json
from uuid import uuid4
from datetime import datetime,timezone
from shared.schemas.models import Manifest

def build_manifest(filename,data,token,provider,recipients):
    return Manifest(document_id=str(uuid4()),filename=filename,sha256=hashlib.sha256(data).hexdigest(),
                    size=len(data),created_at=datetime.now(timezone.utc).isoformat(),
                    watermark_token=token,provider=provider,recipients=recipients)

def canonical_manifest(manifest):
    return json.dumps(manifest.model_dump(),sort_keys=True,separators=(",",":")).encode()
