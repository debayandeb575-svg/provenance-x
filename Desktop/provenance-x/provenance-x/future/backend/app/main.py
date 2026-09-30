from datetime import datetime, timezone
from hashlib import sha256
from uuid import uuid4

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# ============================================================
# PROVENANCE-X BACKEND
# ============================================================

app = FastAPI(
    title="Provenance-X API",
    description="Evidence Integrity and Provenance API",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# IN-MEMORY STORAGE
# ============================================================

witnesses = [
    {
        "id": "WIT-001",
        "name": "Investigation Officer",
        "role": "Primary witness",
        "status": "Verified",
        "trust": 98,
        "initials": "IO",
    },
    {
        "id": "WIT-002",
        "name": "Digital Forensics Lab",
        "role": "Forensic examiner",
        "status": "Online",
        "trust": 96,
        "initials": "DF",
    },
    {
        "id": "WIT-003",
        "name": "Evidence Custodian",
        "role": "Custodian",
        "status": "Ready",
        "trust": 94,
        "initials": "EC",
    },
]

# Evidence records are stored here after verification.
evidence_store = {}

# Generated reports are stored here.
reports = []


# ============================================================
# MODELS
# ============================================================

class WitnessCreate(BaseModel):
    name: str
    role: str


class ReportCreate(BaseModel):
    evidence_id: str
    filename: str = "Current evidence set"
    hash: str = ""
    algorithm: str = "SHA-256"


# ============================================================
# HELPERS
# ============================================================

def utc_now():
    return datetime.now(timezone.utc).isoformat()


def witness_initials(name: str):
    parts = name.strip().split()

    if not parts:
        return "W"

    return "".join(
        part[0].upper()
        for part in parts[:2]
    )


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "service": "Provenance-X API",
        "status": "online",
        "version": "1.0.0",
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "backend": "online",
        "timestamp": utc_now(),
    }


# ============================================================
# EVIDENCE VERIFICATION
# ============================================================

@app.post("/evidence/verify")
async def verify_evidence(
    file: UploadFile = File(...)
):
    """
    Upload evidence and calculate SHA-256.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename supplied.",
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    # Calculate SHA-256
    file_hash = sha256(content).hexdigest()

    # Create evidence ID from hash
    evidence_id = f"PX-{file_hash[:5].upper()}"

    record = {
        "evidence_id": evidence_id,
        "filename": file.filename,
        "size": len(content),
        "hash": file_hash,
        "algorithm": "SHA-256",
        "verified": True,
        "timestamp": utc_now(),
        "content_type": (
            file.content_type
            or "application/octet-stream"
        ),
    }

    # Save evidence
    evidence_store[evidence_id] = record

    return record


# ============================================================
# GET ALL EVIDENCE
# ============================================================

@app.get("/api/evidence")
def get_evidence():
    return {
        "evidence": list(evidence_store.values()),
        "count": len(evidence_store),
    }


# ============================================================
# GET ONE EVIDENCE RECORD
# ============================================================

@app.get("/api/evidence/{evidence_id}")
def get_evidence_record(evidence_id: str):

    evidence = evidence_store.get(evidence_id)

    if not evidence:
        raise HTTPException(
            status_code=404,
            detail="Evidence not found.",
        )

    return {
        "evidence": evidence
    }


# ============================================================
# WITNESSES
# ============================================================

@app.get("/api/witnesses")
def get_witnesses():
    return {
        "witnesses": witnesses,
        "count": len(witnesses),
    }


# ============================================================
# ADD WITNESS
# ============================================================

@app.post("/api/witnesses")
def create_witness(
    payload: WitnessCreate
):

    name = payload.name.strip()
    role = payload.role.strip()

    if not name:
        raise HTTPException(
            status_code=400,
            detail="Witness name is required.",
        )

    if not role:
        raise HTTPException(
            status_code=400,
            detail="Witness role is required.",
        )

    # Prevent duplicate names
    for witness in witnesses:
        if witness["name"].lower() == name.lower():
            raise HTTPException(
                status_code=409,
                detail="A witness with this name already exists.",
            )

    witness_id = f"WIT-{len(witnesses) + 1:03d}"

    witness = {
        "id": witness_id,
        "name": name,
        "role": role,
        "status": "Verified",
        "trust": 100,
        "initials": witness_initials(name),
    }

    witnesses.append(witness)

    return {
        "success": True,
        "message": "Witness registered successfully.",
        "witness": witness,
    }


# ============================================================
# GET ONE WITNESS
# ============================================================

@app.get("/api/witnesses/{witness_id}")
def get_witness(witness_id: str):

    for witness in witnesses:

        if witness["id"] == witness_id:
            return {
                "witness": witness
            }

    raise HTTPException(
        status_code=404,
        detail="Witness not found.",
    )


# ============================================================
# REPORTS
# ============================================================

@app.get("/api/reports")
def get_reports():
    return {
        "reports": reports,
        "count": len(reports),
    }


# ============================================================
# GENERATE REPORT
# ============================================================

@app.post("/api/reports")
def create_report(
    payload: ReportCreate
):

    evidence = evidence_store.get(
        payload.evidence_id
    )

    # --------------------------------------------------------
    # If evidence exists, use the stored verified evidence.
    # --------------------------------------------------------

    if evidence:

        filename = evidence["filename"]
        file_hash = evidence["hash"]
        file_size = evidence["size"]
        algorithm = evidence["algorithm"]
        integrity = "Verified"
        backend_verified = True

    else:

        # ----------------------------------------------------
        # Frontend may provide a local verification result.
        # ----------------------------------------------------

        filename = (
            payload.filename
            or "Current evidence set"
        )

        file_hash = payload.hash
        file_size = 0
        algorithm = (
            payload.algorithm
            or "SHA-256"
        )

        integrity = (
            "Verified"
            if file_hash
            else "Pending verification"
        )

        backend_verified = False

    # Snapshot witnesses at report generation time
    witness_snapshot = [
        dict(witness)
        for witness in witnesses
    ]

    report_id = (
        f"RPT-{datetime.now().year}-"
        f"{uuid4().hex[:6].upper()}"
    )

    report = {
        "id": report_id,
        "report_id": report_id,

        "title": "Digital Evidence Integrity Report",

        "date": datetime.now().strftime(
            "%d %b %Y"
        ),

        "generated_at": utc_now(),

        "status": "Ready",

        "evidence_id": payload.evidence_id,

        "filename": filename,

        "file_size": file_size,

        "algorithm": algorithm,

        "hash": file_hash,

        "integrity": integrity,

        "backend_verified": backend_verified,

        "chain_status": (
            "Complete"
            if len(witness_snapshot) > 0
            else "Requires witnesses"
        ),

        "witness_count": len(
            witness_snapshot
        ),

        "witnesses": witness_snapshot,
    }

    # Save report
    reports.insert(0, report)

    return {
        "success": True,
        "message": "Report generated successfully.",
        "report": report,
    }


# ============================================================
# GET ONE REPORT
# ============================================================

@app.get("/api/reports/{report_id}")
def get_report(report_id: str):

    for report in reports:

        if (
            report["id"] == report_id
            or report.get("report_id") == report_id
        ):
            return {
                "report": report
            }

    raise HTTPException(
        status_code=404,
        detail="Report not found.",
    )


# ============================================================
# DELETE REPORT
# ============================================================

@app.delete("/api/reports/{report_id}")
def delete_report(report_id: str):

    for index, report in enumerate(reports):

        if report["id"] == report_id:

            deleted = reports.pop(index)

            return {
                "success": True,
                "message": "Report deleted.",
                "report": deleted,
            }

    raise HTTPException(
        status_code=404,
        detail="Report not found.",
    )


# ============================================================
# STATISTICS
# ============================================================

@app.get("/api/stats")
def get_stats():

    verified_count = sum(
        1
        for evidence in evidence_store.values()
        if evidence.get("verified")
    )

    average_trust = (
        round(
            sum(
                witness["trust"]
                for witness in witnesses
            )
            / len(witnesses)
        )
        if witnesses
        else 0
    )

    return {
        "evidence": len(evidence_store),
        "verified": verified_count,
        "pending": 0,
        "alerts": 0,
        "witnesses": len(witnesses),
        "reports": len(reports),
        "average_witness_trust": average_trust,
    }