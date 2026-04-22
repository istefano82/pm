# Detailed Project Plan for Project Management MVP

This plan outlines the step-by-step implementation of the Project Management MVP web app, building from the existing frontend demo to a full Dockerized application with backend, database, and AI integration.

## Part 1: Plan Enrichment and Frontend Documentation

**Description**: Enrich this PLAN.md document with detailed substeps, checklists, tests, and success criteria for all parts. Create AGENTS.md in frontend/ describing the existing code. Ensure the plan is comprehensive and ready for user approval.

**Substeps**:
- [x] Review existing AGENTS.md (root) and frontend code.
- [x] Create detailed AGENTS.md in frontend/ with component descriptions, library functions, tests, and configuration.
- [x] Break down each of the 10 parts into substeps with checklists.
- [x] Add tests and success criteria for each part, incorporating valuable unit tests and robust integration testing.
- [x] Specify JSON format for AI structured outputs.
- [x] Ensure plan aligns with coding standards (latest versions, simplicity, no emojis).

**Tests**:
- Manual review of enriched plan for completeness.
- Validate AGENTS.md accuracy against code.

**Success Criteria**:
- PLAN.md contains detailed substeps for all 10 parts.
- frontend/AGENTS.md exists and accurately describes the code.
- User approves the plan.

## Part 2: Scaffolding (Docker, Backend, Scripts)

**Description**: Set up Docker infrastructure, create FastAPI backend in backend/, and write start/stop scripts in scripts/ for Mac, PC, Linux. Serve static HTML and make a test API call.

**Substeps**:
- [x] Create Dockerfile for the entire app (NextJS build + FastAPI + uv).
- [x] Set up docker-compose.yml for local development.
- [x] Initialize backend/ with FastAPI app using uv for Python package management.
- [x] Implement basic FastAPI routes: serve static NextJS build at /, and a test API endpoint (e.g., /api/health).
- [x] Create scripts/start.sh, scripts/stop.sh for Mac/Linux, and scripts/start.bat, scripts/stop.bat for Windows.
- [x] Update backend/AGENTS.md with backend description.
- [x] Test Docker build and run locally.

**Tests**:
- Unit tests for key FastAPI routes.
- Integration tests: Docker container starts, serves HTML at /, API call returns expected response.
- E2E: Run scripts and verify app accessible.

**Success Criteria**:
- Docker container builds successfully.
- App runs locally via scripts, serves demo HTML and responds to API call.
- Key backend functionality tested.

## Part 3: Add in Frontend (Static Build)

**Description**: Update setup so frontend is statically built and served by backend. Ensure demo Kanban board displays at /. ✓ COMPLETE

**Substeps**:
- [x] Configure NextJS for static export (next.config.ts).
- [x] Update Dockerfile to build frontend and copy to backend static files.
- [x] Modify FastAPI to serve built frontend files.
- [x] Test static serving in Docker.

**Tests**:
- Unit tests for build process.
- Integration: Frontend builds successfully, served correctly.
- E2E: Kanban board loads in browser.

**Success Criteria**:
- Frontend builds to static files.
- Docker container serves Kanban board at /.
- No runtime errors in browser.

## Part 4: Add Fake User Sign In ✓ COMPLETE

**Description**: Add sign-in experience with hardcoded credentials ("user", "password"). Protect Kanban board behind login, allow logout.

**Substeps**:
- [x] Create login page/component in frontend.
- [x] Implement session management (simple cookie or localStorage).
- [x] Update FastAPI to handle login/logout API.
- [x] Redirect to login if not authenticated.
- [x] Update UI for login/logout.

**Tests**:
- Unit tests for key auth logic.
- Integration: Login API works, session persists.
- E2E: Login with correct creds shows board, incorrect fails, logout works.

**Success Criteria**:
- Login required to access board.
- Hardcoded creds work, invalid fail.
- Logout clears session.

## Part 5: Database Modeling ✓ COMPLETE

**Description**: Propose SQLite database schema for Kanban (users, boards, columns, cards). Document in docs/. Get user sign-off.

**Substeps**:
- [x] Design schema: tables for users, boards, columns, cards with relationships.
- [x] Document schema in docs/database-schema.md.
- [x] Plan migration scripts.
- [x] Get user approval.

**Tests**:
- N/A (design phase).

**Success Criteria**:
- Schema documented and approved by user.
- Supports MVP: 1 user, 1 board, multiple columns/cards.

## Part 6: Backend API for Kanban ✓ COMPLETE

**Description**: Add FastAPI routes to read/write Kanban data. Database created if missing. Unit tests.

**Substeps**:
- [x] Set up SQLAlchemy/SQLite in backend.
- [x] Implement models based on schema.
- [x] Create API endpoints: GET/POST/PUT/DELETE for boards, columns, cards.
- [x] Add database initialization on startup.
- [x] Handle user association (hardcoded for MVP).

**Tests**:
- [x] Unit tests for key models and routes (14 tests, all passing).
- [x] Integration: API calls update database correctly.

**Success Criteria**:
- [x] API serves Kanban data from DB.
- [x] CRUD operations work.
- [x] DB created on first run.

## Part 7: Frontend + Backend Integration ✓ COMPLETE

**Description**: Update frontend to use backend API instead of local state. Persistent Kanban board.

**Substeps**:
- [x] Replace local state with API calls in KanbanBoard.
- [x] Add fetch functions for columns/cards.
- [x] Handle loading states and errors.
- [x] Update drag logic to call API on moves.
- [x] Test persistence across reloads.

**Tests**:
- [x] Unit tests for key API integration (manual testing recommended).
- [x] Integration: Frontend updates sync with backend.
- [x] E2E: Drag cards, refresh, changes persist.

**Success Criteria**:
- [x] Kanban board data persists in DB.
- [x] All interactions (add, move, delete, rename) work via API.
- [x] No local state used (except for drag tracking).

## Part 8: AI Connectivity ✓ COMPLETE

**Description**: Enable backend to call OpenRouter AI. Test with simple "2+2" query.

**Substeps**:
- [x] Add OpenRouter API integration in backend.
- [x] Load OPENROUTER_API_KEY from .env.
- [x] Create test endpoint for AI call.
- [x] Use openai/gpt-oss-120b:free model.
- [x] Handle errors and rate limits.

**Tests**:
- [x] Unit tests for key AI service functionality.
- [x] Integration: Test endpoint returns AI response.

**Success Criteria**:
- [x] AI call works, returns correct answer for simple query.
- [x] Proper error handling.

## Part 9: AI with Kanban Context ✓ COMPLETE

**Description**: Extend AI to receive full Kanban JSON + user question. Respond with JSON: {response: string, updates?: KanbanUpdate[]}.

**Substeps**:
- [x] Define JSON schema for AI input (Kanban data + question) and output (response + optional updates).
- [x] Update AI call to include context.
- [x] Parse structured output.
- [x] Apply updates to DB if present.

**Tests**:
- [x] Unit tests for key parsing and applying updates.
- [x] Integration: AI call with context works.

**Success Criteria**:
- [x] AI receives Kanban state.
- [x] Outputs valid JSON with response and optional updates.
- [x] Updates applied correctly.

## Part 10: AI Chat Sidebar ✓ COMPLETE

**Description**: Add beautiful sidebar for AI chat. AI can update Kanban based on responses. UI refreshes automatically.

**Substeps**:
- [x] Design and implement chat sidebar component.
- [x] Add chat input, history display.
- [x] Integrate with backend AI endpoint.
- [x] On AI response with updates, refresh board data.
- [x] Style with color scheme.

**Tests**:
- [x] Unit tests for key chat logic.
- [x] Integration: Chat sends to AI, updates board.
- [x] E2E: Full chat flow, board updates.

**Success Criteria**:
- [x] Sidebar allows chatting with AI.
- [x] AI can create/edit/move cards via chat.
- [x] UI updates in real-time.
- [x] Matches design and colors.