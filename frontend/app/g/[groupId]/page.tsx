"use client";

import { useCallback, useEffect, useRef, useState } from "react";
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

  // Fixed UUID for AI agent (consistent across all groups)
  const AI_AGENT_ID = "00000000-0000-0000-0000-000000000000";

  const [userId, setUserId] = useState<string | null>(null);
  const [userName, setUserName] = useState<string | null>(null);
  const [authChecked, setAuthChecked] = useState(false);
  const [groupInfo, setGroupInfo] = useState<{ name: string; invite_code: string } | null>(null);
const [messages, setMessages] = useState<MessageBubble[]>([]);
const [nameDirectory, setNameDirectory] = useState<Record<string, string>>({});
const nameDirectoryRef = useRef<Record<string, string>>({});
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

useEffect(() => {
  if (userId && userName) {
    setNameDirectory((prev) =>
      prev[userId] ? prev : { ...prev, [userId]: userName },
    );
  }
}, [userId, userName]);

useEffect(() => {
  nameDirectoryRef.current = nameDirectory;
}, [nameDirectory]);

const fetchSenderNames = useCallback(
  async (msgs: ChatMessage[]): Promise<Record<string, string>> => {
    const unknownIds = Array.from(
      new Set(
        msgs
          .filter(
            (msg) =>
              msg.sender_id !== "00000000-0000-0000-0000-000000000000" &&
              !nameDirectoryRef.current[msg.sender_id] &&
              !msg.body?.sender_name,
          )
          .map((msg) => msg.sender_id),
      ),
    );
    if (!unknownIds.length) return {};
    try {
      const { data, error } = await supabase
        .from("users")
        .select("id,name,email")
        .in("id", unknownIds);
      if (error) {
        console.error("Failed to fetch sender names", error);
        return {};
      }
      const map: Record<string, string> = {};
      data?.forEach((entry: any) => {
        const label = entry.name || entry.email || "Tripmate";
        if (label) {
          map[entry.id] = label;
        }
      });
      return map;
    } catch (err) {
      console.error("Failed to fetch sender names", err);
      return {};
    }
  },
  [],
);

const fetchAndStoreSenderName = useCallback(
  async (senderId: string): Promise<string | undefined> => {
    if (
      senderId === "00000000-0000-0000-0000-000000000000" ||
      nameDirectoryRef.current[senderId]
    ) {
      return nameDirectoryRef.current[senderId];
    }
    try {
      const { data, error } = await supabase
        .from("users")
        .select("id,name,email")
        .eq("id", senderId)
        .single();
      if (error || !data) return;
      const label = data.name || data.email || "Tripmate";
      setNameDirectory((prev) => ({ ...prev, [senderId]: label }));
      return label;
    } catch (err) {
      console.error("Failed to fetch sender name", err);
    }
  },
  [],
);

  // Initial load + realtime subscription.
  useEffect(() => {
    if (!groupId || !authChecked || !userId) return;

    const loadGroupInfo = async () => {
      try {
        const { data, error } = await supabase
          .from("groups")
          .select("name, invite_code")
          .eq("id", groupId)
          .single();
        if (!error && data) {
          setGroupInfo({
            name: data.name ?? "Group chat",
            invite_code: data.invite_code ?? "",
          });
        }
      } catch (err) {
        console.error("Failed to load group info", err);
      }
    };

    loadGroupInfo();

    const loadMessages = async () => {
      try {
        const data = await fetchGroupMessages(groupId);
        const newNames = await fetchSenderNames(data);
        const combinedNames =
          Object.keys(newNames).length > 0
            ? { ...nameDirectoryRef.current, ...newNames }
            : nameDirectoryRef.current;
        if (Object.keys(newNames).length) {
          setNameDirectory(combinedNames);
        }
        setMessages(
          data.map((msg) =>
            decorateMessage(msg, userId, userName, combinedNames),
          ),
        );
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
        async (payload) => {
          const newMessage = payload.new as ChatMessage;
          
          // Skip AI messages - they're added locally with cards
          if (newMessage.sender_id === "00000000-0000-0000-0000-000000000000") {
            return;
          }

          const ensuredName = await fetchAndStoreSenderName(newMessage.sender_id);
          const lookup = ensuredName
            ? { ...nameDirectoryRef.current, [newMessage.sender_id]: ensuredName }
            : nameDirectoryRef.current;
          
          setMessages((prev) =>
            prev.some((existing) => existing.id === newMessage.id)
              ? prev
              : [
                  ...prev,
                  decorateMessage(
                    newMessage,
                    userId,
                    userName,
                    lookup,
                  ),
                ],
          );
        },
      )
      .subscribe();

    return () => {
      channel.unsubscribe();
    };
  }, [groupId, userId, userName, authChecked, fetchSenderNames, fetchAndStoreSenderName]);

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
        senderName: userName,
      });
      setInput("");
      
      if (inserted) {
        setMessages((prev) =>
          prev.some((existing) => existing.id === inserted.id)
            ? prev
            : [
                ...prev,
                decorateMessage(inserted, userId, userName, {
                  ...nameDirectoryRef.current,
                  [userId]: userName || "You",
                }),
              ],
        );
      }

      // If it's an AI message, call the agent
      if (isAiMessage && messageContent) {
        setAiLoading(true);
        try {
          const agentResponse = await callAIAgent({
            message: messageContent,
            userId,
            groupId,
          });

          //console.log("🤖 Raw AI Response:", agentResponse);
          //console.log("🤖 Raw AI Response type:", typeof agentResponse);

          // STEP 1: agentResponse itself might be a string, parse it
          let messageText = "";
          let cardsArray: any[] = [];
          
          try {
            let parsedData;
            
            // If agentResponse is a string, parse it first
            if (typeof agentResponse === 'string') {
              //console.log("📝 agentResponse is a string, parsing...");
              parsedData = JSON.parse(agentResponse);
            } else {
              parsedData = agentResponse;
            }
            
            //console.log("📦 Parsed Data:", parsedData);
            
            // STEP 2: parsedData.message is another JSON string, parse it again
            if (typeof parsedData.message === 'string') {
              try {
                const innerData = JSON.parse(parsedData.message);
                //console.log("🔄 Inner Data (parsed from message):", innerData);
                
                messageText = String(innerData.message || "");
                cardsArray = Array.isArray(innerData.cards) ? innerData.cards : [];
              } catch (innerParseError) {
                //console.error("❌ Failed to parse inner message:", innerParseError);
                // If inner parse fails, use message as-is
                messageText = String(parsedData.message || "");
                cardsArray = Array.isArray(parsedData.cards) ? parsedData.cards : [];
              }
            } else {
              // Direct extraction
              messageText = String(parsedData.message || "");
              cardsArray = Array.isArray(parsedData.cards) ? parsedData.cards : [];
            }
            
          } catch (parseError) {
            console.error("❌ Failed to parse:", parseError);
            // Fallback
            messageText = "";
            cardsArray = [];
          }

          //console.log("✅ Separated Data:");
          //console.log("  📄 Message Text:", messageText);
          //console.log("  📄 Text Length:", messageText.length, "characters");
          //console.log("  🎴 Cards Array:", cardsArray);
          //console.log("  🎴 Cards Count:", cardsArray.length);
          //console.log("  🎴 Cards JSON Length:", JSON.stringify(cardsArray).length, "characters");

          // Save AI's response to DB with separated fields
          if (messageText || cardsArray.length > 0) {
            const { sendAIMessage } = await import("../../lib/chat");
            const aiMessage = await sendAIMessage({
              groupId,
              senderId: AI_AGENT_ID,
              content: messageText, // Plain text in content field
              body: cardsArray.length > 0 ? cardsArray : null, // Cards array in body field
            });

            if (aiMessage) {
              // Add to local state with proper formatting INCLUDING cards
              const formattedMessage: MessageBubble = {
                ...aiMessage,
                variant: "friend",
                initials: "AI",
                displayName: "AI Travel Agent",
                text: messageText,
                timestamp: new Date(aiMessage.created_at).toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                }),
                cards: cardsArray, // Cards for local display
              };
              
              setMessages((prev) =>
                prev.some((existing) => existing.id === formattedMessage.id)
                  ? prev
                  : [...prev, formattedMessage],
              );
            }
          }
        } catch (err) {
          console.error("Failed to call AI agent", err);
          // Save error message to DB
          try {
            const errorMessage = await sendGroupMessage({
              groupId,
              content: "Sorry. There was an error calling AI agent.",
              senderId: AI_AGENT_ID,
            });

            if (errorMessage) {
              const formattedError: MessageBubble = {
                ...errorMessage,
                variant: "friend",
                initials: "AI",
                displayName: "AI Travel Agent",
                text: "Sorry. There was an error calling AI agent.",
                timestamp: new Date(errorMessage.created_at).toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                }),
              };
              
              setMessages((prev) =>
                prev.some((existing) => existing.id === formattedError.id)
                  ? prev
                  : [...prev, formattedError],
              );
            }
          } catch (dbErr) {
            console.error("Failed to save error message to DB", dbErr);
          }
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
            <h1 className="text-3xl font-bold text-gray-900">
              {groupInfo?.name ?? "Group chat"}
            </h1>
            <p className="text-sm text-gray-500">
              Invite code ·{" "}
              <span className="font-semibold tracking-wide text-blue-500">
                {groupInfo?.invite_code?.toUpperCase() || groupId || "loading"}
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
                Let's plan the trip!
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
                  const isAI = msg.sender_id === "00000000-0000-0000-0000-000000000000";
                  return (
                    <div
                      key={msg.id}
                      className={`flex flex-col gap-3 ${
                        msg.variant === "me" ? "items-end" : "items-start"
                      }`}
                    >
                      {/* Show message bubble only if text exists or it's not an AI message */}
                      {(msg.text || !isAI) && (
                        <div
                          className={`flex gap-3 items-start ${
                            msg.variant === "me" ? "flex-row-reverse text-right" : "text-left"
                          }`}
                        >
                          <div className={`flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-2xl text-sm font-semibold text-white shadow ${
                            isAI 
                              ? "bg-gradient-to-br from-purple-500 to-purple-600 shadow-purple-200"
                              : "bg-gradient-to-br from-blue-500 to-blue-600 shadow-blue-200"
                          }`}>
                            {msg.initials}
                          </div>
                          <div
                            className={`max-w-md rounded-3xl border px-5 py-4 shadow transition text-left ${
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
  nameDirectory: Record<string, string> = {},
): MessageBubble {
  const isAI = message.sender_id === "00000000-0000-0000-0000-000000000000";
  const isSelf = message.sender_id === currentUserId;
  
  // Extract text: prioritize content field (new schema)
  let text = "";
  if (message.content) {
    text = message.content; // Use content field if available
  } else if (message.body) {
    text = extractText(message.body); // Fallback to body for old messages
  }
  
  // Extract cards from body field (only for AI messages)
  let cards: any[] = [];
  if (isAI && message.body && typeof message.body === "object") {
    if (Array.isArray(message.body)) {
      cards = message.body; // body is directly the cards array
    } else if (Array.isArray((message.body as any).cards)) {
      cards = (message.body as any).cards; // body has a cards property
    }
  }
  
  let displayName: string;
  let initials: string;
  
  if (isAI) {
    displayName = "AI Travel Agent";
    initials = "AI";
  } else {
    const directoryName = nameDirectory[message.sender_id];
    const bodyName =
      typeof message.body === "object" && message.body !== null
        ? message.body.sender_name || message.body.author || null
        : null;
    const fallbackName =
      directoryName || (isSelf ? currentUserName || "You" : null) || currentUserName || "Tripmate";
    displayName = bodyName || (message as any).sender_name || fallbackName;
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
    cards,
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
