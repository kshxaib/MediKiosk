# Graph Report - MediKiosk  (2026-08-28)

## Corpus Check
- 87 files · ~25,362 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 488 nodes · 738 edges · 39 communities (31 shown, 8 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 25 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5653f321`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- MediKiosk
- test_auth.py
- system_service.py
- What You Must Do When Invoked
- devDependencies
- AppRoutes.tsx
- test_health.py
- compilerOptions
- compilerOptions
- Frontend Entry and Documentation
- main.py
- endpoints/auth.py
- User
- graphify reference: extra exports and benchmark
- graphify reference: query, path, explain
- 0001_baseline.py
- test_config.py
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- vite-env.d.ts
- tsconfig.json
- app/__init__.py
- .claude/CLAUDE.md
- extraction-spec.md
- useAuthStore.ts
- package.json

## God Nodes (most connected - your core abstractions)
1. `User` - 25 edges
2. `compilerOptions` - 19 edges
3. `compilerOptions` - 17 edges
4. `utcnow()` - 13 edges
5. `AuthService` - 12 edges
6. `create_access_token()` - 12 edges
7. `What You Must Do When Invoked` - 12 edges
8. `Role` - 11 edges
9. `decode_token()` - 11 edges
10. `/graphify` - 11 edges

## Surprising Connections (you probably didn't know these)
- `logout()` --uses--> `User`  [INFERRED]
  backend/app/api/v1/endpoints/auth.py → backend/app/models/user.py
- `get_current_staff_profile()` --uses--> `User`  [INFERRED]
  backend/app/api/v1/endpoints/auth.py → backend/app/models/user.py
- `setup_test_users()` --uses--> `Role`  [INFERRED]
  backend/tests/test_auth.py → backend/app/models/role.py
- `AuthService` --uses--> `User`  [INFERRED]
  backend/app/services/auth/auth_service.py → backend/app/models/user.py
- `setup_test_users()` --uses--> `User`  [INFERRED]
  backend/tests/test_auth.py → backend/app/models/user.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Clinical Intake Flow** — identity_provider_abstraction, ai_clinical_assistant, ocr_extraction_pipeline [EXTRACTED 0.95]

## Communities (39 total, 8 thin omitted)

### Community 0 - "MediKiosk"
Cohesion: 0.11
Nodes (17): AI Clinical Assistant, Cloudinary Document Pipeline, Identity Provider Abstraction, OCR & Extraction Pipeline, PostgreSQL Schema, Project Requirement, 1. Start PostgreSQL, 2. Backend (+9 more)

### Community 1 - "test_auth.py"
Cohesion: 0.13
Nodes (25): hash_password(), Password hashing and verification utilities using bcrypt., Verify a plaintext password against a stored bcrypt hash., Hash a plaintext password with a unique salt., verify_password(), client(), fixture, TestClient (+17 more)

### Community 2 - "system_service.py"
Cohesion: 0.10
Nodes (26): public_config(), get, PublicConfig, Public (non-secret) configuration endpoint consumed by the frontend., health(), get, HealthResponse, Session (+18 more)

### Community 3 - "What You Must Do When Invoked"
Cohesion: 0.07
Nodes (26): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+18 more)

### Community 4 - "devDependencies"
Cohesion: 0.07
Nodes (29): eslint, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, devDependencies, eslint, @eslint/js, eslint-plugin-react-hooks (+21 more)

### Community 5 - "AppRoutes.tsx"
Cohesion: 0.13
Nodes (16): Container(), ContainerProps, ProtectedRoute(), ProtectedRouteProps, StatusBadge(), StatusBadgeProps, env, RootLayout() (+8 more)

### Community 6 - "test_health.py"
Cohesion: 0.17
Nodes (11): get_db(), Session, Yield a request-scoped database session and always close it., _failing_db(), _FailingSession, _ok_db(), _OkSession, TestClient (+3 more)

### Community 7 - "compilerOptions"
Cohesion: 0.08
Nodes (24): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection, moduleResolution (+16 more)

### Community 8 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, moduleResolution, noEmit (+12 more)

### Community 10 - "main.py"
Cohesion: 0.11
Nodes (17): get_settings(), Centralized application configuration. All runtime configuration is read from…, Settings, AppError, FastAPI, Application error type and centralized exception handling. A single…, Base class for expected, handled application errors., register_exception_handlers() (+9 more)

### Community 11 - "endpoints/auth.py"
Cohesion: 0.06
Nodes (51): get_current_staff_profile(), login(), logout(), get, Session, User, Staff Authentication endpoints., Authenticate a staff user and issue JWT Access and Refresh tokens. (+43 more)

### Community 12 - "User"
Cohesion: 0.06
Nodes (48): Alembic migration environment. The database URL is pulled from application…, get_current_active_user(), get_current_user(), User, Shared FastAPI dependencies and RBAC security guards., Validate Bearer access token and return the authenticated User., Ensure the authenticated user is currently active., Dependency factory enforcing RBAC role permissions on route handlers. (+40 more)

### Community 13 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 14 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 17 - "0001_baseline.py"
Cohesion: 0.40
Nodes (4): downgrade(), No-op: no schema in Phase 1., No-op: no schema in Phase 1., upgrade()

### Community 18 - "test_config.py"
Cohesion: 0.50
Nodes (4): TestClient, Tests for GET /api/v1/config/public., test_public_config_leaks_no_secrets(), test_public_config_returns_non_secret_fields()

### Community 19 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 20 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 21 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 36 - "useAuthStore.ts"
Cohesion: 0.19
Nodes (15): apiClient, TOKEN_KEY, authService, getHealth(), getPublicConfig(), AuthState, SystemState, useSystemStore (+7 more)

### Community 37 - "package.json"
Cohesion: 0.10
Nodes (20): axios, dependencies, axios, react, react-dom, react-router-dom, zustand, name (+12 more)

## Knowledge Gaps
- **133 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+128 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `test_auth.py`, `endpoints/auth.py`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Why does `utcnow()` connect `User` to `test_auth.py`, `system_service.py`, `endpoints/auth.py`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Why does `get_health()` connect `system_service.py` to `User`?**
  _High betweenness centrality (0.010) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `User` (e.g. with `get_current_active_user()` and `get_current_user()`) actually correct?**
  _`User` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `private`, `version` to the rest of the system?**
  _133 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `MediKiosk` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._
- **Should `test_auth.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1282051282051282 - nodes in this community are weakly interconnected._