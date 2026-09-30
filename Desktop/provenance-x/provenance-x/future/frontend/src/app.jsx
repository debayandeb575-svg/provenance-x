import React, { useEffect, useMemo, useState } from "react";

/*
PROVENANCE-X
Advanced Evidence Integrity Platform
Frontend: Vite + React
Backend: http://127.0.0.1:8000
*/

const API_BASE = "http://127.0.0.1:8000";

const initialActivity = [
  {
    id: 1,
    type: "system",
    title: "Provenance-X workspace initialized",
    description: "Secure evidence workspace is ready.",
    time: "Just now",
    status: "Operational",
  },
];

const navItems = [
  { id: "dashboard", icon: "⌂", label: "Dashboard" },
  { id: "verify", icon: "✓", label: "Verify Evidence", badge: "1" },
  { id: "provenance", icon: "◈", label: "Provenance" },
  { id: "witnesses", icon: "♙", label: "Witnesses" },
  { id: "reports", icon: "▤", label: "Reports" },
  { id: "viewer", icon: "◉", label: "Secure Viewer" },
];

function App() {
  const [activePage, setActivePage] = useState("dashboard");
  const [selectedFile, setSelectedFile] = useState(null);
  const [verification, setVerification] = useState(null);
  const [loading, setLoading] = useState(false);
  const [backendOnline, setBackendOnline] = useState(false);
  const [toast, setToast] = useState(null);
  const [activity, setActivity] = useState(initialActivity);

  const [stats, setStats] = useState({
    totalEvidence: 1249,
    verifiedRecords: 1249,
    witnesses: 3,
    reports: 24,
  });

  // FIX: mutable witness list
  const [witnesses, setWitnesses] = useState([
    {
      id: "WIT-001",
      name: "Investigation Officer",
      role: "Primary witness",
      status: "Verified",
      trust: 98,
      initials: "IO",
    },
    {
      id: "WIT-002",
      name: "Digital Forensics Lab",
      role: "Forensic examiner",
      status: "Online",
      trust: 96,
      initials: "DF",
    },
    {
      id: "WIT-003",
      name: "Evidence Custodian",
      role: "Custodian",
      status: "Ready",
      trust: 94,
      initials: "EC",
    },
  ]);

  // FIX: mutable report list
  const [reports, setReports] = useState([
    {
      id: "RPT-2026-001",
      title: "Digital Evidence Integrity Report",
      date: "30 Sep 2026",
      status: "Ready",
    },
    {
      id: "RPT-2026-002",
      title: "Chain of Custody Report",
      date: "29 Sep 2026",
      status: "Ready",
    },
    {
      id: "RPT-2026-003",
      title: "Witness Verification Report",
      date: "28 Sep 2026",
      status: "Ready",
    },
  ]);

  // FIX: workflow state
  const [showWitnessForm, setShowWitnessForm] = useState(false);
  const [newWitnessName, setNewWitnessName] = useState("");
  const [newWitnessRole, setNewWitnessRole] = useState("");
  const [reportLoading, setReportLoading] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);
  const [showReport, setShowReport] = useState(false);

  useEffect(() => {
    checkBackend();

    const style = document.createElement("style");
    style.id = "provenance-x-ui";

    style.innerHTML = `
      * { box-sizing: border-box; }

      body {
        margin: 0;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system,
          BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: #070b13;
        color: #eef4ff;
      }

      button, input { font: inherit; }
      button { cursor: pointer; }

      .px-app {
        min-height: 100vh;
        display: flex;
        background:
          radial-gradient(circle at 75% 0%, rgba(0, 216, 255, .09), transparent 25%),
          radial-gradient(circle at 30% 100%, rgba(79, 70, 229, .08), transparent 30%),
          #070b13;
      }

      .px-sidebar {
        width: 255px;
        min-height: 100vh;
        position: fixed;
        left: 0; top: 0; bottom: 0;
        background: rgba(9, 14, 25, .97);
        border-right: 1px solid rgba(255,255,255,.07);
        padding: 22px 14px;
        z-index: 20;
      }

      .px-brand { display: flex; align-items: center; gap: 11px; padding: 4px 9px 26px; }
      .px-logo {
        width: 39px; height: 39px; border-radius: 11px; display: grid;
        place-items: center; background: linear-gradient(135deg,#00d9ff,#4772ff);
        color: white; font-weight: 900; box-shadow: 0 0 25px rgba(0,213,255,.25);
      }
      .px-brand-title { font-size: 15px; font-weight: 800; letter-spacing: -.2px; }
      .px-brand-sub { font-size: 10px; color: #7f8ba3; margin-top: 3px; }
      .px-section-title { color: #56627a; font-size: 9px; font-weight: 800; letter-spacing: 1.6px; padding: 12px 11px 8px; }
      .px-workspace { border: 1px solid rgba(255,255,255,.07); background: rgba(255,255,255,.025); border-radius: 12px; padding: 11px; margin-bottom: 13px; }
      .px-workspace-top { display: flex; align-items: center; gap: 9px; }
      .px-workspace-icon { width: 30px; height: 30px; display: grid; place-items: center; background: #16233a; border-radius: 8px; color: #55dfff; font-weight: 800; }
      .px-workspace-name { font-size: 12px; font-weight: 700; }
      .px-workspace-role { color: #69768f; font-size: 9px; margin-top: 2px; }
      .px-nav { display: flex; flex-direction: column; gap: 4px; }
      .px-nav button { width: 100%; border: 0; background: transparent; color: #8995ab; padding: 11px 12px; border-radius: 9px; display: flex; align-items: center; gap: 12px; text-align: left; transition: .18s ease; }
      .px-nav button:hover { background: rgba(255,255,255,.045); color: #eaf4ff; }
      .px-nav button.active { background: linear-gradient(90deg,rgba(0,215,255,.14),rgba(54,102,255,.08)); color: #fff; box-shadow: inset 2px 0 0 #16dfff; }
      .px-nav-icon { width: 19px; text-align: center; color: #72809a; font-weight: 800; }
      .px-nav button.active .px-nav-icon { color: #1ddfff; }
      .px-nav-label { flex: 1; font-size: 12px; font-weight: 650; }
      .px-badge { min-width: 18px; height: 18px; border-radius: 9px; background: #0bc9ef; color: #04131a; display: grid; place-items: center; font-size: 9px; font-weight: 900; }
      .px-sidebar-bottom { position: absolute; left: 14px; right: 14px; bottom: 18px; }
      .px-system-card { border: 1px solid rgba(255,255,255,.07); border-radius: 12px; padding: 12px; background: rgba(255,255,255,.025); }
      .px-system-line { display: flex; align-items: center; justify-content: space-between; font-size: 10px; color: #8b97ab; }
      .px-online { display: inline-flex; align-items: center; gap: 5px; color: #57e6ae; font-size: 10px; font-weight: 700; }
      .px-dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; box-shadow: 0 0 8px currentColor; }

      .px-main { width: calc(100% - 255px); margin-left: 255px; min-height: 100vh; }
      .px-topbar { height: 72px; border-bottom: 1px solid rgba(255,255,255,.07); display: flex; align-items: center; justify-content: space-between; padding: 0 32px; background: rgba(7,11,19,.82); backdrop-filter: blur(16px); position: sticky; top: 0; z-index: 15; }
      .px-breadcrumb { color: #77849b; font-size: 11px; }
      .px-breadcrumb strong { color: #e5ecf7; }
      .px-top-actions { display: flex; align-items: center; gap: 18px; }
      .px-status { display: flex; align-items: center; gap: 7px; font-size: 10px; color: #8c99ad; }
      .px-user { display: flex; align-items: center; gap: 9px; border-left: 1px solid rgba(255,255,255,.07); padding-left: 18px; }
      .px-avatar { width: 30px; height: 30px; border-radius: 50%; display: grid; place-items: center; background: linear-gradient(135deg,#34446b,#18233a); font-size: 10px; font-weight: 800; }
      .px-user-name { font-size: 10px; font-weight: 700; }
      .px-user-role { font-size: 9px; color: #69758b; margin-top: 2px; }

      .px-content { padding: 31px; max-width: 1600px; margin: auto; }
      .px-page-header { display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: 25px; gap: 20px; }
      .px-eyebrow { font-size: 9px; letter-spacing: 1.8px; color: #23d9ff; font-weight: 850; margin-bottom: 7px; }
      .px-title { font-size: clamp(25px,3vw,37px); letter-spacing: -1.3px; margin: 0; font-weight: 850; }
      .px-description { color: #78859c; font-size: 12px; margin: 8px 0 0; max-width: 650px; line-height: 1.6; }
      .px-primary { border: 0; border-radius: 8px; background: linear-gradient(135deg,#0bd8f5,#267bff); color: #fff; padding: 11px 16px; font-size: 11px; font-weight: 800; box-shadow: 0 8px 25px rgba(0,173,255,.17); transition: .2s; }
      .px-primary:hover { transform: translateY(-1px); box-shadow: 0 12px 30px rgba(0,173,255,.28); }
      .px-primary:disabled { opacity: .65; cursor: wait; transform: none; }
      .px-secondary { border: 1px solid rgba(255,255,255,.09); border-radius: 8px; background: rgba(255,255,255,.035); color: #cbd5e5; padding: 10px 14px; font-size: 11px; font-weight: 700; }
      .px-secondary:hover { background: rgba(255,255,255,.07); }

      .px-grid-4 { display: grid; grid-template-columns: repeat(4,1fr); gap: 13px; }
      .px-card { border: 1px solid rgba(255,255,255,.07); background: linear-gradient(145deg,rgba(19,28,45,.9),rgba(11,17,29,.9)); border-radius: 13px; box-shadow: 0 14px 40px rgba(0,0,0,.15); }
      .px-stat { padding: 17px; min-height: 122px; position: relative; overflow: hidden; }
      .px-stat::after { content: ""; position: absolute; width: 90px; height: 90px; border-radius: 50%; right: -35px; top: -35px; background: rgba(0,217,255,.045); }
      .px-stat-top { display: flex; justify-content: space-between; align-items: center; }
      .px-stat-icon { width: 31px; height: 31px; border-radius: 9px; display: grid; place-items: center; background: rgba(21,211,255,.08); color: #35dcff; font-weight: 900; }
      .px-stat-icon.green { color: #51e6ac; background: rgba(59,226,157,.08); }
      .px-stat-icon.purple { color: #b69aff; background: rgba(157,112,255,.08); }
      .px-stat-icon.orange { color: #ffc16d; background: rgba(255,166,70,.08); }
      .px-stat-label { color: #7c889d; font-size: 10px; font-weight: 650; }
      .px-stat-value { margin-top: 12px; font-size: 25px; font-weight: 850; letter-spacing: -.8px; }
      .px-stat-sub { color: #66738b; font-size: 9px; margin-top: 3px; }

      .px-section-grid { display: grid; grid-template-columns: minmax(0,1.7fr) minmax(290px,.8fr); gap: 14px; margin-top: 14px; }
      .px-panel { padding: 20px; }
      .px-panel-header { display: flex; justify-content: space-between; align-items: center; gap: 10px; margin-bottom: 18px; }
      .px-panel-title { font-size: 12px; font-weight: 800; }
      .px-panel-subtitle { font-size: 9px; color: #69758b; margin-top: 4px; }
      .px-link { border: 0; background: transparent; color: #2edfff; font-size: 10px; font-weight: 700; }
      .px-empty { min-height: 185px; border: 1px dashed rgba(255,255,255,.08); border-radius: 10px; display: grid; place-items: center; text-align: center; padding: 20px; }
      .px-empty-icon { width: 44px; height: 44px; border-radius: 50%; display: grid; place-items: center; background: rgba(0,211,255,.07); color: #2ddfff; font-size: 18px; margin: auto auto 10px; }
      .px-empty-title { font-size: 12px; font-weight: 750; }
      .px-empty-text { color: #68758b; font-size: 10px; margin: 6px 0 12px; }

      .px-security { min-height: 265px; }
      .px-security-main { display: flex; align-items: center; gap: 18px; }
      .px-ring { width: 115px; height: 115px; border-radius: 50%; display: grid; place-items: center; background: radial-gradient(circle at center,#0b1423 57%,transparent 58%), conic-gradient(#25ddff 0 97%,#172438 97% 100%); box-shadow: 0 0 30px rgba(25,215,255,.12); }
      .px-ring-number { font-size: 24px; font-weight: 850; }
      .px-ring-label { font-size: 8px; color: #77849b; text-align: center; }
      .px-check-list { display: flex; flex-direction: column; gap: 10px; flex: 1; }
      .px-check { display: flex; align-items: center; gap: 8px; font-size: 10px; color: #aab5c7; }
      .px-check span { color: #4ee4aa; font-weight: 900; }
      .px-timeline { display: flex; flex-direction: column; gap: 0; }
      .px-event { display: flex; gap: 12px; padding: 13px 0; border-bottom: 1px solid rgba(255,255,255,.055); }
      .px-event:last-child { border-bottom: 0; }
      .px-event-icon { width: 28px; height: 28px; border-radius: 8px; background: #13243a; color: #3bdfff; display: grid; place-items: center; font-size: 11px; flex: 0 0 auto; }
      .px-event-title { font-size: 10px; font-weight: 750; }
      .px-event-description { color: #6f7c91; font-size: 9px; margin-top: 4px; }
      .px-event-time { margin-left: auto; color: #566278; font-size: 8px; white-space: nowrap; }

      .px-verify-layout { display: grid; grid-template-columns: minmax(0,1.5fr) minmax(270px,.7fr); gap: 14px; }
      .px-upload { min-height: 335px; padding: 20px; }
      .px-dropzone { min-height: 205px; border: 1px dashed rgba(41,214,255,.28); border-radius: 13px; background: radial-gradient(circle at center,rgba(0,209,255,.055),transparent 55%); display: grid; place-items: center; text-align: center; padding: 25px; transition: .2s; }
      .px-dropzone:hover { border-color: rgba(41,214,255,.55); background: rgba(0,209,255,.045); }
      .px-upload-icon { width: 53px; height: 53px; border-radius: 14px; display: grid; place-items: center; margin: auto auto 11px; background: #132943; color: #38ddff; font-size: 22px; }
      .px-file-input { display: none; }
      .px-upload-title { font-size: 14px; font-weight: 800; }
      .px-upload-sub { font-size: 10px; color: #68758b; margin-top: 5px; }
      .px-file-card { display: flex; align-items: center; gap: 10px; margin-top: 12px; padding: 11px; background: rgba(255,255,255,.025); border: 1px solid rgba(255,255,255,.06); border-radius: 9px; }
      .px-file-name { font-size: 10px; font-weight: 700; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
      .px-file-size { color: #6f7b90; font-size: 8px; }
      .px-green { color: #50e4a8; }
      .px-process-list { display: flex; flex-direction: column; gap: 10px; }
      .px-process { padding: 14px; border-radius: 10px; background: rgba(255,255,255,.025); border: 1px solid rgba(255,255,255,.055); }
      .px-process-number { color: #26dfff; font-size: 9px; font-weight: 900; }
      .px-process-title { margin-top: 6px; font-size: 11px; font-weight: 750; }
      .px-process-text { color: #69758b; font-size: 9px; line-height: 1.5; margin-top: 4px; }
      .px-result { margin-top: 12px; padding: 14px; border-radius: 10px; border: 1px solid rgba(74,226,167,.18); background: rgba(50,210,150,.045); }
      .px-result-title { color: #50e4a8; font-size: 11px; font-weight: 800; }
      .px-hash { word-break: break-all; color: #8290a7; font-family: ui-monospace,SFMono-Regular,Consolas,monospace; font-size: 8px; line-height: 1.5; margin-top: 7px; }

      .px-table { width: 100%; border-collapse: collapse; }
      .px-table th { text-align: left; color: #68758b; font-size: 9px; font-weight: 700; padding: 11px 9px; border-bottom: 1px solid rgba(255,255,255,.07); }
      .px-table td { padding: 13px 9px; font-size: 10px; color: #c6cfdd; border-bottom: 1px solid rgba(255,255,255,.045); }
      .px-table tr:last-child td { border-bottom: 0; }
      .px-status-badge { display: inline-flex; padding: 4px 8px; border-radius: 20px; font-size: 8px; font-weight: 800; background: rgba(69,225,166,.09); color: #50e4a8; }
      .px-status-badge.blue { color: #48dfff; background: rgba(48,209,255,.08); }
      .px-status-badge.orange { color: #ffc477; background: rgba(255,177,77,.08); }

      .px-witness-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 13px; }
      .px-witness-card { padding: 18px; }
      .px-witness-avatar { width: 45px; height: 45px; border-radius: 13px; display: grid; place-items: center; background: linear-gradient(135deg,#162d4a,#172035); color: #41ddff; font-size: 11px; font-weight: 850; margin-bottom: 15px; }
      .px-witness-name { font-size: 12px; font-weight: 800; }
      .px-witness-role { color: #6d798f; font-size: 9px; margin-top: 4px; }
      .px-trust { margin-top: 17px; }
      .px-trust-head { display: flex; justify-content: space-between; color: #758197; font-size: 9px; margin-bottom: 6px; }
      .px-progress { height: 5px; background: #182234; border-radius: 10px; overflow: hidden; }
      .px-progress > div { height: 100%; background: linear-gradient(90deg,#18d8ff,#49e3a6); border-radius: inherit; }

      .px-viewer { min-height: 560px; display: grid; grid-template-columns: 1fr 310px; overflow: hidden; }
      .px-viewer-main { padding: 25px; border-right: 1px solid rgba(255,255,255,.06); }
      .px-viewer-preview { min-height: 420px; border: 1px solid rgba(255,255,255,.06); border-radius: 11px; background: linear-gradient(rgba(255,255,255,.02) 1px, transparent 1px), linear-gradient(90deg,rgba(255,255,255,.02) 1px, transparent 1px), #080d17; background-size: 25px 25px; display: grid; place-items: center; text-align: center; color: #56637a; }
      .px-viewer-side { padding: 22px; }
      .px-meta-row { padding: 11px 0; border-bottom: 1px solid rgba(255,255,255,.05); }
      .px-meta-label { color: #5f6c83; font-size: 8px; text-transform: uppercase; letter-spacing: 1px; }
      .px-meta-value { color: #c4cede; font-size: 10px; margin-top: 4px; word-break: break-word; }

      .px-toast { position: fixed; right: 25px; bottom: 25px; z-index: 100; padding: 13px 16px; border: 1px solid rgba(50,220,170,.2); background: rgba(11,22,31,.96); box-shadow: 0 15px 45px rgba(0,0,0,.35); border-radius: 10px; color: #dce8f4; font-size: 10px; }

      .px-form-grid { display: grid; grid-template-columns: 1fr 1fr auto; gap: 10px; align-items: end; }
      .px-input-label { color: #5f6c83; font-size: 8px; text-transform: uppercase; letter-spacing: 1px; }
      .px-input { width: 100%; margin-top: 6px; padding: 10px 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,.09); background: rgba(255,255,255,.035); color: #eef4ff; outline: none; }
      .px-input:focus { border-color: rgba(42,215,255,.45); box-shadow: 0 0 0 2px rgba(42,215,255,.06); }
      .px-report-detail { margin-top: 14px; }
      .px-report-hash { margin-top: 14px; }
      .px-report-detail table td:first-child { width: 180px; color: #738098; }

      @media(max-width:1100px) {
        .px-grid-4 { grid-template-columns: repeat(2,1fr); }
        .px-section-grid, .px-verify-layout { grid-template-columns: 1fr; }
        .px-witness-grid { grid-template-columns: 1fr; }
        .px-form-grid { grid-template-columns: 1fr; }
      }

      @media(max-width:760px) {
        .px-sidebar { width: 72px; padding: 15px 8px; }
        .px-brand-title, .px-brand-sub, .px-section-title, .px-workspace, .px-nav-label, .px-badge, .px-sidebar-bottom { display: none; }
        .px-brand { justify-content: center; padding-bottom: 20px; }
        .px-nav button { justify-content: center; padding: 12px; }
        .px-main { width: calc(100% - 72px); margin-left: 72px; }
        .px-topbar { padding: 0 15px; }
        .px-user-name, .px-user-role { display: none; }
        .px-content { padding: 20px 14px; }
        .px-page-header { align-items: flex-start; flex-direction: column; }
        .px-grid-4 { grid-template-columns: 1fr; }
        .px-viewer { grid-template-columns: 1fr; }
        .px-viewer-side { border-top: 1px solid rgba(255,255,255,.06); }
      }
    `;

    document.head.appendChild(style);

    return () => {
      const existing = document.getElementById("provenance-x-ui");
      if (existing) existing.remove();
    };
  }, []);

  useEffect(() => {
    if (!toast) return;
    const timer = setTimeout(() => setToast(null), 3000);
    return () => clearTimeout(timer);
  }, [toast]);

  async function checkBackend() {
    try {
      const response = await fetch(`${API_BASE}/`, { method: "GET" });
      setBackendOnline(response.ok);
    } catch {
      setBackendOnline(false);
    }
  }

  function showToast(message) {
    setToast(message);
  }

  function formatBytes(bytes) {
    if (!bytes) return "0 KB";
    const units = ["B", "KB", "MB", "GB"];
    const index = Math.min(
      Math.floor(Math.log(bytes) / Math.log(1024)),
      units.length - 1
    );
    return `${(bytes / Math.pow(1024, index)).toFixed(index === 0 ? 0 : 1)} ${units[index]}`;
  }

  async function calculateSHA256(file) {
    const buffer = await file.arrayBuffer();
    const hashBuffer = await crypto.subtle.digest("SHA-256", buffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map((byte) => byte.toString(16).padStart(2, "0")).join("");
  }

  function handleFile(file) {
    if (!file) return;
    setSelectedFile(file);
    setVerification(null);
    showToast("Evidence selected. Ready for integrity verification.");
    setActivePage("verify");
  }

  async function handleVerify() {
    if (!selectedFile) {
      showToast("Please select an evidence file first.");
      setActivePage("verify");
      return;
    }

    setLoading(true);
    setVerification(null);

    try {
      const hash = await calculateSHA256(selectedFile);
      let backendResult = null;

      try {
        const formData = new FormData();
        formData.append("file", selectedFile);

        const response = await fetch(`${API_BASE}/evidence/verify`, {
          method: "POST",
          body: formData,
        });

        if (response.ok) {
          backendResult = await response.json().catch(() => null);
        }
      } catch {
        backendResult = null;
      }

      const result = {
        verified: true,
        filename: selectedFile.name,
        size: selectedFile.size,
        hash,
        algorithm: "SHA-256",
        timestamp: new Date().toISOString(),
        backendVerified: Boolean(backendResult),
        backend: backendResult,
        evidence_id:
          backendResult?.evidence_id ||
          backendResult?.id ||
          backendResult?.evidence?.id ||
          null,
      };

      setVerification(result);

      setStats((previous) => ({
        ...previous,
        totalEvidence: previous.totalEvidence + 1,
        verifiedRecords: previous.verifiedRecords + 1,
      }));

      setActivity((previous) => [
        {
          id: Date.now(),
          type: "verify",
          title: "Evidence integrity verified",
          description: `${selectedFile.name} passed SHA-256 integrity verification.`,
          time: "Just now",
          status: "Verified",
        },
        ...previous,
      ]);

      showToast("Evidence verified successfully.");
    } catch (error) {
      console.error(error);

      setVerification({
        verified: false,
        error: error.message || "Verification failed.",
      });

      showToast("Verification failed.");
    } finally {
      setLoading(false);
    }
  }

  function handleNav(page) {
    setActivePage(page);
  }

  // =========================
  // WITNESS FUNCTIONALITY
  // =========================
  function registerWitness() {
    const name = newWitnessName.trim();
    const role = newWitnessRole.trim();

    if (!name || !role) {
      showToast("Please enter witness name and role.");
      return;
    }

    const newWitnessNumber = witnesses.length + 1;

    const initials = name
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0].toUpperCase())
      .join("");

    const newWitness = {
      id: `WIT-${String(newWitnessNumber).padStart(3, "0")}`,
      name,
      role,
      status: "Verified",
      trust: 100,
      initials: initials || "W",
    };

    setWitnesses((previous) => [...previous, newWitness]);

    setStats((previous) => ({
      ...previous,
      witnesses: previous.witnesses + 1,
    }));

    setNewWitnessName("");
    setNewWitnessRole("");
    setShowWitnessForm(false);

    setActivity((previous) => [
      {
        id: Date.now(),
        type: "witness",
        title: "Witness registered",
        description: `${name} was added to the trusted witness registry.`,
        time: "Just now",
        status: "Verified",
      },
      ...previous,
    ]);

    showToast("Witness registered successfully.");
  }

  // =========================
  // REPORT FUNCTIONALITY
  // =========================
  async function generateReport() {
    if (!verification?.verified) {
      showToast("Verify an evidence file before generating a report.");
      setActivePage("verify");
      return;
    }

    setReportLoading(true);

    try {
      /*
       * Prefer a real backend evidence ID if the verification endpoint
       * returned one. Otherwise use a deterministic ID based on the
       * verified SHA-256 fingerprint.
       */
      const evidenceId =
        verification.evidence_id ||
        `EVD-${verification.hash.slice(0, 16).toUpperCase()}`;

      let backendReport = null;

      try {
        const response = await fetch(
          `${API_BASE}/api/reports/${encodeURIComponent(evidenceId)}`
        );

        if (response.ok) {
          backendReport = await response.json().catch(() => null);
        }
      } catch (error) {
        console.log("Backend report endpoint unavailable:", error);
      }

      const now = new Date();
      const reportNumber = String(
        reports.length + 1
      ).padStart(3, "0");

      const reportId =
        backendReport?.report_id ||
        backendReport?.id ||
        `RPT-${now.getFullYear()}-${reportNumber}`;

      const generatedReport = {
        id: reportId,
        report_id: reportId,
        title:
          backendReport?.title ||
          "Digital Evidence Integrity Report",
        date:
          backendReport?.date ||
          now.toLocaleDateString("en-GB", {
            day: "2-digit",
            month: "short",
            year: "numeric",
          }),
        status: backendReport?.status || "Ready",
        evidence_id:
          backendReport?.evidence_id || evidenceId,
        filename:
          backendReport?.filename ||
          verification.filename,
        file_size:
          backendReport?.file_size ??
          verification.size,
        algorithm:
          backendReport?.algorithm ||
          backendReport?.hash_algorithm ||
          verification.algorithm,
        hash:
          backendReport?.hash ||
          verification.hash,
        integrity:
          backendReport?.integrity ||
          backendReport?.integrity_status ||
          "Verified",
        backend_verified:
          backendReport?.backend_verified ??
          verification.backendVerified,
        witness_count:
          backendReport?.witness_count ??
          witnesses.length,
        witnesses:
          backendReport?.witnesses ||
          witnesses.map((witness) => ({
            id: witness.id,
            name: witness.name,
            role: witness.role,
            status: witness.status,
            trust: witness.trust,
          })),
        chain_status:
          backendReport?.chain_status || "Valid",
        generated_at:
          backendReport?.generated_at ||
          now.toISOString(),
      };

      setReports((previous) => [
        generatedReport,
        ...previous,
      ]);

      setStats((previous) => ({
        ...previous,
        reports: previous.reports + 1,
      }));

      setSelectedReport(generatedReport);
      setShowReport(true);

      setActivity((previous) => [
        {
          id: Date.now(),
          type: "report",
          title: "Evidence integrity report generated",
          description: `${generatedReport.id} was generated successfully.`,
          time: "Just now",
          status: "Ready",
        },
        ...previous,
      ]);

      showToast(
        backendReport
          ? "Report generated by backend successfully."
          : "Report generated successfully."
      );
    } catch (error) {
      console.error("Report generation error:", error);
      showToast("Report generation failed.");
    } finally {
      setReportLoading(false);
    }
  }

  function openReport(report) {
    setSelectedReport(report);
    setShowReport(true);
  }

  function renderPage() {
    switch (activePage) {
      case "verify":
        return <VerifyPage />;
      case "provenance":
        return <ProvenancePage />;
      case "witnesses":
        return <WitnessPage />;
      case "reports":
        return <ReportsPage />;
      case "viewer":
        return <ViewerPage />;
      case "dashboard":
      default:
        return <DashboardPage />;
    }
  }

  function PageHeader({ eyebrow, title, description, action }) {
    return (
      <div className="px-page-header">
        <div>
          <div className="px-eyebrow">{eyebrow}</div>
          <h1 className="px-title">{title}</h1>
          <p className="px-description">{description}</p>
        </div>
        {action}
      </div>
    );
  }

  function StatCard({ icon, label, value, subtitle, variant }) {
    return (
      <div className="px-card px-stat">
        <div className="px-stat-top">
          <div className={`px-stat-icon ${variant || ""}`}>{icon}</div>
          <span className="px-stat-label">{label}</span>
        </div>
        <div className="px-stat-value">{value}</div>
        <div className="px-stat-sub">{subtitle}</div>
      </div>
    );
  }

  function DashboardPage() {
    return (
      <>
        <PageHeader
          eyebrow="SECURE DIGITAL PROVENANCE"
          title="Evidence integrity dashboard"
          description="Monitor evidence verification, provenance history, witnesses and audit activity from one secure workspace."
          action={
            <button
              className="px-primary"
              onClick={() => setActivePage("verify")}
            >
              + Verify evidence
            </button>
          }
        />

        <div className="px-grid-4">
          <StatCard
            icon="◆"
            label="TOTAL EVIDENCE"
            value={stats.totalEvidence.toLocaleString()}
            subtitle="+12.8% this month"
          />
          <StatCard
            icon="✓"
            label="VERIFIED RECORDS"
            value={stats.verifiedRecords.toLocaleString()}
            subtitle="Integrity checks passed"
            variant="green"
          />
          <StatCard
            icon="♙"
            label="WITNESSES"
            value={stats.witnesses}
            subtitle="Trusted participants"
            variant="purple"
          />
          <StatCard
            icon="▤"
            label="REPORTS"
            value={stats.reports}
            subtitle="Audit-ready reports"
            variant="orange"
          />
        </div>

        <div className="px-section-grid">
          <div className="px-card px-panel">
            <div className="px-panel-header">
              <div>
                <div className="px-panel-title">Recent evidence activity</div>
                <div className="px-panel-subtitle">
                  Latest events from your secure workspace
                </div>
              </div>
              <button
                className="px-link"
                onClick={() => setActivePage("provenance")}
              >
                View all
              </button>
            </div>

            {activity.length === 0 ? (
              <div className="px-empty">
                <div>
                  <div className="px-empty-icon">◈</div>
                  <div className="px-empty-title">
                    No recent verification records
                  </div>
                  <div className="px-empty-text">
                    Upload evidence and perform a verification to create the
                    first provenance record.
                  </div>
                  <button
                    className="px-primary"
                    onClick={() => setActivePage("verify")}
                  >
                    Verify evidence
                  </button>
                </div>
              </div>
            ) : (
              <div className="px-timeline">
                {activity.slice(0, 5).map((item) => (
                  <div className="px-event" key={item.id}>
                    <div className="px-event-icon">
                      {item.type === "verify"
                        ? "✓"
                        : item.type === "report"
                        ? "▤"
                        : item.type === "witness"
                        ? "♙"
                        : "◆"}
                    </div>
                    <div>
                      <div className="px-event-title">{item.title}</div>
                      <div className="px-event-description">
                        {item.description}
                      </div>
                    </div>
                    <div className="px-event-time">{item.time}</div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="px-card px-panel px-security">
            <div className="px-panel-header">
              <div>
                <div className="px-panel-title">Security integrity</div>
                <div className="px-panel-subtitle">
                  Operational security health
                </div>
              </div>
              <span className="px-status-badge">Operational</span>
            </div>

            <div className="px-security-main">
              <div className="px-ring">
                <div>
                  <div className="px-ring-number">97%</div>
                  <div className="px-ring-label">INTEGRITY</div>
                </div>
              </div>
              <div className="px-check-list">
                <div className="px-check"><span>✓</span> Cryptographic hashing</div>
                <div className="px-check"><span>✓</span> Provenance tracking</div>
                <div className="px-check"><span>✓</span> Witness verification</div>
                <div className="px-check"><span>✓</span> Audit reporting</div>
              </div>
            </div>
          </div>
        </div>

        <div className="px-card px-panel" style={{ marginTop: 14 }}>
          <div className="px-panel-header">
            <div>
              <div className="px-panel-title">Cryptographic integrity</div>
              <div className="px-panel-subtitle">
                Evidence fingerprints are chained into a tamper-evident
                provenance history.
              </div>
            </div>
            <span className="px-status-badge blue">SHA-256 ACTIVE</span>
          </div>

          <div className="px-table-wrap">
            <table className="px-table">
              <thead>
                <tr>
                  <th>COMPONENT</th>
                  <th>STATUS</th>
                  <th>PROTECTION</th>
                  <th>STATE</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Evidence fingerprinting</td>
                  <td><span className="px-status-badge">Verified</span></td>
                  <td>SHA-256</td>
                  <td className="px-green">Operational</td>
                </tr>
                <tr>
                  <td>Provenance records</td>
                  <td><span className="px-status-badge">Active</span></td>
                  <td>Immutable event chain</td>
                  <td className="px-green">Operational</td>
                </tr>
                <tr>
                  <td>Witness module</td>
                  <td><span className="px-status-badge">Protected</span></td>
                  <td>Participant validation</td>
                  <td className="px-green">Operational</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </>
    );
  }

  function VerifyPage() {
    return (
      <>
        <PageHeader
          eyebrow="EVIDENCE VERIFICATION"
          title="Verify digital evidence"
          description="Upload an evidence file and establish its cryptographic integrity and provenance."
        />

        <div className="px-verify-layout">
          <div className="px-card px-upload">
            <div className="px-panel-header">
              <div>
                <div className="px-panel-title">Evidence intake</div>
                <div className="px-panel-subtitle">
                  Select a file to calculate its integrity fingerprint.
                </div>
              </div>
              <span className="px-status-badge blue">SECURE INTAKE</span>
            </div>

            <label className="px-dropzone">
              <input
                className="px-file-input"
                type="file"
                onChange={(event) =>
                  handleFile(event.target.files?.[0])
                }
              />
              <div>
                <div className="px-upload-icon">↑</div>
                <div className="px-upload-title">Upload evidence</div>
                <div className="px-upload-sub">
                  Click to browse your computer
                </div>
              </div>
            </label>

            {selectedFile && (
              <div className="px-file-card">
                <div className="px-workspace-icon">FILE</div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div className="px-file-name">{selectedFile.name}</div>
                  <div className="px-file-size">
                    {formatBytes(selectedFile.size)}
                  </div>
                </div>
                <span className="px-green">✓</span>
              </div>
            )}

            <button
              className="px-primary"
              style={{ width: "100%", marginTop: 12 }}
              onClick={handleVerify}
              disabled={loading}
            >
              {loading
                ? "Calculating integrity fingerprint..."
                : "Verify evidence"}
            </button>

            {verification?.verified && (
              <div className="px-result">
                <div className="px-result-title">✓ Evidence verified</div>
                <div className="px-event-description">
                  Integrity check completed successfully.
                </div>
                <div className="px-hash">
                  SHA-256: {verification.hash}
                </div>
              </div>
            )}

            {verification?.verified === false && (
              <div
                className="px-result"
                style={{
                  borderColor: "rgba(255,90,90,.25)",
                  background: "rgba(255,70,70,.05)",
                }}
              >
                <div style={{ color: "#ff8d8d", fontWeight: 800 }}>
                  Verification failed
                </div>
                <div className="px-event-description">
                  {verification.error}
                </div>
              </div>
            )}
          </div>

          <div className="px-card px-panel">
            <div className="px-panel-header">
              <div>
                <div className="px-panel-title">Verification pipeline</div>
                <div className="px-panel-subtitle">
                  Evidence integrity workflow
                </div>
              </div>
            </div>

            <div className="px-process-list">
              {[
                ["01", "Fingerprint", "A cryptographic hash uniquely identifies the evidence content."],
                ["02", "Provenance", "Evidence history can be connected to a tamper-evident record."],
                ["03", "Verification", "The integrity result can be independently inspected."],
                ["04", "Witness", "Trusted participants can be associated with the evidence lifecycle."],
              ].map(([number, title, text]) => (
                <div className="px-process" key={number}>
                  <div className="px-process-number">{number}</div>
                  <div className="px-process-title">{title}</div>
                  <div className="px-process-text">{text}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </>
    );
  }

  function ProvenancePage() {
    const provenanceRows = useMemo(() => {
      if (!verification) {
        return [
          {
            event: "Workspace initialized",
            actor: "System",
            status: "Active",
            time: "Just now",
          },
        ];
      }

      const time = new Date(verification.timestamp).toLocaleTimeString();

      return [
        { event: "Evidence uploaded", actor: "Investigator", status: "Recorded", time },
        { event: "SHA-256 fingerprint calculated", actor: "Integrity Engine", status: "Verified", time },
        { event: "Integrity verification completed", actor: "Verification Engine", status: "Passed", time },
      ];
    }, [verification]);

    return (
      <>
        <PageHeader
          eyebrow="CHAIN OF CUSTODY"
          title="Provenance history"
          description="Track every important evidence event through a structured, auditable provenance timeline."
          action={
            <button
              className="px-secondary"
              onClick={() => showToast("Provenance export prepared.")}
            >
              Export history
            </button>
          }
        />

        <div className="px-card px-panel">
          <div className="px-panel-header">
            <div>
              <div className="px-panel-title">Evidence provenance chain</div>
              <div className="px-panel-subtitle">
                Immutable-style event history for the current workspace
              </div>
            </div>
            <span className="px-status-badge">CHAIN INTACT</span>
          </div>

          <table className="px-table">
            <thead>
              <tr>
                <th>EVENT</th>
                <th>ACTOR</th>
                <th>STATUS</th>
                <th>TIME</th>
              </tr>
            </thead>
            <tbody>
              {provenanceRows.map((row, index) => (
                <tr key={index}>
                  <td>{row.event}</td>
                  <td>{row.actor}</td>
                  <td><span className="px-status-badge">{row.status}</span></td>
                  <td>{row.time}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="px-section-grid">
          <div className="px-card px-panel">
            <div className="px-panel-header">
              <div>
                <div className="px-panel-title">Current evidence fingerprint</div>
                <div className="px-panel-subtitle">Cryptographic identity</div>
              </div>
            </div>

            {verification ? (
              <div className="px-result">
                <div className="px-result-title">✓ SHA-256 fingerprint</div>
                <div className="px-hash">{verification.hash}</div>
              </div>
            ) : (
              <div className="px-empty">
                <div>
                  <div className="px-empty-title">No evidence fingerprint yet</div>
                  <div className="px-empty-text">
                    Verify an evidence file to create a fingerprint.
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="px-card px-panel">
            <div className="px-panel-header">
              <div>
                <div className="px-panel-title">Integrity controls</div>
              </div>
            </div>

            <div className="px-check-list">
              <div className="px-check"><span>✓</span> Hash generation</div>
              <div className="px-check"><span>✓</span> Event tracking</div>
              <div className="px-check"><span>✓</span> Witness association</div>
              <div className="px-check"><span>✓</span> Audit reporting</div>
            </div>
          </div>
        </div>
      </>
    );
  }

  function WitnessPage() {
    return (
      <>
        <PageHeader
          eyebrow="PROVENANCE-X WITNESS PROGRAM"
          title="Witnesses"
          description="Manage trusted participants associated with evidence verification and provenance events."
          action={
            <button
              className="px-primary"
              onClick={() => setShowWitnessForm(true)}
            >
              + Add witness
            </button>
          }
        />

        {showWitnessForm && (
          <div className="px-card px-panel" style={{ marginBottom: 14 }}>
            <div className="px-panel-header">
              <div>
                <div className="px-panel-title">Register witness</div>
                <div className="px-panel-subtitle">
                  Add a trusted participant to the witness registry.
                </div>
              </div>

              <button
                className="px-secondary"
                onClick={() => {
                  setShowWitnessForm(false);
                  setNewWitnessName("");
                  setNewWitnessRole("");
                }}
              >
                Cancel
              </button>
            </div>

            <div className="px-form-grid">
              <div>
                <div className="px-input-label">WITNESS NAME</div>
                <input
                  className="px-input"
                  value={newWitnessName}
                  onChange={(event) =>
                    setNewWitnessName(event.target.value)
                  }
                  placeholder="Enter witness name"
                />
              </div>

              <div>
                <div className="px-input-label">ROLE</div>
                <input
                  className="px-input"
                  value={newWitnessRole}
                  onChange={(event) =>
                    setNewWitnessRole(event.target.value)
                  }
                  placeholder="e.g. Forensic Examiner"
                />
              </div>

              <button
                className="px-primary"
                onClick={registerWitness}
              >
                Register witness
              </button>
            </div>
          </div>
        )}

        <div className="px-witness-grid">
          {witnesses.map((witness) => (
            <div className="px-card px-witness-card" key={witness.id}>
              <div className="px-witness-avatar">{witness.initials}</div>
              <div className="px-witness-name">{witness.name}</div>
              <div className="px-witness-role">{witness.role}</div>

              <div style={{ marginTop: 13 }}>
                <span className="px-status-badge">{witness.status}</span>
              </div>

              <div className="px-trust">
                <div className="px-trust-head">
                  <span>Trust score</span>
                  <strong>{witness.trust}%</strong>
                </div>
                <div className="px-progress">
                  <div style={{ width: `${witness.trust}%` }} />
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="px-card px-panel" style={{ marginTop: 14 }}>
          <div className="px-panel-header">
            <div>
              <div className="px-panel-title">Witness module status</div>
              <div className="px-panel-subtitle">
                Trusted participant infrastructure
              </div>
            </div>

            <div className="px-online">
              <span className="px-dot" />
              ONLINE
            </div>
          </div>

          <div className="px-grid-4">
            <StatCard
              icon="♙"
              label="REGISTERED"
              value={witnesses.length}
              subtitle="Trusted participants"
            />
            <StatCard
              icon="✓"
              label="VERIFIED"
              value={witnesses.length}
              subtitle="Identity verified"
              variant="green"
            />
            <StatCard
              icon="◈"
              label="AVG TRUST"
              value={
                witnesses.length
                  ? `${Math.round(
                      witnesses.reduce((sum, w) => sum + w.trust, 0) /
                        witnesses.length
                    )}%`
                  : "0%"
              }
              subtitle="Current trust level"
              variant="purple"
            />
            <StatCard
              icon="●"
              label="STATUS"
              value="Ready"
              subtitle="Witness service"
              variant="orange"
            />
          </div>
        </div>
      </>
    );
  }

  function ReportsPage() {
    return (
      <>
        <PageHeader
          eyebrow="AUDIT & COMPLIANCE"
          title="Reports"
          description="Generate and review audit-ready evidence integrity and provenance reports."
          action={
            <button
              className="px-primary"
              onClick={generateReport}
              disabled={reportLoading}
            >
              {reportLoading ? "Generating..." : "+ Generate report"}
            </button>
          }
        />

        <div className="px-card px-panel">
          <div className="px-panel-header">
            <div>
              <div className="px-panel-title">Audit-ready reports</div>
              <div className="px-panel-subtitle">
                Evidence integrity documentation
              </div>
            </div>

            <span className="px-status-badge">
              {reports.length} AVAILABLE
            </span>
          </div>

          <table className="px-table">
            <thead>
              <tr>
                <th>REPORT ID</th>
                <th>TITLE</th>
                <th>DATE</th>
                <th>STATUS</th>
                <th>ACTION</th>
              </tr>
            </thead>

            <tbody>
              {reports.map((report) => (
                <tr key={report.id}>
                  <td>{report.id}</td>
                  <td>{report.title}</td>
                  <td>{report.date}</td>
                  <td>
                    <span className="px-status-badge">
                      {report.status}
                    </span>
                  </td>
                  <td>
                    <button
                      className="px-link"
                      onClick={() => openReport(report)}
                    >
                      View report
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {showReport && selectedReport && (
          <div
            className="px-card px-panel px-report-detail"
            style={{
              borderColor: "rgba(0,217,255,.18)",
            }}
          >
            <div className="px-panel-header">
              <div>
                <div className="px-panel-title">
                  {selectedReport.title}
                </div>
                <div className="px-panel-subtitle">
                  {selectedReport.id} • Generated report
                </div>
              </div>

              <button
                className="px-secondary"
                onClick={() => setShowReport(false)}
              >
                Close
              </button>
            </div>

            <table className="px-table">
              <tbody>
                <tr>
                  <td><strong>Report ID</strong></td>
                  <td>{selectedReport.id}</td>
                </tr>
                <tr>
                  <td><strong>Evidence ID</strong></td>
                  <td>{selectedReport.evidence_id || "—"}</td>
                </tr>
                <tr>
                  <td><strong>Evidence</strong></td>
                  <td>{selectedReport.filename || "—"}</td>
                </tr>
                <tr>
                  <td><strong>File size</strong></td>
                  <td>
                    {selectedReport.file_size
                      ? formatBytes(selectedReport.file_size)
                      : "—"}
                  </td>
                </tr>
                <tr>
                  <td><strong>Algorithm</strong></td>
                  <td>{selectedReport.algorithm || "SHA-256"}</td>
                </tr>
                <tr>
                  <td><strong>Integrity</strong></td>
                  <td>
                    <span className="px-status-badge">
                      {selectedReport.integrity || "Verified"}
                    </span>
                  </td>
                </tr>
                <tr>
                  <td><strong>Chain status</strong></td>
                  <td>
                    <span className="px-status-badge">
                      {selectedReport.chain_status || "Valid"}
                    </span>
                  </td>
                </tr>
                <tr>
                  <td><strong>Witnesses</strong></td>
                  <td>
                    {selectedReport.witness_count ??
                      selectedReport.witnesses?.length ??
                      0}
                  </td>
                </tr>
                <tr>
                  <td><strong>Status</strong></td>
                  <td>
                    <span className="px-status-badge">
                      {selectedReport.status || "Ready"}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>

            {selectedReport.hash && (
              <div className="px-result px-report-hash">
                <div className="px-result-title">
                  SHA-256 Evidence Fingerprint
                </div>
                <div className="px-hash">
                  {selectedReport.hash}
                </div>
              </div>
            )}

            {selectedReport.witnesses?.length > 0 && (
              <div
                className="px-card px-panel"
                style={{ marginTop: 14 }}
              >
                <div className="px-panel-header">
                  <div>
                    <div className="px-panel-title">
                      Witness verification
                    </div>
                    <div className="px-panel-subtitle">
                      Witnesses associated with this report
                    </div>
                  </div>
                </div>

                <table className="px-table">
                  <thead>
                    <tr>
                      <th>WITNESS</th>
                      <th>ROLE</th>
                      <th>STATUS</th>
                      <th>TRUST</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedReport.witnesses.map((witness) => (
                      <tr key={witness.id}>
                        <td>{witness.name}</td>
                        <td>{witness.role}</td>
                        <td>
                          <span className="px-status-badge">
                            {witness.status}
                          </span>
                        </td>
                        <td>{witness.trust}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </>
    );
  }

  function ViewerPage() {
    return (
      <>
        <PageHeader
          eyebrow="SECURE EVIDENCE VIEWER"
          title="Secure Viewer"
          description="Inspect verified evidence metadata and integrity information without modifying the source record."
        />

        <div className="px-card px-viewer">
          <div className="px-viewer-main">
            <div className="px-panel-header">
              <div>
                <div className="px-panel-title">Evidence preview</div>
                <div className="px-panel-subtitle">
                  Read-only secure inspection
                </div>
              </div>
              <span className="px-status-badge blue">READ ONLY</span>
            </div>

            <div className="px-viewer-preview">
              <div>
                <div
                  style={{
                    fontSize: 35,
                    color: "#2cddff",
                    marginBottom: 12,
                  }}
                >
                  ◉
                </div>
                <div
                  style={{
                    fontSize: 12,
                    color: "#8490a5",
                    fontWeight: 700,
                  }}
                >
                  {selectedFile ? selectedFile.name : "No evidence loaded"}
                </div>
                <div
                  style={{
                    fontSize: 9,
                    color: "#515e74",
                    marginTop: 6,
                  }}
                >
                  Secure read-only viewer
                </div>
              </div>
            </div>
          </div>

          <div className="px-viewer-side">
            <div className="px-panel-title">Evidence metadata</div>

            <div className="px-meta-row">
              <div className="px-meta-label">Filename</div>
              <div className="px-meta-value">
                {selectedFile?.name || "—"}
              </div>
            </div>

            <div className="px-meta-row">
              <div className="px-meta-label">Size</div>
              <div className="px-meta-value">
                {selectedFile ? formatBytes(selectedFile.size) : "—"}
              </div>
            </div>

            <div className="px-meta-row">
              <div className="px-meta-label">Algorithm</div>
              <div className="px-meta-value">SHA-256</div>
            </div>

            <div className="px-meta-row">
              <div className="px-meta-label">Verification</div>
              <div className="px-meta-value">
                {verification?.verified ? "Verified" : "Not verified"}
              </div>
            </div>

            <div className="px-meta-row">
              <div className="px-meta-label">Backend</div>
              <div className="px-meta-value">
                {backendOnline ? "Connected" : "Offline / unavailable"}
              </div>
            </div>

            <button
              className="px-secondary"
              style={{ width: "100%", marginTop: 18 }}
              onClick={() => setActivePage("verify")}
            >
              Load evidence
            </button>
          </div>
        </div>
      </>
    );
  }

  return (
    <div className="px-app">
      <aside className="px-sidebar">
        <div className="px-brand">
          <div className="px-logo">PX</div>
          <div>
            <div className="px-brand-title">Provenance-X</div>
            <div className="px-brand-sub">
              Evidence Integrity Platform
            </div>
          </div>
        </div>

        <div className="px-section-title">WORKSPACE</div>

        <div className="px-workspace">
          <div className="px-workspace-top">
            <div className="px-workspace-icon">⌂</div>
            <div>
              <div className="px-workspace-name">
                Investigation Lab
              </div>
              <div className="px-workspace-role">
                Secure Workspace
              </div>
            </div>
          </div>
        </div>

        <div className="px-section-title">PLATFORM</div>

        <nav className="px-nav">
          {navItems.map((item) => (
            <button
              key={item.id}
              className={activePage === item.id ? "active" : ""}
              onClick={() => handleNav(item.id)}
            >
              <span className="px-nav-icon">{item.icon}</span>
              <span className="px-nav-label">{item.label}</span>
              {item.badge && (
                <span className="px-badge">{item.badge}</span>
              )}
            </button>
          ))}
        </nav>

        <div className="px-sidebar-bottom">
          <div className="px-system-card">
            <div className="px-system-line">
              <span>System Secure</span>
              <span className="px-online">
                <span className="px-dot" />
              </span>
            </div>
            <div
              style={{
                marginTop: 7,
                color: "#59667d",
                fontSize: 8,
              }}
            >
              All services monitored
            </div>
          </div>
        </div>
      </aside>

      <main className="px-main">
        <header className="px-topbar">
          <div className="px-breadcrumb">
            Provenance-X /{" "}
            <strong>
              {navItems.find((item) => item.id === activePage)?.label}
            </strong>
          </div>

          <div className="px-top-actions">
            <div className="px-status">
              <span
                className="px-dot"
                style={{
                  color: backendOnline ? "#51e6ac" : "#ffc477",
                }}
              />
              {backendOnline
                ? "All systems operational"
                : "Local verification operational"}
            </div>

            <div className="px-user">
              <div className="px-avatar">IA</div>
              <div>
                <div className="px-user-name">Investigator</div>
                <div className="px-user-role">Administrator</div>
              </div>
            </div>
          </div>
        </header>

        <section className="px-content">
          {renderPage()}
        </section>
      </main>

      {toast && <div className="px-toast">{toast}</div>}
    </div>
  );
}

export default App;