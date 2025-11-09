import { API_BASE } from "./api";

export type ChatMessage = {
  id: string;
  group_id: string;
  sender_id: string;
  kind: string | null;
  body: { [key: string]: any } | null;
  created_at: string;
};

type MessageInsert = {
  groupId: string;
  senderId: string;
  content: string;
};

export type AgentResponse = {
  message: string;
  cards?: any[];
  interactive_elements?: any[];
};

export async function fetchGroupMessages(groupId: string) {
  const res = await fetch(`${API_BASE}/api/messages?group_id=${groupId}`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Failed to load messages (${res.status})`);
  }
  const data = await res.json();
  return (data || []) as ChatMessage[];
}

export async function sendGroupMessage({
  groupId,
  senderId,
  content,
}: MessageInsert) {
  const res = await fetch(`${API_BASE}/api/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      group_id: groupId,
      sender_id: senderId,
      kind: "text",
      body: { text: content },
    }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Failed to send message");
  }
  return (await res.json()) as ChatMessage;
}

export async function callAIAgent({
  message,
  userId,
  groupId,
  //chatHistory,
}: {
  message: string;
  userId: string;
  groupId: string;
  //chatHistory?: Array<{ role: string; content: string }>;
}): Promise<AgentResponse> {
  const res = await fetch(`${API_BASE}/api/agent/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      user_id: userId,
      group_id: groupId,
      // chat_history: chatHistory,
      stream: false,
    }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Failed to call AI agent");
  }

  return (await res.json()) as AgentResponse;
}
