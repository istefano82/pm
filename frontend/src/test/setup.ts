import "@testing-library/jest-dom";
import { vi } from "vitest";

// Mock API module
vi.mock("@/lib/api", () => ({
  fetchBoard: vi.fn(async () => ({
    columns: [
      { id: "col-1", title: "To Do", cardIds: ["1", "2"] },
      { id: "col-2", title: "In Progress", cardIds: ["3"] },
      { id: "col-3", title: "Review", cardIds: ["4"] },
      { id: "col-4", title: "Testing", cardIds: [] },
      { id: "col-5", title: "Done", cardIds: [] },
    ],
    cards: {
      "1": { id: "1", title: "Task 1", details: "Details 1" },
      "2": { id: "2", title: "Task 2", details: "Details 2" },
      "3": { id: "3", title: "Task 3", details: "Details 3" },
      "4": { id: "4", title: "Task 4", details: "Details 4" },
    },
  })),
  createCard: vi.fn(async () => ({})),
  updateCard: vi.fn(async () => ({})),
  deleteCard: vi.fn(async () => ({})),
  moveCard: vi.fn(async () => ({})),
  renameColumn: vi.fn(async () => ({})),
  queryAI: vi.fn(async () => ({ response: "OK", updates: [], board: null })),
}));

// Mock session module
vi.mock("@/lib/session", () => ({
  getAuthToken: vi.fn(() => "mock-token"),
  setAuthToken: vi.fn(),
  clearAuthToken: vi.fn(),
}));
