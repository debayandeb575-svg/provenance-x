import fitz,cv2,numpy as np
def embed_token_on_page(page,token,out_path,dpi=144):
    pix=page.get_pixmap(dpi=dpi,alpha=False)
    img=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,pix.n)
    if pix.n==4: img=cv2.cvtColor(img,cv2.COLOR_RGBA2BGR)
    else: img=cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY).astype(np.float32)
    bits=[int(b) for x in token.encode() for b in f"{x:08b}"]
    i=0
    for y in range(0,gray.shape[0]-7,8):
        for x in range(0,gray.shape[1]-7,8):
            if i>=len(bits): break
            d=cv2.dct(gray[y:y+8,x:x+8]); v=(d[3,4]+d[4,3])/2
            mag=abs(v); target=mag+5 if bits[i] else max(0,mag-5)
            s=1 if v>=0 else -1; d[3,4]=d[4,3]=s*target
            gray[y:y+8,x:x+8]=cv2.idct(d); i+=1
        if i>=len(bits): break
    out=np.clip(gray,0,255).astype(np.uint8)
    ok,enc=cv2.imencode(".png",out)
    if not ok: raise RuntimeError("PNG encoding failed")
    doc=fitz.open(); p=doc.new_page(width=page.rect.width,height=page.rect.height)
    p.insert_image(p.rect,stream=enc.tobytes()); p.set_metadata({"watermark_token":token})
    doc.save(out_path); doc.close()
