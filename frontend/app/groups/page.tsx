"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { createGroup } from "../lib/api";

const randomCode = () =>
  `grp-${Math.random().toString(36).slice(2, 6)}${Math.random()
    .toString(36)
    .slice(2, 4)}`.toUpperCase();

export default function GroupsLanding() {
  const router = useRouter();
  const [creating, setCreating] = useState(false);
  const [createdGroupId, setCreatedGroupId] = useState<string | null>(null);
  const [joinCode, setJoinCode] = useState("");
  const [joinStatus, setJoinStatus] = useState<string | null>(null);
  const [joining, setJoining] = useState(false);
  const [groupName, setGroupName] = useState("");

  const handleCreateGroup = async () => {
    if (creating || !groupName.trim()) return;
    setCreating(true);
    setJoinStatus(null);

    try {
      // For now, generate a random group ID
      // Later, this will call the actual API
      const newId = randomCode().toLowerCase();
      setCreatedGroupId(newId);
      
      // TODO: Uncomment when backend is ready
      // const group = await createGroup(groupName.trim());
      // setCreatedGroupId(group.id);
    } catch (error) {
      console.error("Failed to create group:", error);
      setJoinStatus("Failed to create group. Please try again.");
    } finally {
      setCreating(false);
    }
  };

  const handleJoinGroup = () => {
    if (!joinCode.trim() || joining) return;
    setJoining(true);
    setCreatedGroupId(null);
    setJoinStatus(null);

    // For now, just navigate to the group page
    // Later, this will validate the code and join the group via API
    setTimeout(() => {
      const normalizedCode = joinCode.trim().toLowerCase().replace(/\s+/g, "-");
      router.push(`/g/${normalizedCode}`);
      setJoining(false);
    }, 300);
  };

  const openGroup = () => {
    if (createdGroupId) {
      router.push(`/g/${createdGroupId.toLowerCase()}`);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-orange-50 text-gray-800">
      <header className="border-b border-white/80 bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-4 px-6 py-6">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.4em] text-blue-400">
              TripSmith
            </p>
            <h1 className="text-3xl font-bold text-gray-900">Pick your planning space</h1>
            <p className="text-sm text-gray-500">
              Create a fresh room or hop into an existing crew with a code.
            </p>
          </div>
          <button
            onClick={() => router.push("/")}
            className="rounded-full bg-blue-50 px-4 py-2 text-xs font-semibold text-blue-600 shadow-sm hover:bg-blue-100 transition"
          >
            Home
          </button>
        </div>
      </header>

      <main className="mx-auto flex max-w-5xl flex-col gap-10 px-4 py-10">
        <section className="grid gap-6 md:grid-cols-2">
          {/* Create Group Card */}
          <div className="rounded-3xl bg-white/90 p-6 shadow-xl shadow-blue-100/70 ring-1 ring-blue-50">
            <p className="text-sm font-semibold uppercase tracking-[0.3em] text-blue-400">
              Start new
            </p>
            <h2 className="mt-2 text-2xl font-bold text-gray-900">Create a group chat</h2>
            <p className="mt-2 text-sm text-gray-500">
              Invite friends, set preferences, and let TripSmith keep the conversation flowing.
            </p>
            <input
              type="text"
              value={groupName}
              onChange={(e) => setGroupName(e.target.value)}
              placeholder="Enter group name..."
              className="mt-4 w-full rounded-2xl border border-blue-100 bg-white px-4 py-3 text-sm text-gray-900 shadow-sm placeholder:text-gray-400 focus:border-blue-300 focus:outline-none"
              onKeyPress={(e) => e.key === "Enter" && handleCreateGroup()}
            />
            <button
              className="mt-4 w-full rounded-2xl bg-gradient-to-r from-blue-500 to-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-500/30 transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-60"
              onClick={handleCreateGroup}
              disabled={creating || !groupName.trim()}
            >
              {creating ? "Creating..." : "Create new group"}
            </button>
            {createdGroupId && (
              <div className="mt-4 rounded-2xl border border-blue-100 bg-blue-50/70 p-4 text-sm text-blue-700">
                <p className="font-semibold">Share this invite code:</p>
                <p className="mt-1 text-2xl tracking-[0.35em]">{createdGroupId.toUpperCase()}</p>
                <div className="mt-3 flex flex-wrap gap-3">
                  <button
                    onClick={() => {
                      if (typeof navigator !== "undefined" && navigator.clipboard) {
                        navigator.clipboard.writeText(createdGroupId);
                      }
                    }}
                    className="rounded-full border border-blue-200 px-4 py-1 text-xs font-semibold text-blue-600 hover:bg-white transition"
                  >
                    Copy code
                  </button>
                  <button
                    onClick={openGroup}
                    className="rounded-full border border-blue-200 px-4 py-1 text-xs font-semibold text-blue-600 hover:bg-white transition"
                  >
                    Enter chat
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Join Group Card */}
          <div className="rounded-3xl bg-white/90 p-6 shadow-xl shadow-orange-100/80 ring-1 ring-orange-100">
            <p className="text-sm font-semibold uppercase tracking-[0.3em] text-orange-400">
              Join crew
            </p>
            <h2 className="mt-2 text-2xl font-bold text-gray-900">Enter a group code</h2>
            <p className="mt-2 text-sm text-gray-500">
              Others can share a 6-character code. Drop it below and we'll take you to the group.
            </p>
            <input
              className="mt-4 w-full rounded-2xl border border-orange-100 bg-white px-4 py-3 text-sm uppercase tracking-[0.5em] text-gray-900 shadow-sm placeholder:tracking-normal placeholder:text-gray-400 focus:border-orange-300 focus:outline-none"
              maxLength={12}
              placeholder="GRP-AB12"
              value={joinCode}
              onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
              onKeyPress={(e) => e.key === "Enter" && handleJoinGroup()}
            />
            <button
              className="mt-4 w-full rounded-2xl bg-gradient-to-r from-orange-400 via-pink-400 to-purple-500 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-orange-200 transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-60"
              onClick={handleJoinGroup}
              disabled={joining || !joinCode.trim()}
            >
              {joining ? "Joining..." : "Join group"}
            </button>
            {joinStatus && (
              <p className="mt-4 rounded-2xl border border-orange-100 bg-orange-50/80 p-4 text-sm text-orange-700">
                {joinStatus}
              </p>
            )}
          </div>
        </section>

        <section className="rounded-3xl bg-white/80 p-6 shadow-lg shadow-blue-100/70 ring-1 ring-white">
          <div className="flex flex-col gap-2">
            <p className="text-sm font-semibold uppercase tracking-[0.3em] text-gray-400">
              Tips
            </p>
            <h3 className="text-xl font-semibold text-gray-900">How TripSmith groups work</h3>
            <div className="mt-4 grid gap-4 md:grid-cols-3">
              {[
                {
                  title: "Invite safely",
                  body: "Owners approve join requests so only the right people enter the chat.",
                },
                {
                  title: "Summon AI",
                  body: "Type /ai or @TripSmith inside any chat to pull in routes, ideas, or splits.",
                },
                {
                  title: "Stay in sync",
                  body: "All chats, polls, and budgets stay in one place for the whole crew.",
                },
              ].map((tip) => (
                <div
                  key={tip.title}
                  className="rounded-2xl border border-white/60 bg-white/70 p-4 text-sm text-gray-600"
                >
                  <p className="font-semibold text-gray-900">{tip.title}</p>
                  <p className="mt-2">{tip.body}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

