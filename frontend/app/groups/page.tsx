"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "../lib/supabaseClient";
import { createGroup, joinGroupByCode, GroupRecord } from "../lib/api";

type BannerState = { tone: "success" | "error"; text: string } | null;
type MyGroup = {
  id: string;
  name: string;
  invite_code: string;
  role: string;
};

export default function GroupsLanding() {
  const router = useRouter();
  const [userId, setUserId] = useState<string | null>(null);
  const [authChecked, setAuthChecked] = useState(false);

  const [creating, setCreating] = useState(false);
  const [createdGroup, setCreatedGroup] = useState<GroupRecord | null>(null);
  const [createBanner, setCreateBanner] = useState<BannerState>(null);

  const [joinCode, setJoinCode] = useState("");
  const [joinBanner, setJoinBanner] = useState<BannerState>(null);
  const [joining, setJoining] = useState(false);

  const [groupName, setGroupName] = useState("");
  const [myGroups, setMyGroups] = useState<MyGroup[]>([]);
  const [groupsLoading, setGroupsLoading] = useState(true);
  const [groupsError, setGroupsError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUser = async () => {
      const {
        data: { user },
      } = await supabase.auth.getUser();

      if (!user) {
        setAuthChecked(true);
        router.push("/");
        return;
      }

      setUserId(user.id);
      setAuthChecked(true);
    };

    fetchUser();
  }, [router]);

  const loadMemberships = useCallback(
    async (currentUserId: string) => {
      setGroupsLoading(true);
      setGroupsError(null);
      try {
        const { data, error } = await supabase
          .from("group_members")
          .select(
            `
            group_id,
            role,
            groups:groups (
              id,
              name,
              invite_code,
              created_by
            )
          `,
          )
          .eq("user_id", currentUserId);

        if (error) {
          throw error;
        }

        const mapped =
          data?.map((row: any) => ({
            id: row.groups?.id ?? row.group_id,
            name: row.groups?.name ?? "Untitled trip",
            invite_code: row.groups?.invite_code ?? "N/A",
            role:
              row.role ||
              (row.groups?.created_by === currentUserId ? "Owner" : "Member"),
          })) ?? [];

        // Remove duplicates by group id
        const uniqueGroups = mapped.reduce((acc: MyGroup[], current) => {
          const exists = acc.find(item => item.id === current.id);
          if (!exists) {
            acc.push(current);
          }
          return acc;
        }, []);

        setMyGroups(uniqueGroups);
      } catch (err: any) {
        console.error("Failed to load groups", err);
        setGroupsError(err?.message || "Failed to load groups");
      } finally {
        setGroupsLoading(false);
      }
    },
    [],
  );

  useEffect(() => {
    if (userId) {
      loadMemberships(userId);
    }
  }, [userId, loadMemberships]);

  const handleCreateGroup = async () => {
    if (creating || !groupName.trim() || !userId) return;
    setCreating(true);
    setCreateBanner(null);
    setJoinBanner(null);

    try {
      const group = await createGroup(groupName.trim(), userId);
      await joinGroupByCode(group.invite_code, userId);
      setCreatedGroup(group);
      setGroupName("");
      setCreateBanner({
        tone: "success",
        text: "Group created! Share this code with friends.",
      });
      loadMemberships(userId);
    } catch (error: any) {
      setCreateBanner({
        tone: "error",
        text: error?.message || "Failed to create group. Please try again.",
      });
    } finally {
      setCreating(false);
    }
  };

  const handleJoinGroup = async () => {
    if (!joinCode.trim() || joining || !userId) return;
    setJoining(true);
    setJoinBanner(null);
    setCreatedGroup(null);

    try {
      const normalized = joinCode.trim().toLowerCase();
      const res = await joinGroupByCode(normalized, userId);
      setJoinBanner({
        tone: "success",
        text: "You're in! Redirecting you to the chat…",
      });
      loadMemberships(userId);
      setJoinCode("");
      setTimeout(() => {
        router.push(`/g/${res.group_id}`);
      }, 600);
    } catch (error: any) {
      setJoinBanner({
        tone: "error",
        text: error?.message || "Unable to join group. Double-check the code.",
      });
    } finally {
      setJoining(false);
    }
  };

  const openGroup = () => {
    if (createdGroup?.id) {
      router.push(`/g/${createdGroup.id}`);
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
        <section className="rounded-3xl bg-white/90 p-6 shadow-lg shadow-blue-100/70 ring-1 ring-blue-50">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.3em] text-blue-400">
                My groups
              </p>
              <h2 className="text-2xl font-bold text-gray-900">Jump back into a chat</h2>
            </div>
            <button
              onClick={() => userId && loadMemberships(userId)}
              className="rounded-full border border-blue-100 px-4 py-2 text-xs font-semibold text-blue-600 shadow-sm hover:bg-blue-50 disabled:opacity-50"
              disabled={!userId || groupsLoading}
            >
              Refresh
            </button>
          </div>
          <div className="mt-6">
            {groupsLoading ? (
              <p className="text-sm text-gray-500">Loading your groups…</p>
            ) : groupsError ? (
              <p className="rounded-2xl border border-red-100 bg-red-50/80 px-4 py-3 text-sm text-red-600">
                {groupsError}
              </p>
            ) : myGroups.length === 0 ? (
              <p className="text-sm text-gray-500">
                You haven&apos;t joined any groups yet. Create one or enter a code below.
              </p>
            ) : (
              <ul className="grid gap-4 md:grid-cols-2">
                {myGroups.map((group) => (
                  <li
                    key={group.id}
                    className="rounded-2xl border border-blue-50 bg-white/80 p-4 shadow-sm"
                  >
                    <p className="text-sm font-semibold uppercase tracking-[0.3em] text-gray-400">
                      {group.role}
                    </p>
                    <h3 className="mt-1 text-lg font-semibold text-gray-900">{group.name}</h3>
                    <p className="text-xs text-gray-500">
                      Invite code •{" "}
                      <span className="font-semibold tracking-[0.3em] text-blue-500">
                        {group.invite_code.toUpperCase()}
                      </span>
                    </p>
                    <div className="mt-3 flex gap-3">
                      <button
                        onClick={() => router.push(`/g/${group.id}`)}
                        className="flex-1 rounded-full bg-gradient-to-r from-blue-500 to-blue-600 px-4 py-2 text-sm font-semibold text-white shadow hover:scale-[1.01]"
                      >
                        Open chat
                      </button>
                      <button
                        onClick={() =>
                          navigator.clipboard?.writeText(group.invite_code).catch(() => {})
                        }
                        className="rounded-full border border-blue-100 px-4 py-2 text-xs font-semibold text-blue-600 hover:bg-blue-50"
                      >
                        Copy code
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </section>

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
              onKeyDown={(e) => e.key === "Enter" && handleCreateGroup()}
            />
            <button
              className="mt-4 w-full rounded-2xl bg-gradient-to-r from-blue-500 to-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-500/30 transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-60"
              onClick={handleCreateGroup}
              disabled={creating || !groupName.trim() || !authChecked || !userId}
            >
              {creating ? "Creating..." : "Create new group"}
            </button>
            {createBanner && (
              <p
                className={`mt-3 rounded-2xl border px-4 py-3 text-sm ${
                  createBanner.tone === "success"
                    ? "border-blue-100 bg-blue-50/80 text-blue-700"
                    : "border-red-100 bg-red-50/80 text-red-600"
                }`}
              >
                {createBanner.text}
              </p>
            )}
            {createdGroup && (
              <div className="mt-4 rounded-2xl border border-blue-100 bg-blue-50/70 p-4 text-sm text-blue-700">
                <p className="font-semibold">Share this invite code:</p>
                <p className="mt-1 text-2xl tracking-[0.35em]">
                  {createdGroup.invite_code.toUpperCase()}
                </p>
                <div className="mt-3 flex flex-wrap gap-3">
                  <button
                    onClick={() => {
                      if (typeof navigator !== "undefined" && navigator.clipboard) {
                        navigator.clipboard.writeText(createdGroup.invite_code);
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
              onKeyDown={(e) => e.key === "Enter" && handleJoinGroup()}
            />
            <button
              className="mt-4 w-full rounded-2xl bg-gradient-to-r from-orange-400 via-pink-400 to-purple-500 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-orange-200 transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-60"
              onClick={handleJoinGroup}
              disabled={joining || !joinCode.trim() || !authChecked || !userId}
            >
              {joining ? "Joining..." : "Join group"}
            </button>
            {joinBanner && (
              <p
                className={`mt-4 rounded-2xl border p-4 text-sm ${
                  joinBanner.tone === "success"
                    ? "border-orange-100 bg-orange-50/80 text-orange-700"
                    : "border-red-100 bg-red-50/80 text-red-600"
                }`}
              >
                {joinBanner.text}
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
                  body: "Only people with the invite code can join the group.",
                },
                {
                  title: "Summon AI",
                  body: "Type @ai inside any chat to pull in routes, ideas, or places.",
                },
                {
                  title: "Stay in sync",
                  body: "All chats, preferences, and budgets stay in one place for the whole crew.",
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
