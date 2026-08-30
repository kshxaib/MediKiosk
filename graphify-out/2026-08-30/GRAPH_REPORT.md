# Graph Report - MediKiosk  (2026-08-30)

## Corpus Check
- 161 files · ~70,516 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1176 nodes · 2577 edges · 75 communities (58 shown, 17 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 120 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `474d1c9d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- MediKiosk
- test_auth.py
- system_service.py
- What You Must Do When Invoked
- devDependencies
- AppRoutes.tsx
- AuthService
- compilerOptions
- compilerOptions
- Frontend Entry and Documentation
- test_interview.py
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
- dependencies
- patients.py
- OpenAIService
- QuestionInput.tsx
- ConfigService
- SessionService
- test_sessions.py
- QuestionService
- types/index.ts
- auth_service.py
- question_service.py
- useSessionStore.ts
- ClinicalPolicy
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
- ClinicalContext
- test_health.py
- stores/index.ts
- core/config.py
- usePatientStore.ts
- conftest.py
- AnswerExtraction
- SystemStatusPage.tsx
- main.tsx

## God Nodes (most connected - your core abstractions)
1. `QuestionService` - 30 edges
2. `AnswerExtraction` - 30 edges
3. `Base` - 29 edges
4. `UUIDPrimaryKeyMixin` - 28 edges
5. `NextQuestionDecision` - 28 edges
6. `utcnow()` - 27 edges
7. `User` - 26 edges
8. `TimestampMixin` - 24 edges
9. `_next()` - 23 edges
10. `SessionService` - 22 edges

## Surprising Connections (you probably didn't know these)
- `login()` --uses--> `LoginRequest`  [INFERRED]
  backend/app/api/v1/endpoints/auth.py → backend/app/schemas/auth.py
- `refresh_token()` --uses--> `AuthService`  [INFERRED]
  backend/app/api/v1/endpoints/auth.py → backend/app/services/auth/auth_service.py
- `logout()` --uses--> `User`  [INFERRED]
  backend/app/api/v1/endpoints/auth.py → backend/app/models/user.py
- `get_current_staff_profile()` --uses--> `User`  [INFERRED]
  backend/app/api/v1/endpoints/auth.py → backend/app/models/user.py
- `get_stream_workflows()` --uses--> `WorkflowService`  [INFERRED]
  backend/app/api/v1/endpoints/streams.py → backend/app/services/interview/workflow_service.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Clinical Intake Flow** — identity_provider_abstraction, ai_clinical_assistant, ocr_extraction_pipeline [EXTRACTED 0.95]

## Communities (75 total, 17 thin omitted)

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
Cohesion: 0.18
Nodes (18): Container(), ContainerProps, HomePage(), LoginPage(), NotFoundPage(), ConsentPage(), DepartmentPage(), FacePage() (+10 more)

### Community 6 - "AuthService"
Cohesion: 0.21
Nodes (11): login(), Authenticate a staff user and issue JWT Access and Refresh tokens., Response returned upon successful login., TokenResponse, AuthService, Session, User, Handles staff authentication, token issuance, and token refresh. (+3 more)

### Community 7 - "compilerOptions"
Cohesion: 0.08
Nodes (24): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection, moduleResolution (+16 more)

### Community 8 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, moduleResolution, noEmit (+12 more)

### Community 10 - "test_interview.py"
Cohesion: 0.08
Nodes (66): classify_questions(), Any, Sort unanswered questions into (pending, refinements, skipped). Pure function…, _answer(), client(), _fake_llm(), initialized_session(), _new_session() (+58 more)

### Community 11 - "endpoints/auth.py"
Cohesion: 0.10
Nodes (28): get_current_staff_profile(), logout(), get, post, Session, User, Staff Authentication endpoints., Exchange a valid refresh token for a new access token. (+20 more)

### Community 12 - "User"
Cohesion: 0.08
Nodes (28): get_current_active_user(), get_current_user(), get_db(), Session, User, Shared FastAPI dependencies and RBAC security guards., Yield a request-scoped database session and always close it., Validate Bearer access token and return the authenticated User. (+20 more)

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
Nodes (41): enroll_face(), _extract_image_bytes(), post, Session, Patient Biometric Identity API Endpoints., Extract raw image bytes from data URI or raw base64 string., Extracts face embedding from webcam capture and stores active FaceEnrollment., Compares live webcam capture with enrolled biometric. Returns verified=True on… (+33 more)

### Community 37 - "dependencies"
Cohesion: 0.18
Nodes (11): axios, dependencies, axios, react, react-dom, react-router-dom, zustand, react (+3 more)

### Community 38 - "patients.py"
Cohesion: 0.05
Nodes (52): create_patient(), get_patient(), lookup_patient_by_mobile(), get, patch, post, Session, UUID (+44 more)

### Community 39 - "OpenAIService"
Cohesion: 0.09
Nodes (24): BaseLLMService, LLMUnavailableError, ABC, Exception, Abstract LLM service base — allows future provider swapping., Raised when the LLM provider is unavailable or returns invalid output. The…, Provider-agnostic LLM service interface. Implementations must never let a…, Return structured AnswerExtraction or raise LLMUnavailableError.… (+16 more)

### Community 40 - "QuestionInput.tsx"
Cohesion: 0.24
Nodes (12): KEYS, NumericKeypad(), NumericKeypadProps, numericBounds(), QuestionInput(), QuestionInputProps, SubmittedAnswer, toOptionList() (+4 more)

### Community 41 - "ConfigService"
Cohesion: 0.08
Nodes (36): list_department_consultants(), list_departments(), get, Session, UUID, Department configuration endpoints., list_languages(), get (+28 more)

### Community 42 - "SessionService"
Cohesion: 0.17
Nodes (28): clear_session(), complete_session(), create_session(), get_consents(), get_session(), get, patch, post (+20 more)

### Community 43 - "test_sessions.py"
Cohesion: 0.06
Nodes (54): AppError, Exception, FastAPI, Application error type and centralized exception handling. A single…, Base class for expected, handled application errors., register_exception_handlers(), create_app(), FastAPI (+46 more)

### Community 45 - "QuestionService"
Cohesion: 0.07
Nodes (38): get_next_question(), get_session_answers(), AnswerSubmissionResponse, get, post, Session, UUID, Clinical Interview AI Foundation API endpoints (Phase 5B). (+30 more)

### Community 46 - "types/index.ts"
Cohesion: 0.19
Nodes (12): env, apiClient, TOKEN_KEY, AuthState, SystemState, HealthResponse, PublicConfig, AuthResponse (+4 more)

### Community 48 - "auth_service.py"
Cohesion: 0.22
Nodes (14): Staff authentication service., Auth services package., create_access_token(), create_refresh_token(), decode_token(), Any, UUID, JWT token creation, validation, and extraction using PyJWT. (+6 more)

### Community 49 - "question_service.py"
Cohesion: 0.05
Nodes (77): Alembic migration environment. The database URL is pulled from application…, Base, Declarative base and shared metadata. A consistent naming convention makes…, Reusable model mixins (infrastructure only — no tables defined here). These…, Adds a UUID ``id`` primary key (never a mobile number / RFID / biometric)., Adds UTC ``created_at`` / ``updated_at`` columns., TimestampMixin, UUIDPrimaryKeyMixin (+69 more)

### Community 50 - "useSessionStore.ts"
Cohesion: 0.32
Nodes (12): SessionState, AnswerPayload, AnswerSubmissionResponse, NextQuestion, ConsentRecord, ConsentSubmitPayload, Department, IntakeSession (+4 more)

### Community 51 - "ClinicalPolicy"
Cohesion: 0.09
Nodes (26): build_refinement_question(), ClinicalPolicy, _match_option(), _match_yes_no(), normalize_category(), policy_for_workflow(), Any, Clinical fact and category reasoning for the adaptive questioning engine. This… (+18 more)

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
Cohesion: 0.18
Nodes (20): NextQuestionDecision, Structured LLM output for adaptive next-question selection. Advisory only —…, _make_ctx(), Phase 5B LLM service tests — OpenAI, fully mocked (no real API calls). The live…, Patch the settings object as seen by the OpenAI service module., Construct an OpenAIService with a mocked underlying ChatOpenAI., _service(), _settings_ctx() (+12 more)

### Community 66 - "ClinicalContext"
Cohesion: 0.15
Nodes (11): Return a validated NextQuestionDecision or raise LLMUnavailableError. The…, Build a compact, token-bounded clinical context message. Unlike v1, structured…, ClinicalContext, Compact clinical context passed to the LLM. Token budget is kept minimal — we…, v1 built the answer line as ``raw_answer or normalized_answer``, so for text…, test_07_known_facts_are_rendered_into_the_prompt(), Live OpenAI smoke test (Phase 5B). Behaviour required of this file: - No…, Real API call for adaptive question selection. Any failure fails the test. (+3 more)

### Community 67 - "test_health.py"
Cohesion: 0.22
Nodes (8): _failing_db(), _FailingSession, _ok_db(), _OkSession, TestClient, Tests for GET /api/v1/health. The DB session dependency is overridden with…, test_health_ok(), test_health_reports_503_when_db_down()

### Community 68 - "stores/index.ts"
Cohesion: 0.36
Nodes (5): Navbar(), ProtectedRoute(), ProtectedRouteProps, RootLayout(), useAuthStore

### Community 69 - "core/config.py"
Cohesion: 0.29
Nodes (5): get_settings(), Centralized application configuration. All runtime configuration is read from…, True only when a non-empty LLM API key is configured., Settings, BaseSettings

### Community 70 - "usePatientStore.ts"
Cohesion: 0.57
Nodes (6): PatientState, FaceEnrollResponse, FaceVerifyResponse, Patient, PatientCreatePayload, PatientLookupResponse

### Community 71 - "conftest.py"
Cohesion: 0.20
Nodes (11): Drop the cached service. Used by tests and after a config reload., reset_llm_service(), client(), disable_live_llm_for_unit_tests(), fixture, TestClient, Shared pytest fixtures. Tests exercise the API through FastAPI's ``TestClient``., Disable live LLM network calls during unit/integration tests. Guarantees fast,… (+3 more)

### Community 72 - "AnswerExtraction"
Cohesion: 0.09
Nodes (24): Run bounded LLM extraction. Raises LLMUnavailableError on failure., AnswerExtraction, ExtractedFact, PreviousAnswerSummary, Any, BaseModel, Structured Pydantic schemas for LLM input/output (Phase 5B). These are INTERNAL…, One normalized clinical key/value pair extracted from a patient answer. (+16 more)

### Community 73 - "SystemStatusPage.tsx"
Cohesion: 0.38
Nodes (4): StatusBadge(), StatusBadgeProps, SystemStatusPage(), useSystemStore

## Knowledge Gaps
- **139 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+134 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `utcnow()` connect `question_service.py` to `test_auth.py`, `system_service.py`, `endpoints/identity.py`, `patients.py`, `AuthService`, `SessionService`, `QuestionService`, `auth_service.py`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Why does `QuestionService` connect `QuestionService` to `AnswerExtraction`, `question_service.py`, `ClinicalContext`, `test_interview.py`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Why does `Patient` connect `question_service.py` to `SessionService`, `endpoints/identity.py`, `patients.py`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `QuestionService` (e.g. with `AnswerService` and `Answer`) actually correct?**
  _`QuestionService` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `AnswerExtraction` (e.g. with `AnswerService` and `BaseLLMService`) actually correct?**
  _`AnswerExtraction` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `NextQuestionDecision` (e.g. with `BaseLLMService` and `OpenAIService`) actually correct?**
  _`NextQuestionDecision` has 7 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `private`, `version` to the rest of the system?**
  _139 weakly-connected nodes found - possible documentation gaps or missing edges._