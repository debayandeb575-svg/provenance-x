import fitz
def embed_structural_trace(src,dst,trace):
    doc=fitz.open(src); meta=doc.metadata
    meta["keywords"]=f"provenance-x-trace:{trace}"; meta["producer"]="Provenance-X"
    doc.set_metadata(meta); doc.save(dst); doc.close()
def extract_structural_trace(path):
    doc=fitz.open(path); meta=doc.metadata or {}
    text=(meta.get("keywords") or "")+" "+(meta.get("subject") or "")
    marker="provenance-x-trace:"
    return text.split(marker,1)[1].split()[0] if marker in text else None
