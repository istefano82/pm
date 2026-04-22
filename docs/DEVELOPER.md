# Developer Guide - Project Management MVP

## Overview

Project Management MVP is a full-stack web application for managing tasks on a Kanban board with AI-powered assistance. The app consists of:
- **Frontend**: Next.js 16 with React 19, TypeScript, TailwindCSS
- **Backend**: Python FastAPI with SQLAlchemy 2.0, SQLite
- **AI Integration**: OpenRouter API using gpt-oss-120b:free model
- **Deployment**: Docker containerization

## Project Structure

```
pm/
├── frontend/                 # Next.js frontend app
│   ├── src/
│   │   ├── app/             # Next.js app router
│   │   │   ├── page.tsx      # Home/Kanban page
│   │   │   └── login/        # Login page
│   │   ├── components/       # React components
│   │   │   ├── KanbanBoard.tsx
│   │   │   ├── KanbanColumn.tsx
│   │   │   ├── KanbanCard.tsx
│   │   │   ├── AISidebar.tsx
│   │   │   └── ...
│   │   └── lib/              # Utilities
│   │       ├── api.ts        # API client functions
│   │       ├── kanban.ts     # Kanban logic
│   │       └── session.ts    # Auth token management
│   ├── package.json
│   ├── next.config.ts        # Static export config
│   └── tailwind.config.ts
│
├── backend/                  # FastAPI backend
│   ├── src/backend/
│   │   ├── main.py           # FastAPI app & routes
│   │   ├── models.py         # SQLAlchemy models
│   │   ├── database.py       # DB setup
│   │   └── ai.py             # OpenRouter AI client
│   ├── tests/                # Unit tests
│   ├── pyproject.toml        # uv dependencies
│   ├── uv.lock
│   └── Dockerfile
│
├── docs/
│   ├── PLAN.md              # Project plan (all 10 parts)
│   ├── database-schema.md   # Database design
│   └── DEVELOPER.md         # This file
│
├── scripts/
│   ├── start.sh             # Linux/Mac start script
│   ├── stop.sh
│   ├── start.bat            # Windows batch scripts
│   └── stop.bat
│
├── docker-compose.yml       # Docker compose config
├── Dockerfile               # Multi-stage Docker build
├── CLAUDE.md                # Project requirements
└── .env                     # Environment variables (OpenRouter API key)
```

## Key Technologies

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | Next.js | 16.1.6 |
| Frontend Framework | React | 19 |
| Frontend Styling | TailwindCSS | 3.x |
| Frontend Drag-Drop | @dnd-kit | latest |
| Backend Framework | FastAPI | 0.115.0+ |
| Backend Server | Uvicorn | 0.32.0+ |
| ORM | SQLAlchemy | 2.0+ |
| Database | SQLite | (file-based) |
| AI API | OpenRouter | openai/gpt-oss-120b:free |
| Python Version | 3.10+ | |
| Node.js | 20+ | (20.0.0 for Next.js 16) |
| Package Manager (Python) | uv | latest |

## Development Setup

### Prerequisites

- **Node.js** v20+ (check with `node --version`)
- **Python** 3.10+ (check with `python3 --version`)
- **uv** package manager for Python (install with `pip install uv`)
- **Git**

### Environment Variables

Create a `.env` file in the project root:

```bash
OPENROUTER_API_KEY=sk-or-v1-xxx...
```

Get an API key from https://openrouter.ai/keys (free tier available for gpt-oss-120b:free).

### Frontend Development

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Run dev server** (port 3000):
   ```bash
   npm run dev
   ```
   Visit http://localhost:3000

3. **Build for production**:
   ```bash
   npm run build
   # Output: frontend/out/ (static files)
   ```

4. **Run tests**:
   ```bash
   npm run test         # Unit tests (Vitest)
   npm run test:e2e     # E2E tests (Playwright)
   ```

### Backend Development

1. **Set up virtual environment**:
   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies** (using uv):
   ```bash
   uv sync
   ```

3. **Run dev server** (port 8000):
   ```bash
   uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000
   ```
   Visit http://localhost:8000/api/health

4. **Run tests**:
   ```bash
   pytest
   ```

### Full Stack Development

Run frontend and backend in parallel:

```bash
# Terminal 1: Backend
cd backend
source .venv/bin/activate
uvicorn src.backend.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

Then visit http://localhost:3000. The frontend will proxy API calls to http://localhost:8000.

**Login credentials** (hardcoded for MVP):
- Username: `user`
- Password: `password`

## Docker Setup

### Prerequisites

- Docker (check with `docker --version`)
- Docker Compose (check with `docker-compose --version`)

### Build and Run

1. **Build the Docker image**:
   ```bash
   docker build -t pm-mvp .
   ```

2. **Run with docker-compose**:
   ```bash
   docker-compose up -d
   ```
   App runs on http://localhost:8000

3. **Stop the container**:
   ```bash
   docker-compose down
   ```

### What Happens in Docker

The multi-stage Dockerfile:
1. Builds the frontend (Next.js → static files in `out/`)
2. Sets up the Python backend with uv
3. Copies static files to backend serving directory
4. Runs FastAPI on port 8000

The `docker-compose.yml` binds port 8000 and mounts the database file for persistence.

### Database Persistence

SQLite database file: `kanban.db` (created on first run)

In Docker, it persists in a volume. Locally, it's in the backend directory.

## API Endpoints

### Authentication
- `POST /api/login` - Login with hardcoded credentials, get token
- `POST /api/logout` - Invalidate token
- `GET /api/verify` - Check if token is valid

### Kanban Board
- `GET /api/board` - Get full board state (columns + cards)
- `PUT /api/columns/{id}` - Rename column
- `POST /api/cards` - Create card
- `PUT /api/cards/{id}` - Edit card title/details
- `DELETE /api/cards/{id}` - Delete card
- `PUT /api/cards/{id}/move` - Move card to column/position

### AI
- `POST /api/ai/test` - Test AI endpoint (returns "4" for "2+2")
- `POST /api/ai/query` - Chat with AI, get response + optional board updates

All endpoints (except login/logout) require `Authorization: Bearer <token>` header.

## Frontend Architecture

### State Management

**Local State** (React useState):
- Board data (columns, cards)
- Drag state (activeCardId)
- Chat sidebar (messages, input)

**No Redux/Context needed** for MVP (centralized state in KanbanBoard component).

### Key Components

- **KanbanBoard**: Main container, fetches board, handles drag events
- **KanbanColumn**: Column with droppable area, editable title
- **KanbanCard**: Card with draggable sorting, editable title/details
- **AISidebar**: Floating chat sidebar, integrates with AI API
- **AuthGuard**: Redirects to login if not authenticated

### API Client (lib/api.ts)

All API functions are in one module:
- `fetchBoard()` - GET /api/board
- `createCard(columnId, title, details)` - POST /api/cards
- `updateCard(id, title, details)` - PUT /api/cards/{id}
- `deleteCard(id)` - DELETE /api/cards/{id}
- `moveCard(id, columnId, position)` - PUT /api/cards/{id}/move
- `renameColumn(id, title)` - PUT /api/columns/{id}
- `queryAI(question)` - POST /api/ai/query

All functions handle Bearer token injection automatically.

## Backend Architecture

### Database Models

**User** → **Board** → **Column** → **Card**

- User: username (hardcoded "user" for MVP)
- Board: title, belongs to user
- Column: title, position (for ordering)
- Card: title, details, position (for ordering within column)

See [database-schema.md](./database-schema.md) for full schema.

### Request/Response Format

Board data returned by `/api/board`:
```json
{
  "id": 1,
  "title": "My Project",
  "columns": [
    {
      "id": 1,
      "title": "TODO",
      "position": 0,
      "cards": [
        {
          "id": 1,
          "title": "Task",
          "details": "...",
          "position": 0
        }
      ]
    }
  ]
}
```

Frontend converts this to:
```ts
{
  columns: [
    {
      id: "col-1",
      title: "TODO",
      cardIds: ["1", "2"]
    }
  ],
  cards: {
    "1": { id: "1", title: "Task", details: "..." },
    "2": { ...  }
  }
}
```

(Column IDs prefixed with "col-" to avoid dnd-kit ID namespace collisions.)

### AI Integration (ai.py)

Two functions:
- `call_ai(message)` - Simple query, returns OpenRouter response
- `call_ai_with_context(board_data, question)` - Query with board context, expects JSON response with updates

AI is instructed to respond with:
```json
{
  "response": "Text response to user",
  "updates": [
    { "action": "create_card", "columnId": 1, "title": "...", "details": "..." },
    { "action": "move_card", "cardId": 1, "columnId": 2, "position": 0 },
    { "action": "delete_card", "cardId": 1 }
  ]
}
```

## Deployment Checklist

- [ ] Frontend builds without TypeScript errors: `npm run build`
- [ ] Backend tests pass: `pytest`
- [ ] Docker image builds: `docker build -t pm-mvp .`
- [ ] Container starts without errors: `docker-compose up`
- [ ] Can login with user/password at http://localhost:8000
- [ ] Can create/edit/move/delete cards
- [ ] AI sidebar works and updates board
- [ ] Database persists across container restart

## Troubleshooting

### Frontend won't build
- Check Node.js version: `node --version` (needs v20+)
- Clear cache: `rm -rf .next out node_modules && npm install`

### Backend won't start
- Check Python version: `python3 --version` (needs 3.10+)
- Check dependencies: `uv sync`
- Check .env file has OPENROUTER_API_KEY

### AI calls fail with 403/402
- Verify API key in .env is valid
- Check account has credits on https://openrouter.ai/settings/credits
- Model gpt-oss-120b:free is free tier (no credits needed)

### Docker container won't start
- Check port 8000 is free: `lsof -i :8000`
- Check .env file is in project root
- View logs: `docker-compose logs -f`

### Cards don't persist after refresh
- Check backend is actually saving to DB (in logs)
- Check database file exists: `backend/kanban.db`
- Verify token is being sent in Authorization header

## Performance Notes

- **Frontend**: Static export (no server-side rendering), very fast
- **Backend**: In-memory token store (MVP only, not production)
- **Database**: SQLite (fine for MVP, would need PostgreSQL for production)
- **AI**: Calls are async, don't block board UI

## Security Notes

**MVP only** - not production-ready:
- Credentials hardcoded ("user"/"password")
- Token stored in-memory (lost on restart)
- No HTTPS
- No rate limiting
- No CORS configured (uses simple Bearer token)

For production, add:
- Proper authentication (OAuth, JWT with refresh tokens)
- Database encryption
- HTTPS/TLS
- Rate limiting and DDoS protection
- Environment-based config
- CORS headers
- Request validation and sanitization

## Code Style

- **Frontend**: TypeScript, no ESLint rules disabled, idiomatic React hooks
- **Backend**: Python 3.10+ idioms, type hints, minimal comments
- **General**: No emojis, concise naming, prefer simplicity over abstraction

## Contributing

Follow the coding standards in [CLAUDE.md](../CLAUDE.md):
1. Use latest library versions
2. Keep it simple - no over-engineering
3. Be concise
4. Identify root cause before fixing (don't guess)

## Next Steps

After MVP completion:
1. User management (multiple accounts, auth provider)
2. Multiple boards per user
3. Team collaboration
4. Real-time sync (WebSockets)
5. Advanced AI features (attachments, voice)
6. Mobile app
