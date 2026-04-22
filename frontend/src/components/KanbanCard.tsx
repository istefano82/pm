"use client";

import { useState } from "react";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import clsx from "clsx";
import type { Card } from "@/lib/kanban";

type KanbanCardProps = {
  card: Card;
  onDelete: (cardId: string) => void;
  onEdit: (cardId: string, title: string, details: string) => void;
};

export const KanbanCard = ({ card, onDelete, onEdit }: KanbanCardProps) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(card.title);
  const [editDetails, setEditDetails] = useState(card.details);

  const { attributes, listeners, setNodeRef, transform, transition, isDragging } =
    useSortable({ id: card.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  const handleSave = () => {
    if (!editTitle.trim()) return;
    onEdit(card.id, editTitle.trim(), editDetails.trim());
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditTitle(card.title);
    setEditDetails(card.details);
    setIsEditing(false);
  };

  const stopDrag = (e: React.PointerEvent) => e.stopPropagation();

  return (
    <article
      ref={setNodeRef}
      style={style}
      className={clsx(
        "rounded-2xl border border-transparent bg-white px-4 py-4 shadow-[0_12px_24px_rgba(3,33,71,0.08)]",
        "transition-all duration-150",
        isDragging && "opacity-60 shadow-[0_18px_32px_rgba(3,33,71,0.16)]"
      )}
      {...attributes}
      {...listeners}
      data-testid={`card-${card.id}`}
    >
      {isEditing ? (
        <div onPointerDown={stopDrag} className="flex flex-col gap-2">
          <input
            autoFocus
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleSave();
              if (e.key === "Escape") handleCancel();
            }}
            className="w-full rounded-lg border border-[var(--stroke)] px-3 py-1.5 font-display text-sm font-semibold text-[var(--navy-dark)] outline-none focus:border-[var(--primary-blue)]"
            placeholder="Card title"
          />
          <textarea
            value={editDetails}
            onChange={(e) => setEditDetails(e.target.value)}
            onKeyDown={(e) => e.key === "Escape" && handleCancel()}
            rows={2}
            className="w-full resize-none rounded-lg border border-[var(--stroke)] px-3 py-1.5 text-sm text-[var(--gray-text)] outline-none focus:border-[var(--primary-blue)]"
            placeholder="Details"
          />
          <div className="flex gap-2">
            <button
              type="button"
              onClick={handleSave}
              className="rounded-lg bg-[var(--secondary-purple)] px-3 py-1 text-xs font-semibold text-white transition hover:bg-opacity-90"
            >
              Save
            </button>
            <button
              type="button"
              onClick={handleCancel}
              className="rounded-lg border border-[var(--stroke)] px-3 py-1 text-xs font-semibold text-[var(--gray-text)] transition hover:text-[var(--navy-dark)]"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <div className="flex items-start justify-between gap-3">
          <div
            className="min-w-0 flex-1 cursor-default"
            onDoubleClick={(e) => {
              e.stopPropagation();
              setEditTitle(card.title);
              setEditDetails(card.details);
              setIsEditing(true);
            }}
            onPointerDown={stopDrag}
            title="Double-click to edit"
          >
            <h4 className="font-display text-base font-semibold text-[var(--navy-dark)]">
              {card.title}
            </h4>
            {card.details && (
              <p className="mt-2 text-sm leading-6 text-[var(--gray-text)]">
                {card.details}
              </p>
            )}
          </div>
          <button
            type="button"
            onPointerDown={stopDrag}
            onClick={() => onDelete(card.id)}
            className="shrink-0 rounded-full border border-transparent px-2 py-1 text-xs font-semibold text-[var(--gray-text)] transition hover:border-[var(--stroke)] hover:text-[var(--navy-dark)]"
            aria-label={`Delete ${card.title}`}
          >
            Remove
          </button>
        </div>
      )}
    </article>
  );
};
