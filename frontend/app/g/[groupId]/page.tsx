"use client";

import { useEffect, useRef, useState } from "react";
import { useParams } from "next/navigation";

const starterMessages = [
  {
    id: "1",
    sender: "Ava",
    senderInitials: "A",
    time: "08:41 AM",
    content: "Morning! Found a cute pastel rooftop in Lisbon for Friday night 😍",
    variant: "friend",
  },
  {
    id: "2",
    sender: "Noah",
    senderInitials: "N",
    time: "08:42 AM",
    content: "Let's lock it in! How's everyone feeling about Saturday plans?",
    variant: "friend",
  },
  {
    id: "3",
    sender: "TripSmith AI",
    senderInitials: "AI",
    time: "08:43 AM",
    content:
      "I can shortlist three Saturday activities based on your saved prefs: a sailing brunch, Sintra day trip, or LX Factory art crawl. Want me to drop the details?",
    variant: "ai",
  },
  {
    id: "4",
    sender: "Maya",
    senderInitials: "M",
    time: "08:44 AM",
    content: "LX Factory art crawl sounds dreamy ✨",
    variant: "me",
  },
];

export default function GroupPage() {
  const params = useParams<{ groupId: string }>();
  const groupId = params?.groupId ?? "group-001";
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState(starterMessages);
  const scrollRef = useRef<HTMLDivElement>(null);

  const newId = () =>
    typeof crypto !== "undefined" && "randomUUID" in crypto
      ? crypto.randomUUID()
      : `${Date.now()}-${Math.random().toString(16).slice(2)}`;

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  const handleSend = () => {
    const content = input.trim();
    if (!content) return;

    const newMessage = {
      id: newId(),
      sender: "You",
      senderInitials: "Y",
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      content,
      variant: "me" as const,
    };

    setMessages((prev) => [...prev, newMessage]);
    setInput("");

    const shouldSummonAi = /(^|\s)(\/ai|@ai|@tripsmith)/i.test(content);
    if (shouldSummonAi) {
      setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          {
            id: newId(),
            sender: "TripSmith AI",
            senderInitials: "AI",
            time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
            content:
              "On it! I'll gather options based on your latest chat context and preferences.",
            variant: "ai" as const,
          },
        ]);
      }, 600);
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
            <h1 className="text-3xl font-bold text-gray-900">Creators to Lisbon</h1>
            <p className="text-sm text-gray-500">
              Invite code ·{" "}
              <span className="font-semibold tracking-wide text-blue-500">
                {groupId}
              </span>
            </p>
          </div>
          <button className="rounded-full bg-gradient-to-r from-blue-500 to-blue-600 px-5 py-2 text-sm font-semibold text-white shadow-lg shadow-blue-500/40 hover:scale-[1.02] transition">
            Ask TripSmith AI
          </button>
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
            <div className="flex items-center gap-1 rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-600">
              <span className="text-green-500">•</span> 4 online
            </div>
          </div>

          <div
            ref={scrollRef}
            className="flex h-[60vh] flex-col gap-4 overflow-y-auto px-6 py-6 scrollbar-thin scrollbar-track-transparent scrollbar-thumb-blue-100"
          >
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-3 ${
                  msg.variant === "me" ? "flex-row-reverse text-right" : "text-left"
                }`}
              >
                <div
                  className={`flex h-11 w-11 items-center justify-center rounded-2xl text-sm font-semibold text-white shadow ${
                    msg.variant === "ai"
                      ? "bg-gradient-to-br from-purple-500 to-indigo-500 shadow-purple-200"
                      : "bg-gradient-to-br from-blue-500 to-blue-600 shadow-blue-200"
                  }`}
                >
                  {msg.senderInitials}
                </div>
                <div
                  className={`max-w-md rounded-3xl px-5 py-4 shadow transition ${
                    msg.variant === "me"
                      ? "bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-blue-100"
                      : msg.variant === "ai"
                        ? "bg-gradient-to-r from-purple-50 to-blue-50 text-slate-800 border border-purple-100"
                        : "bg-white text-slate-800 border border-blue-50"
                  }`}
                >
                  <div className="flex items-center justify-between gap-4 text-xs font-semibold">
                    <span className={msg.variant === "me" ? "text-white/80" : "text-blue-500"}>
                      {msg.sender}
                    </span>
                    <span className={msg.variant === "me" ? "text-white/70" : "text-gray-400"}>
                      {msg.time}
                    </span>
                  </div>
                  <p className="mt-2 text-base leading-relaxed">{msg.content}</p>
                  {msg.variant === "ai" && (
                    <div className="mt-3 flex gap-2 text-xs font-semibold">
                      <button className="rounded-full bg-white/70 px-3 py-1 text-blue-600 hover:bg-white">
                        See details
                      </button>
                      <button className="rounded-full bg-transparent px-3 py-1 text-slate-500 hover:text-slate-800">
                        Not now
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          <div className="flex flex-col gap-3 border-t border-blue-50 px-6 py-5 sm:flex-row">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSend()}
              placeholder="Share an update, drop a link, or ask /ai for help…"
              className="flex-1 rounded-full border border-blue-100 bg-white px-5 py-3 text-sm text-gray-700 shadow-sm placeholder:text-gray-400 focus:border-blue-400 focus:outline-none"
            />
            <button
              onClick={handleSend}
              className="rounded-full bg-gradient-to-r from-orange-400 via-pink-400 to-purple-500 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-orange-200 transition hover:opacity-90"
            >
              Send
            </button>
          </div>
        </div>

        <div className="rounded-3xl bg-white/70 p-6 text-sm text-gray-600 shadow-lg shadow-orange-100 ring-1 ring-orange-100 space-y-2">
          <p className="font-semibold text-gray-800">Heads up ✨</p>
          <p>
            Anyone with the invite code can request to join. Group owners approve requests so you stay in control.
          </p>
          <p className="text-gray-500">
            TripSmith AI stays quiet unless you type <span className="font-semibold text-blue-500">/ai</span> or mention <span className="font-semibold text-blue-500">@TripSmith</span> in chat.
          </p>
        </div>
      </main>
    </div>
  );
}


