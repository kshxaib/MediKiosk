# Graph Report - MediKiosk  (2026-08-29)

## Corpus Check
- 158 files · ~66,172 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1141 nodes · 2475 edges · 77 communities (59 shown, 18 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 117 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9d125ae5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- MediKiosk
- test_auth.py
- system_service.py
- What You Must Do When Invoked
- devDependencies
- AppRoutes.tsx
- Base
- compilerOptions
- compilerOptions
- Frontend Entry and Documentation
- test_interview.py
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
- OpenAIService
- session_service.py
- ConfigService
- SessionService
- test_sessions.py
- interview.py
- AuthService
- utcnow
- question_service.py
- schemas/user.py
- clinical_facts.py
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
- test_llm_service.py
- Question
- test_health.py
- User
- core/config.py
- get_doctor_profile
- conftest.py
- ClinicalContext
- NextQuestionDecision
- env.py
- _settings_ctx
- datetime.py

## God Nodes (most connected - your core abstractions)
1. `Base` - 29 edges
2. `UUIDPrimaryKeyMixin` - 28 edges
3. `QuestionService` - 28 edges
4. `NextQuestionDecision` - 27 edges
5. `utcnow()` - 27 edges
6. `User` - 26 edges
7. `AnswerExtraction` - 25 edges
8. `TimestampMixin` - 24 edges
9. `SessionService` - 22 edges
10. `Patient` - 21 edges

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

## Communities (77 total, 18 thin omitted)

### Community 0 - "MediKiosk"
Cohesion: 0.11
Nodes (17): AI Clinical Assistant, Cloudinary Document Pipeline, Identity Provider Abstraction, OCR & Extraction Pipeline, PostgreSQL Schema, Project Requirement, 1. Start PostgreSQL, 2. Backend (+9 more)

### Community 1 - "test_auth.py"
Cohesion: 0.13
Nodes (25): hash_password(), Password hashing and verification utilities using bcrypt., Verify a plaintext password against a stored bcrypt hash., Hash a plaintext password with a unique salt., verify_password(), client(), fixture, TestClient (+17 more)

### Community 2 - "system_service.py"
Cohesion: 0.11
Nodes (25): public_config(), get, PublicConfig, Public (non-secret) configuration endpoint consumed by the frontend., health(), get, HealthResponse, Session (+17 more)

### Community 3 - "What You Must Do When Invoked"
Cohesion: 0.07
Nodes (26): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+18 more)

### Community 4 - "devDependencies"
Cohesion: 0.15
Nodes (13): eslint, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, devDependencies, eslint, @eslint/js, eslint-plugin-react-hooks (+5 more)

### Community 5 - "AppRoutes.tsx"
Cohesion: 0.05
Nodes (62): Container(), ContainerProps, Navbar(), ProtectedRoute(), ProtectedRouteProps, StatusBadge(), StatusBadgeProps, env (+54 more)

### Community 6 - "Base"
Cohesion: 0.13
Nodes (28): Base, Declarative base and shared metadata. A consistent naming convention makes…, Reusable model mixins (infrastructure only — no tables defined here). These…, Adds a UUID ``id`` primary key (never a mobile number / RFID / biometric)., Adds UTC ``created_at`` / ``updated_at`` columns., TimestampMixin, UUIDPrimaryKeyMixin, Answer ORM model for storing clinically meaningful patient responses. (+20 more)

### Community 7 - "compilerOptions"
Cohesion: 0.08
Nodes (24): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection, moduleResolution (+16 more)

### Community 8 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, moduleResolution, noEmit (+12 more)

### Community 10 - "test_interview.py"
Cohesion: 0.05
Nodes (77): NextQuestionResponse, BaseModel, QuestionRead, classify_questions(), _contains_prohibited(), InterviewState, Any, Session (+69 more)

### Community 11 - "endpoints/auth.py"
Cohesion: 0.18
Nodes (15): Staff Authentication endpoints., LoginRequest, LogoutResponse, BaseModel, Authentication and JWT request/response schemas., Returns email or username depending on which was provided., Response returned upon successful login., Payload to request a new access token using a refresh token. (+7 more)

### Community 12 - "deps.py"
Cohesion: 0.12
Nodes (18): get_current_active_user(), get_current_user(), get_db(), Session, User, Shared FastAPI dependencies and RBAC security guards., Yield a request-scoped database session and always close it., Validate Bearer access token and return the authenticated User. (+10 more)

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
Nodes (42): enroll_face(), _extract_image_bytes(), post, Session, Patient Biometric Identity API Endpoints., Extract raw image bytes from data URI or raw base64 string., Extracts face embedding from webcam capture and stores active FaceEnrollment., Compares live webcam capture with enrolled biometric. Returns verified=True on… (+34 more)

### Community 37 - "dependencies"
Cohesion: 0.18
Nodes (11): axios, dependencies, axios, react, react-dom, react-router-dom, zustand, react (+3 more)

### Community 38 - "patients.py"
Cohesion: 0.06
Nodes (50): create_patient(), get_patient(), lookup_patient_by_mobile(), get, patch, post, Session, UUID (+42 more)

### Community 39 - "OpenAIService"
Cohesion: 0.12
Nodes (16): Run bounded LLM extraction. Raises LLMUnavailableError on failure., LLMUnavailableError, Exception, Raised when the LLM provider is unavailable or returns invalid output. The…, _current_fingerprint(), get_llm_service(), LLM service package (Phase 5B). Exports: BaseLLMService - Provider-neutral…, Return the configured LLM service. The instance is cached because constructing… (+8 more)

### Community 40 - "session_service.py"
Cohesion: 0.15
Nodes (14): Session, Safe development seeding for initial roles, dev staff accounts, hospitals,…, Idempotently seed default roles, test accounts, hospital, streams, and…, seed_database(), Department, Department ORM model., Hospital Department entity (GEN_MED, CARDIO, NEURO, etc.)., Hospital (+6 more)

### Community 41 - "ConfigService"
Cohesion: 0.07
Nodes (36): list_department_consultants(), list_departments(), get, Session, UUID, Department configuration endpoints., list_languages(), get (+28 more)

### Community 42 - "SessionService"
Cohesion: 0.16
Nodes (29): clear_session(), complete_session(), create_session(), get_consents(), get_session(), get, patch, post (+21 more)

### Community 43 - "test_sessions.py"
Cohesion: 0.06
Nodes (54): AppError, Exception, FastAPI, Application error type and centralized exception handling. A single…, Base class for expected, handled application errors., register_exception_handlers(), create_app(), FastAPI (+46 more)

### Community 45 - "interview.py"
Cohesion: 0.17
Nodes (18): get_next_question(), get_session_answers(), AnswerSubmissionResponse, get, post, Session, UUID, Clinical Interview AI Foundation API endpoints (Phase 5B). (+10 more)

### Community 46 - "AuthService"
Cohesion: 0.16
Nodes (15): login(), logout(), post, Session, Authenticate a staff user and issue JWT Access and Refresh tokens., Exchange a valid refresh token for a new access token., Acknowledge logout for the authenticated staff session., refresh_token() (+7 more)

### Community 48 - "utcnow"
Cohesion: 0.20
Nodes (16): Staff authentication service., Auth services package., create_access_token(), create_refresh_token(), decode_token(), Any, UUID, JWT token creation, validation, and extraction using PyJWT. (+8 more)

### Community 49 - "question_service.py"
Cohesion: 0.09
Nodes (28): Answer, Clinically meaningful answer entity linked to an IntakeSession., ClinicalWorkflow, Configurable clinical history & case-taking workflow., SessionStatus, Question Pydantic schemas., AnswerService, AnswerSubmissionResponse (+20 more)

### Community 50 - "schemas/user.py"
Cohesion: 0.22
Nodes (9): get_current_staff_profile(), get, User, Return the profile and role of the currently authenticated staff member., BaseModel, User and Role Pydantic response schemas., Sanitized staff user profile (never exposes password_hash)., RoleResponse (+1 more)

### Community 51 - "clinical_facts.py"
Cohesion: 0.11
Nodes (23): build_refinement_question(), ClinicalPolicy, _match_option(), _match_yes_no(), normalize_category(), policy_for_workflow(), Any, Clinical fact and category reasoning for the adaptive questioning engine. This… (+15 more)

### Community 52 - "package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 53 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, preview

### Community 54 - "schemas/hospital.py"
Cohesion: 0.50
Nodes (3): HospitalRead, BaseModel, Hospital Pydantic schemas.

### Community 64 - "test_llm_service.py"
Cohesion: 0.11
Nodes (20): AnswerExtraction, ExtractedFact, PreviousAnswerSummary, BaseModel, Structured Pydantic schemas for LLM input/output (Phase 5B). These are INTERNAL…, One normalized clinical key/value pair extracted from a patient answer., Structured LLM output for answer normalization., Fold the fact list into a mapping (later keys win). (+12 more)

### Community 66 - "Question"
Cohesion: 0.33
Nodes (4): ClinicalWorkflow ORM model., Question, Question ORM model for adaptive clinical intake., Question entity defined within a clinical workflow.

### Community 67 - "test_health.py"
Cohesion: 0.22
Nodes (8): _failing_db(), _FailingSession, _ok_db(), _OkSession, TestClient, Tests for GET /api/v1/health. The DB session dependency is overridden with…, test_health_ok(), test_health_reports_503_when_db_down()

### Community 68 - "User"
Cohesion: 0.40
Nodes (3): Protected Doctor demonstration routes., Staff user account (ADMIN, DOCTOR)., User

### Community 69 - "core/config.py"
Cohesion: 0.13
Nodes (11): get_settings(), Centralized application configuration. All runtime configuration is read from…, True only when a non-empty LLM API key is configured., Settings, Database engine and session factory. Creating the engine does not open a…, Live OpenAI smoke test (Phase 5B). Behaviour required of this file: - No…, Real API call for adaptive question selection. Any failure fails the test., Real API call for extraction. Verifies one answer -> several categories. Input… (+3 more)

### Community 70 - "get_doctor_profile"
Cohesion: 0.40
Nodes (5): get_doctor_profile(), Any, get, User, Doctor route verifying DOCTOR (or supervisory ADMIN) role access.

### Community 71 - "conftest.py"
Cohesion: 0.20
Nodes (11): Drop the cached service. Used by tests and after a config reload., reset_llm_service(), client(), disable_live_llm_for_unit_tests(), fixture, TestClient, Shared pytest fixtures. Tests exercise the API through FastAPI's ``TestClient``., Disable live LLM network calls during unit/integration tests. Guarantees fast,… (+3 more)

### Community 72 - "ClinicalContext"
Cohesion: 0.14
Nodes (13): BaseLLMService, ABC, Abstract LLM service base — allows future provider swapping., Provider-agnostic LLM service interface. Implementations must never let a…, Return a validated NextQuestionDecision or raise LLMUnavailableError. The…, Return structured AnswerExtraction or raise LLMUnavailableError.…, _contains_prohibited_content(), OpenAI LLM service via LangChain (Phase 5B). Architecture: ClinicalContext /… (+5 more)

### Community 73 - "NextQuestionDecision"
Cohesion: 0.33
Nodes (13): NextQuestionDecision, Structured LLM output for adaptive next-question selection. Advisory only —…, _make_ctx(), Construct an OpenAIService with a mocked underlying ChatOpenAI., _service(), test_01_successful_next_question_decision(), test_02_non_conforming_output_raises_unavailable(), test_03_timeout_raises_unavailable() (+5 more)

### Community 75 - "_settings_ctx"
Cohesion: 0.67
Nodes (3): Patch the settings object as seen by the OpenAI service module., _settings_ctx(), test_10_missing_api_key_raises()

## Knowledge Gaps
- **136 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+131 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `utcnow()` connect `utcnow` to `test_auth.py`, `system_service.py`, `endpoints/identity.py`, `Base`, `patients.py`, `session_service.py`, `test_interview.py`, `SessionService`, `datetime.py`, `AuthService`, `question_service.py`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Why does `AnswerExtraction` connect `test_llm_service.py` to `ClinicalContext`, `question_service.py`, `test_interview.py`, `OpenAIService`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Why does `create_app()` connect `test_sessions.py` to `test_auth.py`, `test_interview.py`, `endpoints/identity.py`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `QuestionService` (e.g. with `AnswerService` and `Answer`) actually correct?**
  _`QuestionService` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `NextQuestionDecision` (e.g. with `BaseLLMService` and `OpenAIService`) actually correct?**
  _`NextQuestionDecision` has 7 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `private`, `version` to the rest of the system?**
  _136 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `MediKiosk` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._