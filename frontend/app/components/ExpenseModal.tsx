"use client";

import { useEffect, useMemo, useState } from "react";
import {
  createExpense,
  getGroupMembers,
  ExpenseParticipant,
  ExpensePayload,
  GroupMemberRecord,
} from "../lib/api";

export type ExpenseRecordedInfo = {
  expenseId: string;
  amount: number;
  description?: string;
  payerId: string;
  payerLabel: string;
  participantIds: string[];
};

type Props = {
  groupId: string;
  currentUserId: string;
  currentUserName?: string | null;
  onClose: () => void;
  onExpenseRecorded?: (info: ExpenseRecordedInfo) => void;
};

type ParticipantSelection = {
  user_id: string;
  label: string;
  selected: boolean;
};

const getDisplayName = (member: GroupMemberRecord, fallbackUserId: string): string => {
  // Prefer user_name, fall back to user_email, then to a short ID
  return member.user_name || member.user_email || `User ${fallbackUserId.slice(0, 6)}`;
};

export default function ExpenseModal({
  groupId,
  currentUserId,
  currentUserName,
  onClose,
  onExpenseRecorded,
}: Props) {
  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");
  const [participants, setParticipants] = useState<ParticipantSelection[]>([]);
  const [payerId, setPayerId] = useState(currentUserId);
  const [splitMode, setSplitMode] = useState<"everyone" | "selected">("everyone");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadMembers = async () => {
      try {
        setLoading(true);
        const members = await getGroupMembers(groupId);
        const seen = new Set<string>();
        const mapped: ParticipantSelection[] = members.map((m: GroupMemberRecord) => {
          seen.add(m.user_id);
          return {
            user_id: m.user_id,
            label: getDisplayName(m, m.user_id),
            selected: true,
          };
        });
        // If current user is not in the members list, add them
        if (!seen.has(currentUserId)) {
          // Use provided currentUserName or fall back to email or ID
          const currentUserLabel = currentUserName || `User ${currentUserId.slice(0, 6)}`;
          mapped.push({
            user_id: currentUserId,
            label: currentUserLabel,
            selected: true,
          });
        }
        setParticipants(mapped);
        setPayerId(currentUserId);
      } catch (err) {
        console.error("Failed to load group members", err);
        setError("Failed to load group members. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    loadMembers();
  }, [groupId, currentUserId]);

  const selectedCount = useMemo(
    () => participants.filter((p) => p.selected).length,
    [participants],
  );

  const handleToggleParticipant = (userId: string) => {
    setParticipants((prev) =>
      prev.map((p) =>
        p.user_id === userId
          ? {
              ...p,
              selected: !p.selected,
            }
          : p,
      ),
    );
  };

  const handleSplitModeChange = (mode: "everyone" | "selected") => {
    setSplitMode(mode);
    if (mode === "everyone") {
      // Select everyone when "Everyone" is chosen
      setParticipants((prev) => prev.map((p) => ({ ...p, selected: true })));
    }
  };

  const resetState = () => {
    setDescription("");
    setAmount("");
    setSplitMode("everyone");
    setError(null);
    setParticipants((prev) => prev.map((p) => ({ ...p, selected: true })));
    setPayerId(currentUserId);
  };

  const handleSubmit = async () => {
    setError(null);
    const numericAmount = parseFloat(amount);
    if (!numericAmount || numericAmount <= 0) {
      setError("Please enter a valid amount greater than zero.");
      return;
    }

    const selectedParticipants = participants.filter((p) => p.selected);
    if (selectedParticipants.length === 0) {
      setError("Select at least one participant to split the expense.");
      return;
    }

    // Always split equally - backend will calculate shares automatically
    const splitBetween: ExpenseParticipant[] = selectedParticipants.map((p) => ({ user_id: p.user_id }));

    const payload: ExpensePayload = {
      group_id: groupId,
      payer_id: payerId,
      amount: numericAmount,
      description: description.trim() || undefined,
      split_between: splitBetween,
    };

    try {
      setSubmitting(true);
      const res = await createExpense(payload);
      onExpenseRecorded?.({
        expenseId: res.expense_id,
        amount: numericAmount,
        description: payload.description,
        payerId,
        payerLabel: participants.find((p) => p.user_id === payerId)?.label || `User ${payerId.slice(0, 6)}`,
        participantIds: selectedParticipants.map((p) => p.user_id),
      });
      resetState();
      onClose();
    } catch (err) {
      console.error("Failed to create expense", err);
      setError(err instanceof Error ? err.message : "Failed to create expense. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
      <div className="w-full max-w-xl rounded-3xl bg-white p-6 shadow-xl">
        <div className="mb-4 flex items-start justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Add group expense</h3>
            <p className="text-sm text-gray-500">Log a shared cost and split it among tripmates.</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-full p-2 text-gray-400 transition hover:bg-gray-100 hover:text-gray-600"
            aria-label="Close expense modal"
          >
            ✕
          </button>
        </div>

        {loading ? (
          <p className="py-6 text-sm text-gray-500">Loading group members…</p>
        ) : (
          <div className="space-y-5">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">Description</label>
              <input
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none"
                placeholder="e.g., Dinner at The Mill"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">Amount (USD)</label>
              <input
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none"
                placeholder="e.g., 120.00"
                value={amount}
                onChange={(e) => {
                  const value = e.target.value;
                  if (/^\d*(\.\d{0,2})?$/.test(value)) setAmount(value);
                }}
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">Paid by</label>
              <select
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none"
                value={payerId}
                onChange={(e) => setPayerId(e.target.value)}
              >
                {participants.map((p) => (
                  <option key={p.user_id} value={p.user_id}>
                    {p.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">Split equally by</label>
              <div className="flex items-center gap-4 text-sm">
                <label className="flex items-center gap-2">
                  <input
                    type="radio"
                    name="split-mode"
                    checked={splitMode === "everyone"}
                    onChange={() => handleSplitModeChange("everyone")}
                  />
                  Everyone
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="radio"
                    name="split-mode"
                    checked={splitMode === "selected"}
                    onChange={() => handleSplitModeChange("selected")}
                  />
                  Selected people
                </label>
              </div>
            </div>

            {splitMode === "selected" && (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-semibold text-gray-700">Select participants</span>
                  <span className="text-xs text-gray-500">{selectedCount} selected</span>
                </div>
                <div className="grid gap-2 md:grid-cols-2">
                  {participants.map((participant) => (
                    <div
                      key={participant.user_id}
                      className={`rounded-lg border px-3 py-2 text-sm transition ${
                        participant.selected ? "border-blue-200 bg-blue-50" : "border-gray-200"
                      }`}
                    >
                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={participant.selected}
                          onChange={() => handleToggleParticipant(participant.user_id)}
                        />
                        <span className="font-medium text-gray-700">{participant.label}</span>
                      </label>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {error && <p className="text-sm text-red-500">{error}</p>}

            <div className="flex items-center justify-end gap-3">
              <button
                type="button"
                onClick={onClose}
                className="rounded-full border border-gray-200 px-4 py-2 text-sm font-semibold text-gray-600 hover:bg-gray-50"
                disabled={submitting}
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleSubmit}
                disabled={submitting}
                className="rounded-full bg-gradient-to-r from-blue-500 to-indigo-500 px-5 py-2 text-sm font-semibold text-white shadow hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {submitting ? "Saving…" : "Save expense"}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
