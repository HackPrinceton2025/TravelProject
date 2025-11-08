const API_BASE = process.env.NEXT_PUBLIC_BACKEND_API_URL || process.env.BACKEND_API_URL || "http://localhost:8000";

export async function getGroups() {
  const r = await fetch(`${API_BASE}/api/groups`, { cache: "no-store" });
  return r.json();
}

export async function createGroup(name: string) {
  const r = await fetch(`${API_BASE}/api/groups`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  return r.json();
}


