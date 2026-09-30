# 🛡️ Provenance-X: Advanced Digital Evidence Integrity Platform

> **Smart India Hackathon (SIH 2026) Submission**  
> A zero-friction, cryptographic forensic platform engineered to enforce immutable digital evidence integrity, multi-party witness consensus, and automated audit-ready reporting.

---

## 📌 Problem & Executive Summary

In digital forensics, legal disputes, and custody handovers, digital media is vulnerable to silent bit manipulation, metadata spoofing, and adversarial attacks. Traditional chain-of-custody logging often relies on centralized or manual documentation that lacks real-time mathematical verifiability.

**Provenance-X** solves this with an isolated, verifiable architecture:
* **Client-Side & Server-Side Dual Sealing:** Instant SHA-256 fingerprinting paired with Merkle tree verification.
* **Decentralized Witness Protocol:** Multi-party threshold verification and dynamic trust scoring for investigating officers, labs, and custodians.
* **Automated Forensic Reporting:** Generation of tamper-evident forensic certificates for court and audit compliance.
* **Isolated Read-Only Viewer:** Zero-alteration metadata inspector preventing accidental modification of file timestamps or headers.

---

## 🏗️ Core System Modules

### 1. 🔍 Cryptographic Evidence Intake & Verification
* **Dual-Tier Hashing:** Calculates cryptographic fingerprints in-browser via the Web Crypto API (`crypto.subtle`) and validates them against the backend integrity engine.
* **Tamper Detection:** Detects any alteration down to a single byte or pixel.
* **Adversarial Watermark Resilience:** Engineered to withstand adversarial noise and compression through dual-layer (DCT + structural) confidence analysis.

### 2. 👥 Multi-Party Witness Management Program
* **Dynamic Witness Registry:** Tracks participating forensic examiners, investigation officers, and evidence custodians.
* **Trust Scoring & Reputation:** Assigns verifiable trust scores (0–100%) based on verified identity, cryptographic attestation history, and role credentials.
* **Threshold / Quorum Consensus:** Evidence verification requires multi-signature validation from authenticated witness nodes before entering permanent provenance chains.
* **Dynamic Participant Intake:** Real-time form interface to register and authorize new investigation officers and forensic units.

### 3. 📄 Audit-Ready Report Generation Engine
* **Automated Compliance Certificates:** Generates comprehensive forensic integrity documentation assigned deterministic serial identifiers (e.g., `RPT-2026-XXX`).
* **Cryptographic Attestation Inclusion:** Embeds SHA-256 hashes, file dimensions, MIME types, timestamps, and integrity status directly in the report manifest.
* **Witness Audit Trail:** Lists every verified witness, their designated forensic role, and corresponding trust score at the time of report compilation.
* **Export-Ready Output:** Structured view ready for legal discovery, regulatory review, and court submission.

### 4. ◈ Immutable Provenance Chain
* **Chronological Event Logging:** Automatically tracks lifecycle events:
  1. Evidence intake & registration
  2. Cryptographic fingerprint calculation
  3. Verification engine pass/fail audit
  4. Witness signing and consensus
* **Tamper-Evident History:** Formatted as an auditable sequence preventing retroactive log manipulation.

### 5. ◉ Secure Read-Only Viewer
* **Non-Invasive Inspection Sandbox:** Isolated file inspection interface that protects original file attributes, EXIF data, and filesystem metadata from read/write corruption.
* **Live System Status Bar:** Real-time indicator monitoring backend API connectivity, cryptographic engine health, and active operational states.

---

## 💻 Tech Stack

| Domain | Technology |
| :--- | :--- |
| **Frontend UI** | React 18, Vite 6, Modern CSS Engine |
| **Backend API** | Python 3.11+, FastAPI, Uvicorn |
| **Integrity & Cryptography** | Web Crypto API (Client), SHA-256, Merkle Tree Proofs |
| **Automated Testing** | Pytest, Pytest-Mock |
| **Execution Environment** | Isolated Local Host / Air-Gapped Forensic Enclave |

---

## 🧪 Automated Test Suite (Validation Proof)

The core cryptographic algorithms and integrity pipelines are verified through an automated test suite:

```bash
cd backend
pytest tests/ -v
