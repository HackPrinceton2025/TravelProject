import { getAccessToken } from "./auth";

const API_BASE = process.env.NEXT_PUBLIC_BACKEND_API_URL || process.env.BACKEND_API_URL || "http://localhost:8000";

// Helper to get headers with auth token
async function getAuthHeaders() {
  const token = await getAccessToken();
  return {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` }),
  };
}

export async function getGroups() {
  const headers = await getAuthHeaders();
  const r = await fetch(`${API_BASE}/api/groups`, {
    cache: "no-store",
    headers,
  });
  return r.json();
}

export async function createGroup(name: string) {
  const headers = await getAuthHeaders();
  const r = await fetch(`${API_BASE}/api/groups`, {
    method: "POST",
    headers,
    body: JSON.stringify({ name }),
  });
  return r.json();
}


