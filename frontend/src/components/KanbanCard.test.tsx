import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi, describe, it, expect, beforeEach } from "vitest";
import { KanbanCard } from "@/components/KanbanCard";

describe("KanbanCard", () => {
  const mockCard = {
    id: "card-1",
    title: "Test Card",
    details: "Test details",
  };

  const mockOnDelete = vi.fn();
  const mockOnEdit = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders card with title and details", () => {
    render(
      <KanbanCard
        card={mockCard}
        onDelete={mockOnDelete}
        onEdit={mockOnEdit}
      />
    );

    expect(screen.getByText("Test Card")).toBeInTheDocument();
    expect(screen.getByText("Test details")).toBeInTheDocument();
  });

  it("enters edit mode on double-click", async () => {
    render(
      <KanbanCard
        card={mockCard}
        onDelete={mockOnDelete}
        onEdit={mockOnEdit}
      />
    );

    const cardElement = screen.getByText("Test Card").closest("div");
    await userEvent.dblClick(cardElement!);

    expect(screen.getByDisplayValue("Test Card")).toBeInTheDocument();
    expect(screen.getByDisplayValue("Test details")).toBeInTheDocument();
  });

  it("saves changes on Enter key", async () => {
    render(
      <KanbanCard
        card={mockCard}
        onDelete={mockOnDelete}
        onEdit={mockOnEdit}
      />
    );

    const cardElement = screen.getByText("Test Card").closest("div");
    await userEvent.dblClick(cardElement!);

    const titleInput = screen.getByDisplayValue("Test Card");
    await userEvent.clear(titleInput);
    await userEvent.type(titleInput, "Updated Card");
    await userEvent.keyboard("{Enter}");

    expect(mockOnEdit).toHaveBeenCalledWith("card-1", "Updated Card", "Test details");
  });

  it("cancels edit mode on Escape", async () => {
    render(
      <KanbanCard
        card={mockCard}
        onDelete={mockOnDelete}
        onEdit={mockOnEdit}
      />
    );

    const cardElement = screen.getByText("Test Card").closest("div");
    await userEvent.dblClick(cardElement!);

    const titleInput = screen.getByDisplayValue("Test Card");
    await userEvent.clear(titleInput);
    await userEvent.type(titleInput, "Updated Card");
    await userEvent.keyboard("{Escape}");

    expect(screen.queryByDisplayValue("Updated Card")).not.toBeInTheDocument();
    expect(screen.getByText("Test Card")).toBeInTheDocument();
  });

  it("deletes card on remove button click", async () => {
    render(
      <KanbanCard
        card={mockCard}
        onDelete={mockOnDelete}
        onEdit={mockOnEdit}
      />
    );

    const removeButton = screen.getByLabelText(`Delete ${mockCard.title}`);
    await userEvent.click(removeButton);

    expect(mockOnDelete).toHaveBeenCalledWith("card-1");
  });
});
