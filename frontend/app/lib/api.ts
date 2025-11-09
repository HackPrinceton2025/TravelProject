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

export type GroupMemberRecord = {
  group_id: string;
  user_id: string;
  user_name?: string;
  user_email?: string;
  joined_at?: string;
};

export type ExpenseParticipant = {
  user_id: string;
  share?: number;
};

export type ExpensePayload = {
  group_id: string;
  payer_id: string;
  amount: number;
  description?: string;
  split_between: ExpenseParticipant[];
};

export type ExpenseResponse = {
  message: string;
  expense_id: string;
};

export type PreferenceStatus = {
  has_interests: boolean;
  has_budget: boolean;
  has_departure_city: boolean;
  interests: string[];
  budget_max?: number | null;
  departure_city?: string | null;
};

export type PreferenceUpdatePayload = {
  group_id: string;
  user_id: string;
  interests?: string[];
  budget_max?: number;
  departure_city?: string;
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

export async function getGroupMembers(groupId: string) {
  const r = await fetch(`${API_BASE}/api/group_members/${groupId}`, {
    cache: "no-store",
  });
  return handleResponse<GroupMemberRecord[]>(r);
}

export async function createExpense(payload: ExpensePayload) {
  const r = await fetch(`${API_BASE}/api/expenses`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse<ExpenseResponse>(r);
}

export async function getGroupBalances(groupId: string) {
  const r = await fetch(`${API_BASE}/api/expenses/group/${groupId}/balances`, {
    cache: "no-store",
  });
  return handleResponse<{
    group_id: string;
    balances: Record<string, number>;
    settlements: { from: string; to: string; amount: string }[];
  }>(r);
}

export async function getPreferenceStatus(groupId: string, userId: string) {
  const params = new URLSearchParams({ group_id: groupId, user_id: userId });
  const r = await fetch(`${API_BASE}/api/preferences/status?${params.toString()}`, {
    cache: "no-store",
  });
  return handleResponse<PreferenceStatus>(r);
}

export async function updatePreferences(payload: PreferenceUpdatePayload) {
  const r = await fetch(`${API_BASE}/api/preferences/update`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse<{ success: boolean; updated_preferences: Record<string, unknown> }>(r);
}
