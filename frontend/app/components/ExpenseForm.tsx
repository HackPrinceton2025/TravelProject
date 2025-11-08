"use client";

import { useState } from "react";

export default function ExpenseForm() {
  const [amount, setAmount] = useState("");
  const [desc, setDesc] = useState("");
  const submit = () => {
    setAmount("");
    setDesc("");
  };
  return (
    <div className="border border-gray-700 rounded p-4 space-y-2">
      <h3 className="font-semibold">Add Expense</h3>
      <input
        className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
        placeholder="Description"
        value={desc}
        onChange={(e) => setDesc(e.target.value)}
      />
      <input
        className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
        placeholder="Amount"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
      />
      <button className="bg-green-600 px-4 py-2 rounded" onClick={submit}>
        Save
      </button>
    </div>
  );
}


