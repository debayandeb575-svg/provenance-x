from shared.crypto.classical_fallback import ClassicalFallbackProvider
from core.receipts.sign_verify import create_receipt
from core.witness.witness_node import WitnessNode
from core.witness.threshold import check_threshold
def test_threshold():
    p=ClassicalFallbackProvider(); r,_=create_receipt("h","d","i",p)
    ws={f"w{i}":WitnessNode.create(f"w{i}",p) for i in range(3)}
    es=[ws["w0"].endorse(r),ws["w1"].endorse(r)]
    assert check_threshold(r,es,ws,2)["satisfied"]
