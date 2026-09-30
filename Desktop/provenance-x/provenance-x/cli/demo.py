from pathlib import Path
import hashlib, json
from reportlab.pdfgen import canvas
from shared.crypto.classical_fallback import ClassicalFallbackProvider
from core.sealing.manifest import build_manifest
from core.sealing.seal import seal_package,decrypt_package
from core.watermark.derive import derive_watermark
from core.watermark.structural_embed import embed_structural_trace
from core.receipts.sign_verify import create_receipt,sign_receipt
from core.witness.witness_node import WitnessNode
from core.witness.threshold import check_threshold
from core.merkle.log import MerkleLog
from core.merkle.proof import make_proof
from core.forensics.investigate import investigate

ROOT=Path(__file__).resolve().parents[1]; DEMO=ROOT/"demo_data"; STATE=DEMO/"demo_state"
SOURCE=DEMO/"source_pdfs"/"source.pdf"; LEAK=DEMO/"leaked_samples"/"leaked.pdf"

def main():
    SOURCE.parent.mkdir(parents=True,exist_ok=True); LEAK.parent.mkdir(parents=True,exist_ok=True); STATE.mkdir(exist_ok=True)
    c=canvas.Canvas(str(SOURCE)); c.drawString(72,750,"PROVENANCE-X DEMO DOCUMENT"); c.drawString(72,720,"Confidential provenance demonstration"); c.save()
    data=SOURCE.read_bytes(); p=ClassicalFallbackProvider()
    recipient=p.generate_kem_keypair(); rid="alice"; dh=hashlib.sha256(data).hexdigest()
    token=derive_watermark(b"demo-secret",dh,rid)
    # Structural token makes this deterministic demo easy to inspect.
    import shutil; shutil.copy2(SOURCE,LEAK); embed_structural_trace(str(SOURCE),str(LEAK),token)
    m=build_manifest(SOURCE.name,data,token,p.name,[rid]); pkg=seal_package(data,m,p,{rid:recipient.public_key})
    assert decrypt_package(pkg,rid,recipient.private_key,p)==data
    issuer=p.generate_signing_keypair(); receipt,_=create_receipt(m.sha256,m.document_id,"issuer",p)
    sign_receipt(receipt,issuer.private_key,p)
    ws={f"w{i}":WitnessNode.create(f"w{i}",p) for i in range(3)}
    es=[ws["w0"].endorse(receipt),ws["w1"].endorse(receipt),ws["w2"].endorse(receipt)]
    print("2-of-3:",check_threshold(receipt,es,ws))
    log=MerkleLog(); idx=log.append(receipt.model_dump_json().encode()); proof=make_proof(log,idx)
    report=investigate(str(LEAK),token,receipt,issuer.public_key,p,es,ws,proof)
    (STATE/"report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    (STATE/"receipt.json").write_text(receipt.model_dump_json(indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2))
if __name__=="__main__": main()
