# Frontend AGENTS.md

This describes the existing frontend code for the Kanban board demo.

## Overview

The frontend is a NextJS 16 application with React 19, TypeScript, and TailwindCSS. It implements a demo Kanban board with drag-and-drop functionality using @dnd-kit. The app is a pure frontend demo, not yet integrated with a backend.

## Key Components

- **KanbanBoard** (`src/components/KanbanBoard.tsx`): Main component that manages the board state (columns and cards) in local state. Handles drag-and-drop events using @dnd-kit, including drag start/end, column renaming, adding/deleting cards. Renders the header with board info and the grid of columns.

- **KanbanColumn** (`src/components/KanbanColumn.tsx`): Represents each column. Uses @dnd-kit's droppable and sortable contexts. Displays column title (editable), card count, list of cards, and a form to add new cards. Shows "Drop a card here" placeholder when empty.

- **KanbanCard** (`src/components/KanbanCard.tsx`): Individual card component, sortable within columns. Displays title and details, with a delete button.

- **KanbanCardPreview** (`src/components/KanbanCardPreview.tsx`): Simplified card view used in the drag overlay.

- **NewCardForm** (`src/components/NewCardForm.tsx`): Form to add new cards to a column, with title and details inputs.

## Library

- **kanban.ts** (`src/lib/kanban.ts`): Defines types (Card, Column, BoardData), provides initial demo data with 5 columns and 8 cards, and implements the `moveCard` function for handling drag-and-drop logic (reordering within column or moving between columns). Also includes `createId` for generating unique IDs.

## Tests

- **kanban.test.ts**: Unit tests for the `moveCard` function using Vitest, covering reordering and moving cards.

- **KanbanBoard.test.tsx**: Component tests for KanbanBoard, likely testing rendering and interactions.

- E2E tests in `tests/kanban.spec.ts` using Playwright.

## Configuration

- **package.json**: Scripts for dev, build, start, lint, test (unit with Vitest, e2e with Playwright).

- **next.config.ts**: NextJS configuration.

- **tailwindcss**: For styling, with custom CSS variables for colors matching the scheme.

- **eslint.config.mjs**: Linting configuration.

- **vitest.config.ts**: Unit testing config with coverage.

- **playwright.config.ts**: E2E testing config.

## Pages

- **page.tsx** (`src/app/page.tsx`): Simple page that renders the KanbanBoard component.

The code follows the coding standards: latest versions, simple and concise, no unnecessary features.