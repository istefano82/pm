"use client";

import { useState, useRef, useEffect } from "react";
import clsx from "clsx";
import { BoardData } from "@/lib/kanban";
import * as api from "@/lib/api";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
};

type AISidebarProps = {
  board: BoardData | null;
  onBoardUpdate: (board: BoardData) => void;
};

export const AISidebar = ({ board, onBoardUpdate }: AISidebarProps) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || !board || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await api.queryAI(input);

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.response,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Apply updates and refresh board
      if (response.updates && response.updates.length > 0 && response.board) {
        onBoardUpdate(response.board);
      }
    } catch (error) {
      console.error("AI query failed:", error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Sorry, I encountered an error. Please try again.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* Floating toggle button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={clsx(
          "fixed right-6 bottom-6 rounded-full p-4 font-semibold text-white shadow-lg transition-all z-40",
          isOpen ? "bg-[var(--secondary-purple)] hover:opacity-90" : "bg-[var(--primary-blue)] hover:opacity-90"
        )}
        aria-label="Toggle AI chat"
      >
        {isOpen ? "✕" : "✨"}
      </button>

      {/* Sidebar panel */}
      <aside
        className={clsx(
          "fixed right-0 top-0 h-full w-96 bg-white shadow-xl transition-transform duration-300 z-50 flex flex-col border-l border-[var(--stroke)]",
          isOpen ? "translate-x-0" : "translate-x-full"
        )}
      >
        {/* Header */}
        <div className="border-b border-[var(--stroke)] bg-gradient-to-r from-[var(--primary-blue)] to-[var(--secondary-purple)] px-6 py-6 text-white">
          <h2 className="font-display text-lg font-semibold">AI Assistant</h2>
          <p className="mt-1 text-sm opacity-90">Ask me to manage your cards</p>
        </div>

        {/* Messages container */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 ? (
            <div className="flex h-full items-center justify-center text-center">
              <div>
                <p className="text-sm text-[var(--gray-text)]">
                  Start by asking me to create, move, or edit cards. For example:
                </p>
                <ul className="mt-3 space-y-2 text-xs text-[var(--gray-text)]">
                  <li className="rounded-lg bg-[var(--surface)] p-2">
                    "Create a card called Deploy to staging"
                  </li>
                  <li className="rounded-lg bg-[var(--surface)] p-2">
                    "Move the Deploy card to In Progress"
                  </li>
                  <li className="rounded-lg bg-[var(--surface)] p-2">
                    "Delete the old task card"
                  </li>
                </ul>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={clsx(
                    "flex gap-3",
                    message.role === "user" ? "justify-end" : "justify-start"
                  )}
                >
                  {message.role === "assistant" && (
                    <div className="h-8 w-8 rounded-full bg-[var(--primary-blue)] flex items-center justify-center text-white text-xs font-semibold flex-shrink-0">
                      AI
                    </div>
                  )}
                  <div
                    className={clsx(
                      "max-w-xs rounded-lg px-4 py-2 text-sm",
                      message.role === "user"
                        ? "bg-[var(--primary-blue)] text-white"
                        : "bg-[var(--surface)] text-[var(--navy-dark)]"
                    )}
                  >
                    {message.content}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start gap-3">
                  <div className="h-8 w-8 rounded-full bg-[var(--primary-blue)] flex items-center justify-center text-white text-xs font-semibold flex-shrink-0">
                    AI
                  </div>
                  <div className="rounded-lg bg-[var(--surface)] px-4 py-2">
                    <div className="flex gap-1">
                      <div className="h-2 w-2 rounded-full bg-[var(--primary-blue)] animate-bounce" />
                      <div className="h-2 w-2 rounded-full bg-[var(--primary-blue)] animate-bounce delay-100" />
                      <div className="h-2 w-2 rounded-full bg-[var(--primary-blue)] animate-bounce delay-200" />
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input area */}
        <div className="border-t border-[var(--stroke)] bg-white p-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="Ask me something..."
              disabled={isLoading || !board}
              className="flex-1 rounded-lg border border-[var(--stroke)] px-3 py-2 text-sm outline-none focus:border-[var(--primary-blue)] disabled:bg-[var(--surface)] disabled:text-[var(--gray-text)]"
            />
            <button
              onClick={handleSend}
              disabled={isLoading || !board || !input.trim()}
              className="rounded-lg bg-[var(--secondary-purple)] px-4 py-2 text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Send
            </button>
          </div>
        </div>
      </aside>
    </>
  );
};
