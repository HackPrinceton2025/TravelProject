import { supabase } from "./supabaseClient";

export type ChatMessage = {
  id: string;
  group_id: string;
  sender_id: string;
  sender_name: string | null;
  content: string;
  created_at: string;
};

type MessageInsert = {
  groupId: string;
  senderId: string;
  senderName: string | null;
  content: string;
};

export async function fetchGroupMessages(groupId: string) {
  const { data, error } = await supabase
    .from("messages")
    .select("*")
    .eq("group_id", groupId)
    .order("created_at", { ascending: true });

  if (error) throw error;
  return (data || []) as ChatMessage[];
}

export async function sendGroupMessage({
  groupId,
  senderId,
  senderName,
  content,
}: MessageInsert) {
  const { error } = await supabase.from("messages").insert({
    group_id: groupId,
    sender_id: senderId,
    sender_name: senderName,
    content,
  });

  if (error) throw error;
}
