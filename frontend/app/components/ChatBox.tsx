"use client";

import { useState } from "react";

export default function ChatBox() {
  const [message, setMessage] = useState("");
  const send = () => {
    setMessage("");
  };
  return (
    <div className="flex gap-2">
      <input
        className="flex-1 bg-gray-800 border border-gray-700 rounded px-3 py-2"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Type a message"
      />
      <button className="bg-blue-600 px-4 py-2 rounded" onClick={send}>
        Send
      </button>
    </div>
  );
}


