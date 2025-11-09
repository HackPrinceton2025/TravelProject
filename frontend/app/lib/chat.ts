import { API_BASE } from "./api";

export type ChatMessage = {
  id: string;
  group_id: string;
  sender_id: string;
  kind: string | null;
  content: string | null; // New: plain text content
  body: { [key: string]: any } | null; // JSONB for cards
  created_at: string;
};

type MessageInsert = {
  groupId: string;
  senderId: string;
  content: string;
  senderName?: string | null;
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
  senderName,
}: MessageInsert) {
  const payload = {
    group_id: groupId,
    sender_id: senderId,
    kind: "text",
    content,
    body: {
      text: content,
      sender_name: senderName ?? "",
    },
  };
  
  const res = await fetch(`${API_BASE}/api/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Failed to send message");
  }
  const response = await res.json();
  return response as ChatMessage;
}

export async function sendAIMessage({
  groupId,
  senderId,
  content,
  body,
}: {
  groupId: string;
  senderId: string;
  content: string; // Plain text message
  body: { [key: string]: any } | null; // Cards data
}) {
  const payload = {
    group_id: groupId,
    sender_id: senderId,
    kind: "ai-response",
    content: content, // Text in content field
    body: body, // Cards in body field
  };

  console.log("🚀 sendAIMessage payload:");
  console.log("  📄 content length:", content.length, "characters");
  console.log("  🎴 body (cards):", body);
  console.log("  🎴 body type:", Array.isArray(body) ? "array" : typeof body);
  if (body) {
    const bodyString = JSON.stringify(body);
    console.log("  🎴 body JSON length:", bodyString.length, "characters");
    console.log("  🎴 cards count:", Array.isArray(body) ? body.length : "N/A");
  }
  console.log("  📦 total payload size:", JSON.stringify(payload).length, "characters");

  const res = await fetch(`${API_BASE}/api/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      group_id: groupId,
      sender_id: senderId,
      kind: "ai-response",
      content,
      body: {
        ...(body ?? {}),
        text: content,
        sender_name: "TripSmith AI",
      },
    }),
    body: JSON.stringify(payload),
  });
  
  if (!res.ok) {
    const text = await res.text();
    console.error("❌ sendAIMessage failed:", text);
    throw new Error(text || "Failed to send AI message");
  }
  const response = await res.json();
  console.log("✅ sendAIMessage successful");
  return response as ChatMessage;
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
