
const API_URL = "http://127.0.0.1:8000";

async function request(endpoint, options = {}) {
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      ...(options.body instanceof FormData
        ? {}
        : { "Content-Type": "application/json" }),
      ...(options.headers || {}),
    },
  });

  const text = await response.text();

  let data;

  try {
    data = text ? JSON.parse(text) : {};
  } catch {
    data = { message: text };
  }

  if (!response.ok) {
    throw new Error(
      data.detail || data.message || `API error: ${response.status}`
    );
  }

  return data;
}

export const api = {

  // System
  health: () =>
    request("/api/health"),

  // Upload evidence
  uploadEvidence: (file) => {
    const formData = new FormData();
    formData.append("file", file);

    return request("/api/evidence/upload", {
      method: "POST",
      body: formData,
    });
  },

  // Verify evidence
  verifyEvidence: (evidenceId) =>
    request(`/api/evidence/${evidenceId}/verify`, {
      method: "POST",
    }),

  // Provenance
  getProvenance: (evidenceId) =>
    request(`/api/provenance/${evidenceId}`),

  getAllProvenance: () =>
    request("/api/provenance"),

  // Witnesses
  getWitnesses: (evidenceId) =>
    request(`/api/witnesses/${evidenceId}`),

  // Reports
  getReportSummary: () =>
    request("/api/reports/summary"),

  // Statistics
  getStatistics: () =>
    request("/api/statistics"),

  // Merkle verification
  verifyMerkle: (evidenceId) =>
    request(`/api/merkle/verify/${evidenceId}`),
};

export default api;