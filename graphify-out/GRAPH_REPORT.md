# Graph Report - MediKiosk  (2026-08-30)

## Corpus Check
- 174 files · ~81,169 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1364 nodes · 3220 edges · 92 communities (74 shown, 18 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 167 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `151e96cf`
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
- interview.py
- types/index.ts
- utcnow
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
- get_llm_service
- test_health.py
- stores/index.ts
- core/config.py
- usePatientStore.ts
- conftest.py
- AnswerExtraction
- SystemStatusPage.tsx
- main.tsx
- cases.py
- test_case_summary.py
- Base
- models/__init__.py
- session_service.py
- .build
- schemas.py
- InterviewState
- .record_answer
- QuestionService
- get_current_user
- ._reject_generated_question
- get_admin_dashboard_stats
- get_doctor_profile
- env.py
- schemas/question.py

## God Nodes (most connected - your core abstractions)
1. `Base` - 41 edges
2. `UUIDPrimaryKeyMixin` - 40 edges
3. `TimestampMixin` - 36 edges
4. `utcnow()` - 35 edges
5. `AnswerExtraction` - 33 edges
6. `QuestionService` - 30 edges
7. `IntakeSession` - 29 edges
8. `CaseSummaryService` - 28 edges
9. `NextQuestionDecision` - 28 edges
10. `Patient` - 26 edges

## Surprising Connections (you probably didn't know these)
- `get_current_user()` --uses--> `User`  [INFERRED]
  backend/app/api/deps.py → backend/app/models/user.py
- `get_current_active_user()` --uses--> `User`  [INFERRED]
  backend/app/api/deps.py → backend/app/models/user.py
- `get_admin_dashboard_stats()` --uses--> `User`  [INFERRED]
  backend/app/api/v1/endpoints/admin.py → backend/app/models/user.py
- `login()` --uses--> `LoginRequest`  [INFERRED]
  backend/app/api/v1/endpoints/auth.py → backend/app/schemas/auth.py
- `refresh_token()` --uses--> `RefreshTokenRequest`  [INFERRED]
  backend/app/api/v1/endpoints/auth.py → backend/app/schemas/auth.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Clinical Intake Flow** — identity_provider_abstraction, ai_clinical_assistant, ocr_extraction_pipeline [EXTRACTED 0.95]

## Communities (92 total, 18 thin omitted)

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
Cohesion: 0.16
Nodes (16): login(), Session, Authenticate a staff user and issue JWT Access and Refresh tokens., Exchange a valid refresh token for a new access token., refresh_token(), Response returned upon successful login., Response containing a renewed access token., TokenRefreshResponse (+8 more)

### Community 7 - "compilerOptions"
Cohesion: 0.08
Nodes (24): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection, moduleResolution (+16 more)

### Community 8 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, moduleResolution, noEmit (+12 more)

### Community 10 - "test_interview.py"
Cohesion: 0.08
Nodes (65): classify_questions(), Sort unanswered questions into (pending, refinements, skipped). Pure function…, _answer(), client(), _fake_llm(), initialized_session(), _new_session(), _next() (+57 more)

### Community 11 - "endpoints/auth.py"
Cohesion: 0.11
Nodes (23): get_current_staff_profile(), logout(), get, post, User, Staff Authentication endpoints., Acknowledge logout for the authenticated staff session., Return the profile and role of the currently authenticated staff member. (+15 more)

### Community 12 - "User"
Cohesion: 0.15
Nodes (12): Shared FastAPI dependencies and RBAC security guards., Dependency factory enforcing RBAC role permissions on route handlers., require_role(), Protected Admin demonstration routes., Protected Doctor demonstration routes., Database engine and session factory. Creating the engine does not open a…, Role ORM model for RBAC., Staff roles (e.g. ADMIN, DOCTOR). (+4 more)

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

### Community 39 - "OpenAIService"
Cohesion: 0.12
Nodes (14): _contains_prohibited_content(), OpenAIService, Any, Ask the model to select the next clinical question. Returns a validated…, Extract structured facts and satisfied categories from one answer. NOTE:…, Render the assembled structured summary as prose. The model receives ONLY the…, Log an LLM failure with the exception CLASS only — never its content. Provider…, Build a compact, token-bounded clinical context message. Unlike v1, structured… (+6 more)

### Community 40 - "QuestionInput.tsx"
Cohesion: 0.24
Nodes (12): KEYS, NumericKeypad(), NumericKeypadProps, numericBounds(), QuestionInput(), QuestionInputProps, SubmittedAnswer, toOptionList() (+4 more)

### Community 41 - "ConfigService"
Cohesion: 0.07
Nodes (38): get_db(), Yield a request-scoped database session and always close it., list_department_consultants(), list_departments(), get, Session, UUID, Department configuration endpoints. (+30 more)

### Community 42 - "SessionService"
Cohesion: 0.16
Nodes (29): clear_session(), complete_session(), create_session(), get_consents(), get_session(), get, patch, post (+21 more)

### Community 43 - "test_sessions.py"
Cohesion: 0.06
Nodes (54): AppError, Exception, FastAPI, Application error type and centralized exception handling. A single…, Base class for expected, handled application errors., register_exception_handlers(), create_app(), FastAPI (+46 more)

### Community 45 - "interview.py"
Cohesion: 0.17
Nodes (18): get_next_question(), get_session_answers(), AnswerSubmissionResponse, get, post, Session, UUID, Clinical Interview AI Foundation API endpoints (Phase 5B). (+10 more)

### Community 46 - "types/index.ts"
Cohesion: 0.19
Nodes (12): env, apiClient, TOKEN_KEY, AuthState, SystemState, HealthResponse, PublicConfig, AuthResponse (+4 more)

### Community 48 - "utcnow"
Cohesion: 0.20
Nodes (16): Staff authentication service., Auth services package., create_access_token(), create_refresh_token(), decode_token(), Any, UUID, JWT token creation, validation, and extraction using PyJWT. (+8 more)

### Community 49 - "question_service.py"
Cohesion: 0.14
Nodes (18): Answer, Clinically meaningful answer entity linked to an IntakeSession., ClinicalWorkflow, ClinicalWorkflow ORM model., Configurable clinical history & case-taking workflow., Question, Question ORM model for adaptive clinical intake., Question entity defined within a clinical workflow. (+10 more)

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
Cohesion: 0.17
Nodes (21): NextQuestionDecision, Structured LLM output for adaptive next-question selection. Advisory only —…, _make_ctx(), Phase 5B LLM service tests — OpenAI, fully mocked (no real API calls). The live…, Patch the settings object as seen by the OpenAI service module., Construct an OpenAIService with a mocked underlying ChatOpenAI., _service(), _settings_ctx() (+13 more)

### Community 66 - "get_llm_service"
Cohesion: 0.19
Nodes (12): LLMUnavailableError, Exception, Raised when the LLM provider is unavailable or returns invalid output. The…, _current_fingerprint(), get_llm_service(), LLM service package (Phase 5B). Exports: BaseLLMService - Provider-neutral…, Return the configured LLM service. The instance is cached because constructing…, Live OpenAI smoke test (Phase 5B). Behaviour required of this file: - No… (+4 more)

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
Nodes (22): Return structured AnswerExtraction or raise LLMUnavailableError.…, AnswerExtraction, ExtractedFact, PreviousAnswerSummary, Any, BaseModel, One normalized clinical key/value pair extracted from a patient answer., One symptom with the timing and severity that belong to THAT symptom. Keeping… (+14 more)

### Community 73 - "SystemStatusPage.tsx"
Cohesion: 0.38
Nodes (4): StatusBadge(), StatusBadgeProps, SystemStatusPage(), useSystemStore

### Community 75 - "cases.py"
Cohesion: 0.07
Nodes (46): create_case_edit(), generate_case_summary(), get_case(), get_case_summary_for_session(), list_case_edits(), get, post, Session (+38 more)

### Community 76 - "test_case_summary.py"
Cohesion: 0.12
Nodes (52): AlertType, DocumentType, ExtractionStatus, str, InformationSource, str, Canonical provenance values (§23). Used by timeline events and by every item in…, TimelineEventType (+44 more)

### Community 77 - "Base"
Cohesion: 0.13
Nodes (28): Base, Declarative base and shared metadata. A consistent naming convention makes…, Reusable model mixins (infrastructure only — no tables defined here). These…, Adds a UUID ``id`` primary key (never a mobile number / RFID / biometric)., Adds UTC ``created_at`` / ``updated_at`` columns., TimestampMixin, UUIDPrimaryKeyMixin, Alert (+20 more)

### Community 78 - "models/__init__.py"
Cohesion: 0.10
Nodes (28): AlertSeverity, AlertStatus, str, Case, CaseEdit, CaseStatus, EditorType, str (+20 more)

### Community 79 - "session_service.py"
Cohesion: 0.14
Nodes (15): Session, Safe development seeding for initial roles, dev staff accounts, hospitals,…, Idempotently seed default roles, test accounts, hospital, streams, and…, seed_database(), Department, Department ORM model., Hospital Department entity (GEN_MED, CARDIO, NEURO, etc.)., Hospital (+7 more)

### Community 80 - ".build"
Cohesion: 0.15
Nodes (15): _clean(), _entry_confidence(), _entry_label(), HistoricalContext, history_item(), Any, Session, UUID (+7 more)

### Community 81 - "schemas.py"
Cohesion: 0.15
Nodes (13): BaseLLMService, ABC, Any, Abstract LLM service base — allows future provider swapping., Provider-agnostic LLM service interface. Implementations must never let a…, Return a validated NextQuestionDecision or raise LLMUnavailableError. The…, Render an already-assembled structured case summary as prose. The model is a…, OpenAI LLM service via LangChain (Phase 5B). Architecture: ClinicalContext /… (+5 more)

### Community 82 - "InterviewState"
Cohesion: 0.18
Nodes (9): NextQuestionResponse, InterviewState, Everything needed to choose the next question, computed once per request., Human-readable satisfied categories, using this workflow's spellings., Fact-aware deterministic selection. Unlike v1 this is NOT "first unanswered by…, Ask the LLM, then re-validate its proposal against known facts., Ask the patient to refine a partially-known answer. The question keeps its real…, test_19_llm_used_defaults_false() (+1 more)

### Community 83 - ".record_answer"
Cohesion: 0.14
Nodes (11): AnswerSubmissionResponse, Any, Session, UUID, Validate, persist raw answer, then attempt bounded LLM extraction., Record which LLM-generated question this answer belongs to. Only used when…, Category vocabulary of the session's own workflow. Scoped to one workflow so…, Fold a successful extraction into the stored JSONB envelope. (+3 more)

### Community 84 - "QuestionService"
Cohesion: 0.40
Nodes (6): Session, UUID, QuestionService, Adaptive entry point: try the LLM, fall back to deterministic. Both paths…, Deterministic next-question — always safe, and fact-aware., True when anything is still worth asking (pending or refinement).

### Community 85 - "get_current_user"
Cohesion: 0.29
Nodes (7): get_current_active_user(), get_current_user(), Session, User, Validate Bearer access token and return the authenticated User., Ensure the authenticated user is currently active., HTTPAuthorizationCredentials

### Community 86 - "._reject_generated_question"
Cohesion: 0.29
Nodes (6): question_fingerprint(), Stable short fingerprint of a question, for repeat detection., _contains_prohibited(), Any, Return a rejection reason for a generated question, or None to allow. This is…, Shared with the LLM service validator (single keyword source of truth).

### Community 87 - "get_admin_dashboard_stats"
Cohesion: 0.40
Nodes (5): get_admin_dashboard_stats(), Any, get, User, Admin-only diagnostic endpoint verifying ADMIN RBAC role access.

### Community 88 - "get_doctor_profile"
Cohesion: 0.40
Nodes (5): get_doctor_profile(), Any, get, User, Doctor route verifying DOCTOR (or supervisory ADMIN) role access.

### Community 90 - "schemas/question.py"
Cohesion: 0.50
Nodes (3): BaseModel, QuestionRead, Question Pydantic schemas.

## Knowledge Gaps
- **139 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+134 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `utcnow()` connect `utcnow` to `test_auth.py`, `system_service.py`, `endpoints/identity.py`, `AuthService`, `patients.py`, `SessionService`, `cases.py`, `User`, `Base`, `models/__init__.py`, `session_service.py`, `test_case_summary.py`, `question_service.py`, `.record_answer`, `QuestionService`?**
  _High betweenness centrality (0.090) - this node is a cross-community bridge._
- **Why does `AnswerExtraction` connect `AnswerExtraction` to `test_llm_service.py`, `OpenAIService`, `test_interview.py`, `test_case_summary.py`, `schemas.py`, `question_service.py`, `.record_answer`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Why does `User` connect `User` to `test_auth.py`, `AuthService`, `endpoints/auth.py`, `Base`, `models/__init__.py`, `session_service.py`, `utcnow`, `get_current_user`, `get_admin_dashboard_stats`, `get_doctor_profile`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `AnswerExtraction` (e.g. with `AnswerService` and `BaseLLMService`) actually correct?**
  _`AnswerExtraction` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `private`, `version` to the rest of the system?**
  _139 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `MediKiosk` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._
- **Should `test_auth.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1282051282051282 - nodes in this community are weakly interconnected._