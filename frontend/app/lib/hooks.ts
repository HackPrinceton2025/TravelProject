"use client";

import { create } from "zustand";

type Message = { id: string; sender: string; content: string };

type Store = {
  messages: Message[];
  addMessage: (m: Message) => void;
  clear: () => void;
};

export const useChatStore = create<Store>((set) => ({
  messages: [],
  addMessage: (m) => set((s) => ({ messages: [...s.messages, m] })),
  clear: () => set({ messages: [] }),
}));


