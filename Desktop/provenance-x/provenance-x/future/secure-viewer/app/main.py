import hashlib
import hmac
import os
import time
import uuid

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI(
    title="Provenance-X Secure Viewer",
    version="1.0.0",
)


VIEWER_SECRET = os.getenv(
    "VIEWER_SECRET",
    "CHANGE_THIS_VIEWER_SECRET",
)


class ViewerTokenRequest(BaseModel):
    evidence_id: str
    evidence_hash: str


class ViewerTokenResponse(BaseModel):
    token: str
    evidence_id: str
    expires_in: int


def sign_token(
    evidence_id: str,
    evidence_hash: str,
    expiry: int,
) -> str:

    payload = (
        f"{evidence_id}|"
        f"{evidence_hash}|"
        f"{expiry}"
    )

    signature = hmac.new(
        VIEWER_SECRET.encode(),
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()

    return f"{payload}|{signature}"


def verify_token(token: str):

    parts = token.split("|")

    if len(parts) != 4:
        raise HTTPException(
            status_code=401,
            detail="Invalid viewer token",
        )

    evidence_id = parts[0]
    evidence_hash = parts[1]
    expiry = parts[2]
    signature = parts[3]

    try:
        expiry_int = int(expiry)
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid expiry",
        )

    if time.time() > expiry_int:
        raise HTTPException(
            status_code=401,
            detail="Viewer token expired",
        )

    expected = hmac.new(
        VIEWER_SECRET.encode(),
        f"{evidence_id}|"
        f"{evidence_hash}|"
        f"{expiry}".encode(),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(
        expected,
        signature,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid signature",
        )

    return {
        "evidence_id": evidence_id,
        "evidence_hash": evidence_hash,
    }


@app.get("/health")
def health():

    return {
        "service": "secure-viewer",
        "status": "ok",
    }


@app.post(
    "/viewer/token",
    response_model=ViewerTokenResponse,
)
def create_viewer_token(
    request: ViewerTokenRequest,
):

    expiry = int(time.time()) + 300

    token = sign_token(
        request.evidence_id,
        request.evidence_hash,
        expiry,
    )

    return ViewerTokenResponse(
        token=token,
        evidence_id=request.evidence_id,
        expires_in=300,
    )


@app.get("/viewer/{token}")
def view_evidence(token: str):

    evidence = verify_token(token)

    return {
        "viewer": "secure-viewer",
        "access": "authorized",
        "evidence_id": evidence["evidence_id"],
        "evidence_hash": evidence["evidence_hash"],
    }