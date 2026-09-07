/**
 * Thin fetch wrapper for the backend API.
 *
 * Centralizing requests here (rather than scattering fetch() calls
 * through components) means swapping in auth headers, a different
 * base URL, or React Query later touches one file, not every screen.
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

async function handle(response) {
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch {
      // ignore JSON parse failures, fall back to statusText
    }
    throw new Error(detail);
  }
  return response.json();
}

export async function uploadCsv(file) {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(`${BASE_URL}/api/upload`, {
    method: "POST",
    body: formData,
  });
  return handle(response);
}

export async function fetchLeads(params = {}) {
  const query = new URLSearchParams(
    Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== "")
  );
  const response = await fetch(`${BASE_URL}/api/leads?${query.toString()}`);
  return handle(response);
}

export async function fetchBatches() {
  const response = await fetch(`${BASE_URL}/api/batches`);
  return handle(response);
}

export function exportCsvUrl(params = {}) {
  const query = new URLSearchParams(
    Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== "")
  );
  return `${BASE_URL}/api/leads-export/csv?${query.toString()}`;
}
