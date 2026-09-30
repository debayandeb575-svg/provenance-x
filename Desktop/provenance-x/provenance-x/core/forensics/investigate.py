from core.watermark.extract import extract_token_from_pdf
from core.watermark.structural_embed import extract_structural_trace
from core.receipts.sign_verify import verify_receipt
from core.witness.threshold import check_threshold
from core.merkle.proof import verify_proof
def investigate(path,expected,receipt,issuer_pub,provider,endorsements,witnesses,proof):
    token,confidence=extract_token_from_pdf(path,len(expected))
    return {"file":path,"watermark":{"expected":expected,"recovered":token,"match":token==expected,"confidence":confidence},
            "structural_trace":extract_structural_trace(path),
            "receipt_signature_valid":verify_receipt(receipt,issuer_pub,provider),
            "witness_threshold":check_threshold(receipt,endorsements,witnesses,2),
            "merkle_inclusion_valid":verify_proof(proof)}
