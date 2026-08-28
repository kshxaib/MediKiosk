# Graph Report - MediKiosk  (2026-08-29)

## Corpus Check
- 150 files · ~52,367 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 924 nodes · 1915 edges · 66 communities (50 shown, 16 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 88 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b72df9a0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- MediKiosk
- test_auth.py
- router.py
- What You Must Do When Invoked
- devDependencies
- AppRoutes.tsx
- test_health.py
- compilerOptions
- compilerOptions
- Frontend Entry and Documentation
- main.py
- endpoints/auth.py
- deps.py
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
- endpoints/identity.py
- dependencies
- patients.py
- useSessionStore.ts
- Base
- ConfigService
- utcnow
- test_sessions.py
- interview.py
- AuthService
- auth_service.py
- get_doctor_profile
- get_current_staff_profile
- get_admin_dashboard_stats
- package.json
- scripts
- schemas/hospital.py
- tailwindcss
- @tailwindcss/vite
- @types/node
- @types/react-dom
- typescript
- typescript-eslint
- vite
- @vitejs/plugin-react
- core/config.py

## God Nodes (most connected - your core abstractions)
1. `Base` - 29 edges
2. `UUIDPrimaryKeyMixin` - 28 edges
3. `utcnow()` - 27 edges
4. `User` - 26 edges
5. `TimestampMixin` - 24 edges
6. `SessionService` - 22 edges
7. `Patient` - 21 edges
8. `compilerOptions` - 19 edges
9. `Department` - 18 edges
10. `IntakeSession` - 18 edges

## Surprising Connections (you probably didn't know these)
- `get_current_user()` --uses--> `User`  [INFERRED]
  backend/app/api/deps.py → backend/app/models/user.py
- `get_current_active_user()` --uses--> `User`  [INFERRED]
  backend/app/api/deps.py → backend/app/models/user.py
- `require_role()` --uses--> `User`  [INFERRED]
  backend/app/api/deps.py → backend/app/models/user.py
- `get_admin_dashboard_stats()` --uses--> `User`  [INFERRED]
  backend/app/api/v1/endpoints/admin.py → backend/app/models/user.py
- `login()` --uses--> `LoginRequest`  [INFERRED]
  backend/app/api/v1/endpoints/auth.py → backend/app/schemas/auth.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Clinical Intake Flow** — identity_provider_abstraction, ai_clinical_assistant, ocr_extraction_pipeline [EXTRACTED 0.95]

## Communities (66 total, 16 thin omitted)

### Community 0 - "MediKiosk"
Cohesion: 0.11
Nodes (17): AI Clinical Assistant, Cloudinary Document Pipeline, Identity Provider Abstraction, OCR & Extraction Pipeline, PostgreSQL Schema, Project Requirement, 1. Start PostgreSQL, 2. Backend (+9 more)

### Community 1 - "test_auth.py"
Cohesion: 0.13
Nodes (25): hash_password(), Password hashing and verification utilities using bcrypt., Verify a plaintext password against a stored bcrypt hash., Hash a plaintext password with a unique salt., verify_password(), client(), fixture, TestClient (+17 more)

### Community 2 - "router.py"
Cohesion: 0.10
Nodes (26): public_config(), get, PublicConfig, Public (non-secret) configuration endpoint consumed by the frontend., health(), get, HealthResponse, Session (+18 more)

### Community 3 - "What You Must Do When Invoked"
Cohesion: 0.07
Nodes (26): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+18 more)

### Community 4 - "devDependencies"
Cohesion: 0.15
Nodes (13): eslint, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, devDependencies, eslint, @eslint/js, eslint-plugin-react-hooks (+5 more)

### Community 5 - "AppRoutes.tsx"
Cohesion: 0.11
Nodes (30): Container(), ContainerProps, ProtectedRoute(), ProtectedRouteProps, StatusBadge(), StatusBadgeProps, RootLayout(), rootElement (+22 more)

### Community 6 - "test_health.py"
Cohesion: 0.22
Nodes (8): _failing_db(), _FailingSession, _ok_db(), _OkSession, TestClient, Tests for GET /api/v1/health. The DB session dependency is overridden with…, test_health_ok(), test_health_reports_503_when_db_down()

### Community 7 - "compilerOptions"
Cohesion: 0.08
Nodes (24): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection, moduleResolution (+16 more)

### Community 8 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, moduleResolution, noEmit (+12 more)

### Community 10 - "main.py"
Cohesion: 0.06
Nodes (47): AppError, FastAPI, Application error type and centralized exception handling. A single…, Base class for expected, handled application errors., register_exception_handlers(), create_app(), FastAPI, FastAPI application entry point. Builds the app via a factory so it can be… (+39 more)

### Community 11 - "endpoints/auth.py"
Cohesion: 0.15
Nodes (16): Staff Authentication endpoints., LoginRequest, LogoutResponse, BaseModel, Authentication and JWT request/response schemas., Returns email or username depending on which was provided., Payload to request a new access token using a refresh token., Logout confirmation response. (+8 more)

### Community 12 - "deps.py"
Cohesion: 0.15
Nodes (14): get_current_active_user(), get_current_user(), get_db(), Session, User, Shared FastAPI dependencies and RBAC security guards., Yield a request-scoped database session and always close it., Validate Bearer access token and return the authenticated User. (+6 more)

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

### Community 36 - "endpoints/identity.py"
Cohesion: 0.06
Nodes (44): enroll_face(), _extract_image_bytes(), post, Session, Patient Biometric Identity API Endpoints., Extract raw image bytes from data URI or raw base64 string., Extracts face embedding from webcam capture and stores active FaceEnrollment., Compares live webcam capture with enrolled biometric. Returns verified=True on… (+36 more)

### Community 37 - "dependencies"
Cohesion: 0.18
Nodes (11): axios, dependencies, axios, react, react-dom, react-router-dom, zustand, react (+3 more)

### Community 38 - "patients.py"
Cohesion: 0.06
Nodes (50): create_patient(), get_patient(), lookup_patient_by_mobile(), get, patch, post, Session, UUID (+42 more)

### Community 39 - "useSessionStore.ts"
Cohesion: 0.11
Nodes (30): env, apiClient, TOKEN_KEY, AuthState, PatientState, SessionState, SystemState, HealthResponse (+22 more)

### Community 40 - "Base"
Cohesion: 0.07
Nodes (64): Base, Declarative base and shared metadata. A consistent naming convention makes…, Reusable model mixins (infrastructure only — no tables defined here). These…, Adds a UUID ``id`` primary key (never a mobile number / RFID / biometric)., Adds UTC ``created_at`` / ``updated_at`` columns., TimestampMixin, UUIDPrimaryKeyMixin, Session (+56 more)

### Community 41 - "ConfigService"
Cohesion: 0.08
Nodes (36): list_department_consultants(), list_departments(), get, Session, UUID, Department configuration endpoints., list_languages(), get (+28 more)

### Community 42 - "utcnow"
Cohesion: 0.13
Nodes (33): clear_session(), complete_session(), create_session(), get_consents(), get_session(), get, patch, post (+25 more)

### Community 43 - "test_sessions.py"
Cohesion: 0.14
Nodes (25): client(), created_patient(), fixture, TestClient, random_mobile(), Comprehensive unit and integration tests for Phase 4 Session and Consent., Helper to create a fresh registered patient for session tests., test_clear_session_cancels_session() (+17 more)

### Community 45 - "interview.py"
Cohesion: 0.12
Nodes (23): get_next_question(), get_session_answers(), AnswerSubmissionResponse, get, post, Session, UUID, Clinical Interview AI Foundation API endpoints. (+15 more)

### Community 46 - "AuthService"
Cohesion: 0.16
Nodes (16): login(), Session, Authenticate a staff user and issue JWT Access and Refresh tokens., Exchange a valid refresh token for a new access token., refresh_token(), Response returned upon successful login., Response containing a renewed access token., TokenRefreshResponse (+8 more)

### Community 48 - "auth_service.py"
Cohesion: 0.22
Nodes (14): Staff authentication service., Auth services package., create_access_token(), create_refresh_token(), decode_token(), Any, UUID, JWT token creation, validation, and extraction using PyJWT. (+6 more)

### Community 49 - "get_doctor_profile"
Cohesion: 0.40
Nodes (5): get_doctor_profile(), Any, get, User, Doctor route verifying DOCTOR (or supervisory ADMIN) role access.

### Community 50 - "get_current_staff_profile"
Cohesion: 0.29
Nodes (7): get_current_staff_profile(), logout(), get, post, User, Acknowledge logout for the authenticated staff session., Return the profile and role of the currently authenticated staff member.

### Community 51 - "get_admin_dashboard_stats"
Cohesion: 0.40
Nodes (5): get_admin_dashboard_stats(), Any, get, User, Admin-only diagnostic endpoint verifying ADMIN RBAC role access.

### Community 52 - "package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 53 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, preview

### Community 54 - "schemas/hospital.py"
Cohesion: 0.50
Nodes (3): HospitalRead, BaseModel, Hospital Pydantic schemas.

### Community 64 - "core/config.py"
Cohesion: 0.18
Nodes (6): Alembic migration environment. The database URL is pulled from application…, get_settings(), Centralized application configuration. All runtime configuration is read from…, Settings, Database engine and session factory. Creating the engine does not open a…, BaseSettings

## Knowledge Gaps
- **135 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+130 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `utcnow()` connect `utcnow` to `test_auth.py`, `router.py`, `endpoints/identity.py`, `patients.py`, `Base`, `interview.py`, `AuthService`, `auth_service.py`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Why does `User` connect `Base` to `test_auth.py`, `endpoints/auth.py`, `deps.py`, `AuthService`, `auth_service.py`, `get_doctor_profile`, `get_current_staff_profile`, `get_admin_dashboard_stats`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Why does `create_app()` connect `main.py` to `test_auth.py`, `test_sessions.py`, `endpoints/identity.py`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `User` (e.g. with `get_current_active_user()` and `get_current_user()`) actually correct?**
  _`User` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `private`, `version` to the rest of the system?**
  _135 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `MediKiosk` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._
- **Should `test_auth.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1282051282051282 - nodes in this community are weakly interconnected._