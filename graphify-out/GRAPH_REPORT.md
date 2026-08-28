# Graph Report - MediKiosk  (2026-08-28)

## Corpus Check
- 107 files · ~38,483 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 659 nodes · 1117 edges · 51 communities (41 shown, 10 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 44 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6dff5177`
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
- endpoints/identity.py
- package.json
- patients.py
- usePatientStore.ts
- patient_service.py
- utcnow
- Base
- Role
- .lookup
- .lookup
- InsightFaceService
- get_doctor_profile
- models/__init__.py

## God Nodes (most connected - your core abstractions)
1. `User` - 25 edges
2. `utcnow()` - 19 edges
3. `compilerOptions` - 19 edges
4. `compilerOptions` - 17 edges
5. `Patient` - 16 edges
6. `PatientService` - 15 edges
7. `MobileIdentityProvider` - 14 edges
8. `Base` - 13 edges
9. `FaceEnrollment` - 13 edges
10. `PatientIdentifier` - 13 edges

## Surprising Connections (you probably didn't know these)
- `get_current_user()` --uses--> `User`  [INFERRED]
  backend/app/api/deps.py → backend/app/models/user.py
- `logout()` --uses--> `User`  [INFERRED]
  backend/app/api/v1/endpoints/auth.py → backend/app/models/user.py
- `get_current_staff_profile()` --uses--> `User`  [INFERRED]
  backend/app/api/v1/endpoints/auth.py → backend/app/models/user.py
- `get_doctor_profile()` --uses--> `User`  [INFERRED]
  backend/app/api/v1/endpoints/doctor.py → backend/app/models/user.py
- `lookup_patient_by_mobile()` --uses--> `MobileIdentityProvider`  [INFERRED]
  backend/app/api/v1/endpoints/patients.py → backend/app/services/identity/mobile_provider.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Clinical Intake Flow** — identity_provider_abstraction, ai_clinical_assistant, ocr_extraction_pipeline [EXTRACTED 0.95]

## Communities (51 total, 10 thin omitted)

### Community 0 - "MediKiosk"
Cohesion: 0.11
Nodes (17): AI Clinical Assistant, Cloudinary Document Pipeline, Identity Provider Abstraction, OCR & Extraction Pipeline, PostgreSQL Schema, Project Requirement, 1. Start PostgreSQL, 2. Backend (+9 more)

### Community 1 - "test_auth.py"
Cohesion: 0.13
Nodes (25): hash_password(), Password hashing and verification utilities using bcrypt., Verify a plaintext password against a stored bcrypt hash., Hash a plaintext password with a unique salt., verify_password(), client(), fixture, TestClient (+17 more)

### Community 2 - "system_service.py"
Cohesion: 0.08
Nodes (30): public_config(), get, PublicConfig, Public (non-secret) configuration endpoint consumed by the frontend., health(), get, HealthResponse, Session (+22 more)

### Community 3 - "What You Must Do When Invoked"
Cohesion: 0.07
Nodes (26): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+18 more)

### Community 4 - "devDependencies"
Cohesion: 0.07
Nodes (29): eslint, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, devDependencies, eslint, @eslint/js, eslint-plugin-react-hooks (+21 more)

### Community 5 - "AppRoutes.tsx"
Cohesion: 0.12
Nodes (20): Container(), ContainerProps, ProtectedRoute(), ProtectedRouteProps, StatusBadge(), StatusBadgeProps, RootLayout(), rootElement (+12 more)

### Community 6 - "test_health.py"
Cohesion: 0.13
Nodes (14): get_current_user(), get_db(), Session, Yield a request-scoped database session and always close it., Validate Bearer access token and return the authenticated User., _failing_db(), _FailingSession, _ok_db() (+6 more)

### Community 7 - "compilerOptions"
Cohesion: 0.08
Nodes (24): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection, moduleResolution (+16 more)

### Community 8 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, moduleResolution, noEmit (+12 more)

### Community 10 - "main.py"
Cohesion: 0.08
Nodes (35): AppError, FastAPI, Application error type and centralized exception handling. A single…, Base class for expected, handled application errors., register_exception_handlers(), create_app(), FastAPI, FastAPI application entry point. Builds the app via a factory so it can be… (+27 more)

### Community 11 - "endpoints/auth.py"
Cohesion: 0.06
Nodes (53): get_current_staff_profile(), login(), logout(), get, post, Session, User, Staff Authentication endpoints. (+45 more)

### Community 12 - "User"
Cohesion: 0.15
Nodes (16): get_current_active_user(), User, Shared FastAPI dependencies and RBAC security guards., Ensure the authenticated user is currently active., Dependency factory enforcing RBAC role permissions on route handlers., require_role(), get_admin_dashboard_stats(), Any (+8 more)

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
Cohesion: 0.09
Nodes (30): enroll_face(), _extract_image_bytes(), post, Session, Patient Biometric Identity API Endpoints., Extract raw image bytes from data URI or raw base64 string., Extracts face embedding from webcam capture and stores active FaceEnrollment., Compares live webcam capture with enrolled biometric. Returns verified=True on… (+22 more)

### Community 37 - "package.json"
Cohesion: 0.10
Nodes (20): axios, dependencies, axios, react, react-dom, react-router-dom, zustand, name (+12 more)

### Community 38 - "patients.py"
Cohesion: 0.09
Nodes (35): create_patient(), get_patient(), lookup_patient_by_mobile(), get, post, Session, UUID, Patient API Endpoints. (+27 more)

### Community 39 - "usePatientStore.ts"
Cohesion: 0.15
Nodes (18): env, apiClient, TOKEN_KEY, AuthState, PatientState, SystemState, HealthResponse, PublicConfig (+10 more)

### Community 40 - "patient_service.py"
Cohesion: 0.16
Nodes (16): Adds UTC ``created_at`` / ``updated_at`` columns., TimestampMixin, PatientIdentifier, PatientIdentifier ORM model for polymorphic identifier abstraction., Identifier attached to a patient (e.g. MOBILE, future RFID)., Patient, IdentityProvider, ABC (+8 more)

### Community 41 - "utcnow"
Cohesion: 0.21
Nodes (12): Reusable model mixins (infrastructure only — no tables defined here). These…, Adds a UUID ``id`` primary key (never a mobile number / RFID / biometric)., UUIDPrimaryKeyMixin, FaceEnrollment, FaceEnrollment ORM model., Stores biometric face enrollment embedding references., Role ORM model for RBAC., InsightFace ArcFace Biometric Service implementation. (+4 more)

### Community 42 - "Base"
Cohesion: 0.29
Nodes (4): Alembic migration environment. The database URL is pulled from application…, Base, Declarative base and shared metadata. A consistent naming convention makes…, DeclarativeBase

### Community 43 - "Role"
Cohesion: 0.22
Nodes (7): Session, Safe development seeding for initial roles and dev staff accounts., Idempotently seed default roles and development test accounts., seed_database(), Database engine and session factory. Creating the engine does not open a…, Staff roles (e.g. ADMIN, DOCTOR)., Role

### Community 45 - ".lookup"
Cohesion: 0.50
Nodes (3): Patient, Session, Looks up an active patient by their identifier value.

### Community 48 - "InsightFaceService"
Cohesion: 0.19
Nodes (9): InsightFaceService, Session, UUID, Verify live captured face against stored active enrollment using cosine…, Production-grade biometric facial recognition service using InsightFace ArcFace…, Decode raw image bytes to BGR numpy array., Detect face and extract normalized 512-d ArcFace embedding vector., Extract biometric embedding and persist active FaceEnrollment. (+1 more)

### Community 49 - "get_doctor_profile"
Cohesion: 0.40
Nodes (5): get_doctor_profile(), Any, get, User, Doctor route verifying DOCTOR (or supervisory ADMIN) role access.

## Knowledge Gaps
- **133 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+128 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `utcnow()` connect `utcnow` to `test_auth.py`, `system_service.py`, `patients.py`, `patient_service.py`, `endpoints/auth.py`, `InsightFaceService`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Why does `User` connect `User` to `test_auth.py`, `test_health.py`, `patient_service.py`, `utcnow`, `Base`, `endpoints/auth.py`, `Role`, `get_doctor_profile`, `models/__init__.py`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Why does `Patient` connect `patient_service.py` to `patients.py`, `utcnow`, `Base`, `InsightFaceService`, `models/__init__.py`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `User` (e.g. with `get_current_active_user()` and `get_current_user()`) actually correct?**
  _`User` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `Patient` (e.g. with `InsightFaceService` and `IdentityProvider`) actually correct?**
  _`Patient` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `private`, `version` to the rest of the system?**
  _133 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `MediKiosk` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._