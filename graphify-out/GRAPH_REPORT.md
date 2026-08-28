# Graph Report - MediKiosk  (2026-08-28)

## Corpus Check
- 66 files · ~21,563 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 337 nodes · 386 edges · 36 communities (28 shown, 8 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 6 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a1851c03`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- MediKiosk
- package.json
- system_service.py
- What You Must Do When Invoked
- devDependencies
- SystemStatusPage.tsx
- test_health.py
- compilerOptions
- compilerOptions
- Frontend Entry and Documentation
- main.py
- useSystemHealth.ts
- env.py
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

## God Nodes (most connected - your core abstractions)
1. `compilerOptions` - 19 edges
2. `compilerOptions` - 17 edges
3. `What You Must Do When Invoked` - 12 edges
4. `/graphify` - 11 edges
5. `get_health()` - 9 edges
6. `graphify reference: extra exports and benchmark` - 8 edges
7. `MediKiosk` - 8 edges
8. `health()` - 7 edges
9. `PublicConfig` - 7 edges
10. `Project Requirement` - 7 edges

## Surprising Connections (you probably didn't know these)
- `public_config()` --uses--> `PublicConfig`  [INFERRED]
  backend/app/api/v1/endpoints/config.py → backend/app/schemas/system.py
- `health()` --uses--> `HealthResponse`  [INFERRED]
  backend/app/api/v1/endpoints/health.py → backend/app/schemas/system.py
- `SystemStatusPage()` --calls--> `useSystemHealth()`  [EXTRACTED]
  frontend/src/pages/SystemStatusPage.tsx → frontend/src/hooks/useSystemHealth.ts
- `Frontend Entry Point` --references--> `Frontend README`  [INFERRED]
  frontend/index.html → frontend/README.md
- `public_config()` --calls--> `get_public_config()`  [EXTRACTED]
  backend/app/api/v1/endpoints/config.py → backend/app/services/system_service.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Clinical Intake Flow** — identity_provider_abstraction, ai_clinical_assistant, ocr_extraction_pipeline [EXTRACTED 0.95]

## Communities (36 total, 8 thin omitted)

### Community 0 - "MediKiosk"
Cohesion: 0.11
Nodes (17): AI Clinical Assistant, Cloudinary Document Pipeline, Identity Provider Abstraction, OCR & Extraction Pipeline, PostgreSQL Schema, Project Requirement, 1. Start PostgreSQL, 2. Backend (+9 more)

### Community 1 - "package.json"
Cohesion: 0.12
Nodes (16): dependencies, react, react-dom, react-router-dom, name, private, scripts, build (+8 more)

### Community 2 - "system_service.py"
Cohesion: 0.07
Nodes (35): public_config(), get, PublicConfig, Public (non-secret) configuration endpoint consumed by the frontend., health(), get, HealthResponse, Session (+27 more)

### Community 3 - "What You Must Do When Invoked"
Cohesion: 0.07
Nodes (26): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+18 more)

### Community 4 - "devDependencies"
Cohesion: 0.07
Nodes (29): eslint, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, devDependencies, eslint, @eslint/js, eslint-plugin-react-hooks (+21 more)

### Community 5 - "SystemStatusPage.tsx"
Cohesion: 0.17
Nodes (12): Container(), ContainerProps, StatusBadge(), StatusBadgeProps, NAV_ITEMS, RootLayout(), rootElement, HomePage() (+4 more)

### Community 6 - "test_health.py"
Cohesion: 0.10
Nodes (17): get_db(), Session, Shared FastAPI dependencies., Yield a request-scoped database session and always close it., get_settings(), Centralized application configuration. All runtime configuration is read from…, Settings, Database engine and session factory. Creating the engine does not open a… (+9 more)

### Community 7 - "compilerOptions"
Cohesion: 0.08
Nodes (24): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection, moduleResolution (+16 more)

### Community 8 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, moduleResolution, noEmit (+12 more)

### Community 10 - "main.py"
Cohesion: 0.15
Nodes (13): AppError, FastAPI, Application error type and centralized exception handling. A single…, Base class for expected, handled application errors., register_exception_handlers(), create_app(), FastAPI, FastAPI application entry point. Builds the app via a factory so it can be… (+5 more)

### Community 11 - "useSystemHealth.ts"
Cohesion: 0.31
Nodes (9): env, SystemHealthState, useSystemHealth(), apiRequest(), RequestOptions, getHealth(), getPublicConfig(), HealthResponse (+1 more)

### Community 12 - "env.py"
Cohesion: 0.22
Nodes (5): Alembic migration environment. The database URL is pulled from application…, Base, Declarative base and shared metadata. A consistent naming convention makes…, SQLAlchemy ORM models. Phase 1 intentionally defines NO business tables.…, DeclarativeBase

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

## Knowledge Gaps
- **131 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+126 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `devDependencies` connect `devDependencies` to `package.json`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Why does `get_db()` connect `test_health.py` to `system_service.py`?**
  _High betweenness centrality (0.007) - this node is a cross-community bridge._
- **What connects `name`, `private`, `version` to the rest of the system?**
  _131 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `MediKiosk` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.11764705882352941 - nodes in this community are weakly interconnected._
- **Should `system_service.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07293868921775898 - nodes in this community are weakly interconnected._
- **Should `What You Must Do When Invoked` be split into smaller, more focused modules?**
  _Cohesion score 0.07407407407407407 - nodes in this community are weakly interconnected._