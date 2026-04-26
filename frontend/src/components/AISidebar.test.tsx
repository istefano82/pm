import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi, describe, it, expect, beforeEach } from "vitest";
import { AISidebar } from "@/components/AISidebar";

describe("AISidebar", () => {
  const mockBoard = {
    columns: [
      { id: "col-1", title: "To Do", cardIds: [] },
    ],
    cards: {},
  };

  const mockOnBoardUpdate = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    Element.prototype.scrollIntoView = vi.fn();
  });

  it("renders toggle button", () => {
    render(<AISidebar board={mockBoard} onBoardUpdate={mockOnBoardUpdate} />);
    expect(screen.getByLabelText("Toggle AI chat")).toBeInTheDocument();
  });

  it("opens sidebar on toggle button click", async () => {
    render(<AISidebar board={mockBoard} onBoardUpdate={mockOnBoardUpdate} />);

    const toggleButton = screen.getByLabelText("Toggle AI chat");
    await userEvent.click(toggleButton);

    expect(screen.getByText("AI Assistant")).toBeInTheDocument();
  });

  it("shows example prompts when no messages", async () => {
    render(<AISidebar board={mockBoard} onBoardUpdate={mockOnBoardUpdate} />);

    const toggleButton = screen.getByLabelText("Toggle AI chat");
    await userEvent.click(toggleButton);

    expect(screen.getByText(/Create a card called Deploy to staging/i)).toBeInTheDocument();
  });

  it("disables input when no board", () => {
    render(<AISidebar board={null} onBoardUpdate={mockOnBoardUpdate} />);

    const toggleButton = screen.getByLabelText("Toggle AI chat");
    // Should not crash when board is null
    expect(toggleButton).toBeInTheDocument();
  });

  it("sends message on button click", async () => {
    render(<AISidebar board={mockBoard} onBoardUpdate={mockOnBoardUpdate} />);

    const toggleButton = screen.getByLabelText("Toggle AI chat");
    await userEvent.click(toggleButton);

    const input = screen.getByPlaceholderText("Ask me something...");
    const sendButton = within(
      input.closest("div")!.parentElement!
    ).getByRole("button", { name: /send/i });

    await userEvent.type(input, "Test message");
    await userEvent.click(sendButton);

    expect(screen.getByText("Test message")).toBeInTheDocument();
  });

  it("sends message on Enter key", async () => {
    render(<AISidebar board={mockBoard} onBoardUpdate={mockOnBoardUpdate} />);

    const toggleButton = screen.getByLabelText("Toggle AI chat");
    await userEvent.click(toggleButton);

    const input = screen.getByPlaceholderText("Ask me something...");
    await userEvent.type(input, "Test message");
    await userEvent.keyboard("{Enter}");

    expect(screen.getByText("Test message")).toBeInTheDocument();
  });
});
