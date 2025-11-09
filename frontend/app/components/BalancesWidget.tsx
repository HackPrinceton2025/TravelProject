"use client";

import { useEffect, useState } from "react";
import { getGroupBalances, getGroupMembers, GroupMemberRecord } from "../lib/api";

type Props = {
  groupId: string;
  currentUserId: string;
};

type BalanceData = {
  group_id: string;
  balances: Record<string, number>;
  settlements: { from: string; to: string; amount: string }[];
};

export default function BalancesWidget({ groupId, currentUserId }: Props) {
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [balanceData, setBalanceData] = useState<BalanceData | null>(null);
  const [members, setMembers] = useState<GroupMemberRecord[]>([]);
  const [error, setError] = useState<string | null>(null);

  const getUserName = (userId: string): string => {
    const member = members.find((m) => m.user_id === userId);
    return member?.user_name || member?.user_email || `User ${userId.slice(0, 6)}`;
  };

  const loadBalances = async () => {
    try {
      setLoading(true);
      setError(null);
      const [balances, groupMembers] = await Promise.all([
        getGroupBalances(groupId),
        getGroupMembers(groupId),
      ]);
      setBalanceData(balances);
      setMembers(groupMembers);
    } catch (err) {
      console.error("Failed to load balances", err);
      setError(err instanceof Error ? err.message : "Failed to load balances");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (showModal) {
      loadBalances();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [showModal]);

  if (!showModal) {
    return (
      <button
        onClick={() => setShowModal(true)}
        className="rounded-full border border-green-200 px-4 py-2 text-sm font-semibold text-green-600 shadow-sm transition hover:bg-green-50"
      >
        💰 View balances
      </button>
    );
  }

  const hasBalances = balanceData && Object.keys(balanceData.balances).length > 0;
  const hasSettlements = balanceData && balanceData.settlements.length > 0;
  const allBalancesZero = balanceData && Object.values(balanceData.balances).every((b) => Math.abs(b) < 0.01);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
      <div className="w-full max-w-2xl rounded-3xl bg-white p-6 shadow-xl max-h-[90vh] overflow-y-auto">
        <div className="mb-4 flex items-start justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Group balances</h3>
            <p className="text-sm text-gray-500">See who owes whom and how to settle up</p>
          </div>
          <button
            type="button"
            onClick={() => setShowModal(false)}
            className="rounded-full p-2 text-gray-400 transition hover:bg-gray-100 hover:text-gray-600"
            aria-label="Close balances modal"
          >
            ✕
          </button>
        </div>

        {loading ? (
          <p className="py-6 text-sm text-gray-500">Loading balances…</p>
        ) : error ? (
          <p className="py-6 text-sm text-red-500">{error}</p>
        ) : !hasBalances || allBalancesZero ? (
          <p className="py-6 text-sm text-gray-500">No expenses recorded yet. All balances are settled!</p>
        ) : (
          <div className="space-y-6">
            {/* Individual Balances */}
            <div>
              <h4 className="mb-3 text-sm font-semibold text-gray-700">Individual balances</h4>
              <div className="space-y-2">
                {balanceData &&
                  Object.entries(balanceData.balances).map(([userId, balance]) => {
                    const isCurrentUser = userId === currentUserId;
                    const isOwed = balance > 0;
                    const owes = balance < 0;
                    const isEven = Math.abs(balance) < 0.01;

                    if (isEven) return null;

                    return (
                      <div
                        key={userId}
                        className={`rounded-lg border px-4 py-3 text-sm ${
                          isCurrentUser
                            ? "border-blue-300 bg-blue-50"
                            : "border-gray-200 bg-gray-50"
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-medium text-gray-700">{getUserName(userId)}</span>
                          <span
                            className={`font-semibold ${
                              isOwed ? "text-green-600" : "text-red-600"
                            }`}
                          >
                            {isOwed
                              ? `+$${Math.abs(balance).toFixed(2)}`
                              : `-$${Math.abs(balance).toFixed(2)}`}
                          </span>
                        </div>
                        <p className="mt-1 text-xs text-gray-500">
                          {isOwed
                            ? "Others owe this amount"
                            : "Owes this amount to others"}
                        </p>
                      </div>
                    );
                  })}
              </div>
            </div>

            {/* Settlement Plan */}
            {hasSettlements && balanceData.settlements.length > 0 && (
              <div>
                <h4 className="mb-3 text-sm font-semibold text-gray-700">Settlement plan</h4>
                <p className="mb-3 text-xs text-gray-500">
                  To settle all debts, make these payments:
                </p>
                <div className="space-y-2">
                  {balanceData.settlements.map((settlement, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between rounded-lg border border-purple-200 bg-purple-50 px-4 py-3 text-sm"
                    >
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-gray-700">
                          {getUserName(settlement.from)}
                        </span>
                        <span className="text-gray-400">→</span>
                        <span className="font-medium text-gray-700">
                          {getUserName(settlement.to)}
                        </span>
                      </div>
                      <span className="font-semibold text-purple-600">
                        ${parseFloat(settlement.amount).toFixed(2)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {!hasSettlements && (
              <p className="py-2 text-sm text-gray-500">All balances are settled!</p>
            )}
          </div>
        )}

        <div className="mt-6 flex items-center justify-end gap-3">
          <button
            type="button"
            onClick={() => setShowModal(false)}
            className="rounded-full border border-gray-200 px-4 py-2 text-sm font-semibold text-gray-600 hover:bg-gray-50"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

