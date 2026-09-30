# Demo
1. Generate a PDF.
2. Derive a recipient-specific HMAC token.
3. Render/embed the token.
4. Seal the original with AES-256-GCM.
5. Sign a receipt.
6. Obtain three witness endorsements and require 2-of-3.
7. Append the receipt to a Merkle log.
8. Investigate the leaked PDF.
