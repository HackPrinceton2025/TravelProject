export const API_BASE =
  process.env.NEXT_PUBLIC_BACKEND_API_URL ||
  process.env.BACKEND_API_URL ||
  "http://localhost:8000";

type FetchError = { detail?: string };

export type GroupRecord = {
  id: string;
  name: string;
  invite_code: string;
  created_at?: string;
};

const handleResponse = async <T>(res: Response): Promise<T> => {
  if (res.ok) {
    return (await res.json()) as T;
  }
  let detail: string | undefined;
  try {
    const data = (await res.json()) as FetchError;
    detail = data.detail;
  } catch {
    detail = await res.text();
  }
  throw new Error(detail || "Request failed");
};

export async function getGroups() {
  const r = await fetch(`${API_BASE}/api/groups`, { cache: "no-store" });
  return handleResponse<GroupRecord[]>(r);
}

export async function createGroup(name: string, createdBy?: string) {
  const payload: Record<string, string> = { name };
  if (createdBy) payload.created_by = createdBy;
  const r = await fetch(`${API_BASE}/api/groups`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse<GroupRecord>(r);
}

export type JoinGroupResponse = {
  message: string;
  group_id: string;
};

export async function joinGroupByCode(inviteCode: string, userId: string) {
  const params = new URLSearchParams({
    invite_code: inviteCode,
    user_id: userId,
  });
  const r = await fetch(`${API_BASE}/api/group_members/join?${params.toString()}`, {
    method: "POST",
  });
  return handleResponse<JoinGroupResponse>(r);
}
