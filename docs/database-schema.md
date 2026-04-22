# Kanban Database Schema

This document defines the SQLite database schema for the Project Management MVP.

## Overview

The schema supports a multi-user system with multiple boards per user, columns within boards, and cards within columns. The MVP uses hardcoded authentication, but the schema is structured to support proper user management in future versions.

## Tables

### users
Stores user accounts.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | |
| username | TEXT | UNIQUE NOT NULL | |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | |

**Notes**: No password column — MVP authentication is handled in FastAPI with hardcoded credentials. Future versions will add password_hash.

### boards
Stores Kanban boards, one per user.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | |
| user_id | INTEGER | NOT NULL, FK → users.id | Board owner |
| title | TEXT | NOT NULL | Board name |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | |

**Notes**: MVP restricts to 1 board per user, but schema allows multiple boards for future expansion.

### columns
Stores board columns (e.g., "To Do", "In Progress", "Done").

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | |
| board_id | INTEGER | NOT NULL, FK → boards.id | Parent board |
| title | TEXT | NOT NULL | Column name |
| position | INTEGER | NOT NULL | Order within board (0-indexed) |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | |

**Notes**: Columns are fixed in MVP (not user-deletable), but can be renamed. Position allows reordering without linked-list complexity.

### cards
Stores individual cards/tasks within columns.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | |
| column_id | INTEGER | NOT NULL, FK → columns.id | Parent column |
| title | TEXT | NOT NULL | Card title |
| details | TEXT | DEFAULT '' | Card description |
| position | INTEGER | NOT NULL | Order within column (0-indexed) |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | |

**Notes**: Cards can be moved between columns via drag-and-drop.

## Relationships

```
users (1) ──── (N) boards
              │
              └──(1) ──── (N) columns
                          │
                          └──(1) ──── (N) cards
```

## Initial Data

For MVP testing, the system creates:
- 1 user: username="user"
- 1 board: title="My Project"
- 5 columns: "To Do", "In Progress", "Review", "Testing", "Done"
- 8 sample cards distributed across columns

## Notes for Implementation

- **No migrations**: SQLAlchemy's `create_all()` will create tables on first run. The database file is created automatically if it doesn't exist.
- **Position ordering**: Use integer positions (0, 1, 2, ...) to order items within their parent. When moving a card, update positions of affected cards in O(n) time.
- **No soft deletes**: Deleted items are fully removed (suitable for MVP).
- **No audit trail**: No updated_at or modified_by columns (can be added later if needed).
