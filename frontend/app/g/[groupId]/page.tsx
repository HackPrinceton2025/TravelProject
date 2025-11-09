"use client";

import { useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { supabase } from "../../lib/supabaseClient";
import { ChatMessage, fetchGroupMessages, sendGroupMessage, callAIAgent } from "../../lib/chat";
import CardCarousel from "../../components/CardCarousel";

type MessageBubble = ChatMessage & {
  variant: "me" | "friend";
  initials: string;
  timestamp: string;
  displayName: string;
  text: string;
  cards?: any[];
};

export default function GroupPage() {
  const params = useParams<{ groupId: string }>();
  const router = useRouter();
  const groupId = params?.groupId ?? "";

  const [userId, setUserId] = useState<string | null>(null);
  const [userName, setUserName] = useState<string | null>(null);
  const [authChecked, setAuthChecked] = useState(false);
  const [messages, setMessages] = useState<MessageBubble[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Ensure only authenticated users can access the chat.
  useEffect(() => {
    const getUser = async () => {
      const {
        data: { user },
      } = await supabase.auth.getUser();

      if (!user) {
        setAuthChecked(true);
        router.push("/");
        return;
      }

      setUserId(user.id);
      setUserName(user.user_metadata?.name || user.email);
      setAuthChecked(true);
    };

    getUser();
  }, [router]);

  // Initial load + realtime subscription.
  useEffect(() => {
    if (!groupId || !authChecked || !userId) return;

    const loadMessages = async () => {
      try {
        const data = await fetchGroupMessages(groupId);
        setMessages(data.map((msg) => decorateMessage(msg, userId, userName)));
      } catch (err) {
        console.error("Failed to fetch messages", err);
      } finally {
        setLoading(false);
      }
    };

    loadMessages();

    const channel = supabase
      .channel(`messages:${groupId}`)
      .on(
        "postgres_changes",
        {
          event: "INSERT",
          schema: "public",
          table: "messages",
          filter: `group_id=eq.${groupId}`,
        },
        (payload) => {
          const newMessage = payload.new as ChatMessage;
          setMessages((prev) =>
            prev.some((existing) => existing.id === newMessage.id)
              ? prev
              : [...prev, decorateMessage(newMessage, userId, userName)],
          );
        },
      )
      .subscribe();

    return () => {
      channel.unsubscribe();
    };
  }, [groupId, userId, userName, authChecked]);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed || !userId || !groupId || sending) return;

    setSending(true);
    try {
      // Check if message starts with @ai
      const isAiMessage = trimmed.toLowerCase().startsWith("@ai");
      const messageContent = isAiMessage ? trimmed.slice(3).trim() : trimmed;

      // Send user's message first
      const inserted = await sendGroupMessage({
        groupId,
        content: trimmed,
        senderId: userId,
      });
      setInput("");
      
      if (inserted) {
        setMessages((prev) =>
          prev.some((existing) => existing.id === inserted.id)
            ? prev
            : [...prev, decorateMessage(inserted, userId, userName)],
        );
      }

      // If it's an AI message, call the agent
      if (isAiMessage && messageContent) {
        setAiLoading(true);
        try {
          // Build chat history from recent messages (last 10)
          // const chatHistory = messages.slice(-10).map((msg) => ({
          //   role: msg.sender_id === "ai-agent" ? "assistant" : "user",
          //   content: msg.text,
          // }));
          console.log(userId);
          console.log(groupId)
          const agentResponse = await callAIAgent({
            message: messageContent,
            userId,
            groupId,
            // chatHistory,
          });

          // Add AI's response to local state only (not saving to DB)
          if (agentResponse.message || agentResponse.cards) {
            const aiMessage: MessageBubble = {
              id: `ai-${Date.now()}`, // Temporary local ID
              group_id: groupId,
              sender_id: "ai-agent",
              kind: "ai-response",
              body: { text: agentResponse.message || "" },
              created_at: new Date().toISOString(),
              variant: "friend",
              initials: "AI",
              displayName: "AI Travel Agent",
              text: agentResponse.message || "", // Empty string if only cards
              timestamp: new Date().toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
              }),
              cards: agentResponse.cards || [],
            };

            setMessages((prev) => [...prev, aiMessage]);
          }
        } catch (err) {
          console.error("Failed to call AI agent", err);
          // Add error message to local state
          const errorMessage: MessageBubble = {
            id: `ai-error-${Date.now()}`,
            group_id: groupId,
            sender_id: "ai-agent",
            kind: "ai-response",
            body: { text: "Sorry. There was an error calling AI agent." },
            created_at: new Date().toISOString(),
            variant: "friend",
            initials: "AI",
            displayName: "AI Travel Agent",
            text: "Sorry. There was an error calling AI agent.",
            timestamp: new Date().toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            }),
          };

          setMessages((prev) => [...prev, errorMessage]);
        } finally {
          setAiLoading(false);
        }
      }
    } catch (err) {
      console.error("Failed to send message", err);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-orange-50">
      <header className="border-b border-white/60 bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-5">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.4em] text-blue-400">
              TripSmith • Group
            </p>
            <h1 className="text-3xl font-bold text-gray-900">Group chat</h1>
            <p className="text-sm text-gray-500">
              Invite code ·{" "}
              <span className="font-semibold tracking-wide text-blue-500">
                {groupId || "loading"}
              </span>
            </p>
          </div>
        </div>
      </header>

      <main className="mx-auto flex max-w-5xl flex-col gap-5 px-4 py-8">
        <div className="rounded-3xl bg-white/80 shadow-xl shadow-blue-100/60 ring-1 ring-blue-50">
          <div className="flex items-center justify-between border-b border-blue-50 px-6 py-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.35em] text-blue-400">
                Group chat
              </p>
              <h2 className="text-xl font-semibold text-gray-900">
                Your sunny planning space
              </h2>
            </div>
          </div>

          <div
            ref={scrollRef}
            className="flex h-[60vh] flex-col gap-4 overflow-y-auto px-6 py-6 scrollbar-thin scrollbar-track-transparent scrollbar-thumb-blue-100"
          >
            {loading ? (
              <p className="text-sm text-gray-500">Loading messages…</p>
            ) : (
              <>
                {messages.map((msg) => {
                  const isAI = msg.sender_id === "ai-agent";
                  return (
                    <div
                      key={msg.id}
                      className={`flex flex-col gap-3 ${
                        msg.variant === "me" ? "items-end" : "items-start"
                      }`}
                    >
                      {/* Show message bubble only if text exists or it's not an AI message */}
                      {(msg.text || !isAI) && (
                        <div className={`flex gap-3 ${
                          msg.variant === "me" ? "flex-row-reverse text-right" : "text-left"
                        }`}>
                          <div className={`flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-2xl text-sm font-semibold text-white shadow ${
                            isAI 
                              ? "bg-gradient-to-br from-purple-500 to-purple-600 shadow-purple-200"
                              : "bg-gradient-to-br from-blue-500 to-blue-600 shadow-blue-200"
                          }`}>
                            {msg.initials}
                          </div>
                          <div
                            className={`max-w-md rounded-3xl border px-5 py-4 shadow transition ${
                              msg.variant === "me"
                                ? "border-transparent bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-blue-100"
                                : isAI
                                ? "border-purple-100 bg-gradient-to-br from-purple-50 to-pink-50 text-slate-800"
                                : "border-blue-50 bg-white text-slate-800"
                            }`}
                          >
                            <div className="flex items-center justify-between gap-4 text-xs font-semibold">
                              <span className={
                                msg.variant === "me" 
                                  ? "text-white/80" 
                                  : isAI 
                                  ? "text-purple-600" 
                                  : "text-blue-500"
                              }>
                                {msg.displayName}
                              </span>
                              <span className={msg.variant === "me" ? "text-white/70" : "text-gray-400"}>
                                {msg.timestamp}
                              </span>
                            </div>
                            <div className="mt-2 text-base leading-relaxed whitespace-pre-wrap">
                              {msg.text}
                            </div>
                          </div>
                        </div>
                      )}
                      {/* Render cards if present */}
                      {msg.cards && msg.cards.length > 0 && (
                        <div className="w-full max-w-4xl">
                          <CardCarousel cards={msg.cards} />
                        </div>
                      )}
                    </div>
                  );
                })}
                {aiLoading && (
                  <div className="flex gap-3 text-left">
                    <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-purple-500 to-purple-600 text-sm font-semibold text-white shadow shadow-purple-200">
                      AI
                    </div>
                    <div className="max-w-md rounded-3xl border border-purple-50 bg-white px-5 py-4 text-slate-800 shadow">
                      <div className="flex items-center gap-2">
                        <div className="flex gap-1">
                          <div className="h-2 w-2 animate-bounce rounded-full bg-purple-500" style={{ animationDelay: "0ms" }}></div>
                          <div className="h-2 w-2 animate-bounce rounded-full bg-purple-500" style={{ animationDelay: "150ms" }}></div>
                          <div className="h-2 w-2 animate-bounce rounded-full bg-purple-500" style={{ animationDelay: "300ms" }}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>

          <div className="flex flex-col gap-3 border-t border-blue-50 px-6 py-5 sm:flex-row">
            <div className="flex-1">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSend()}
                placeholder="Share an update or plan your next step… (Tip: Start with @ai to ask AI agent)"
                className="w-full rounded-full border border-blue-100 bg-white px-5 py-3 text-sm text-gray-700 shadow-sm placeholder:text-gray-400 focus:border-blue-400 focus:outline-none"
              />
            </div>
            <button
              onClick={handleSend}
              disabled={sending || aiLoading}
              className="rounded-full bg-gradient-to-r from-orange-400 via-pink-400 to-purple-500 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-orange-200 transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {sending ? "Sending…" : aiLoading ? "AI Loading..." : "Send"}
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}

function decorateMessage(
  message: ChatMessage,
  currentUserId: string | null,
  currentUserName: string | null,
): MessageBubble {
  const isAI = message.sender_id === "ai-agent";
  const isSelf = message.sender_id === currentUserId;
  const text = extractText(message.body);
  
  let displayName: string;
  let initials: string;
  
  if (isAI) {
    displayName = "AI Travel Agent";
    initials = "AI";
  } else {
    const fallbackName = isSelf ? currentUserName || "You" : "Tripmate";
    displayName = (message as any).sender_name || fallbackName;
    initials =
      displayName?.slice(0, 2).toUpperCase() ||
      message.sender_id.slice(0, 2).toUpperCase() ||
      "??";
  }

  return {
    ...message,
    variant: isSelf ? "me" : "friend",
    initials,
    displayName,
    text,
    timestamp: new Date(message.created_at).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    }),
  };
}

function extractText(body: ChatMessage["body"]): string {
  if (body === null || body === undefined) return "";

  if (typeof body === "string") return body;

  if (typeof body === "object") {
    if (typeof body.text === "string") return body.text;
    if (typeof body.message === "string") return body.message;
    if (typeof body.content === "string") return body.content;
    if ("data" in body && typeof body.data === "string") return body.data;
    try {
      return JSON.stringify(body);
    } catch {
      return "";
    }
  }

  return String(body);
}
