from core.watermark.derive import derive_watermark
def test_token():
    assert derive_watermark(b"s","hash","alice")==derive_watermark(b"s","hash","alice")
