# Alternative Model Context Protocol (MCP) Implementation Plan

This document presents an alternative strategy for extending **BugIt** into a fully-featured Model Context Protocol (MCP) tool server.  It is intentionally more granular and opinionated than the original `MCP_PLAN.md` to expose design trade-offs and additional quality gates.

---
## Guiding Principles

1. **Separation of Concerns** – Business logic, I/O, and orchestration live in distinct layers.
2. **Composable Tools** – Each CLI capability becomes a *pure* function that can be wired into either the CLI or the MCP server.
3. **Backward Compatibility First** – All existing tests must pass after every phase.
4. **Observability & Resilience** – First-class logging, metrics, and error boundaries.
5. **Progressive Adoption** – Incremental rollout guarded by feature flags for rapid feedback.

---
## Phase 0  |  Foundations & House-Keeping

| # | Task | Success Criteria |
|---|------|-----------------|
|0.1|Create `mcp/` package with `__init__.py`.|Package importable, unit-tested.|
|0.2|Introduce shared type aliases & error classes (`mcp/types.py`, `mcp/errors.py`).|Interfaces compile under `mypy`.|
|0.3|Add `pre-commit` hooks (format, lint, type-check, security-scan).|CI passes on pristine checkout.|

---
## Phase 1  |  Business-Logic Extraction

1. **Refactor Command Modules**  
   • Move *all* non-I/O logic from each `commands/*.py` into `core/` or new `mcp/tools.py`.  
   • Publish a _functional_ API surface (no `click` types, no print statements).
2. **Add Fast Unit Tests** for each new tool function (happy & sad paths).
3. **Maintain CLI Parity** by thinly wrapping the new tool functions.

> 🔎 *Rationale:* Ensures deterministic behavior and makes subsequent phases almost mechanical glue work.

---
## Phase 2  |  MCP Server Skeleton

1. **Select Transport** – Use JSON-RPC 2.0 over stdio (mirrors original plan).  
2. **Implement Lifecycle RPCs**: `initialize`, `initialized`, `shutdown`, `exit`.
3. **Dynamic Tool Registry**  
   • Introspect `mcp.tools` via `inspect.getmembers` to auto-discover callables.  
   • Expose metadata (`name`, `description`, `parameters` in JSON Schema).
4. **Package Entry Point** – `python -m mcp.server` or `bugit server` sub-command.
5. **Add Smoke Tests** that spin up server in subprocess and fetch `tools/list`.

---
## Phase 3  |  Tool Wiring & Contracts

Repeat for each legacy command (order by usage frequency):

| Tool | CLI Source | New Function | Notes |
|------|------------|--------------|-------|
|`bugit/new`|`commands/new.py`|`mcp.tools.create_issue`|Validate description, persist, return record.|
|`bugit/list`|`commands/list.py`|`mcp.tools.list_issues`|Support filters & pagination.|
|`bugit/show`|`commands/show.py`|`mcp.tools.get_issue`|Return single issue; 404 on miss.|
|`bugit/edit`|`commands/edit.py`|`mcp.tools.update_issue`|Partial updates, optimistic-locking.|
|`bugit/delete`|`commands/delete.py`|`mcp.tools.delete_issue`|Soft-delete flag instead of hard remove.|
|`bugit/config`|`commands/config.py`|`mcp.tools.set_config`|Return updated config.|

> Each addition gated by a `@feature_flag("mcp_<tool>")` decorator for controlled rollout.

---
## Phase 4  |  Robustness & Observability

1. **Structured Logging** with correlation IDs per JSON-RPC request.
2. **Metrics Hooks** (`requests_total`, `errors_total`, `latency_ms`) surfaced via optional Prometheus exporter.
3. **Graceful Cancellation** – Handle `$/cancelRequest` from clients.
4. **Concurrency Model** – Process requests on a `ThreadPoolExecutor` to avoid blocking stdio.
5. **Security Review** – Static analysis (Bandit), dependency scanning, fuzz tests.

---
## Phase 5  |  Documentation & DX

1. **Docs Site** – Auto-generate OpenAPI-like catalog from tool registry.
2. **README Updates** – Quick-start, troubleshooting, and architecture diagrams.
3. **Example Clients** – Python snippet, shell script, and GitHub Actions example.

---
## Exit Criteria

- `pytest -q` → 100 % pass and ≥ 95 % coverage.
- Server can be discovered & invoked from external IDE plugin (manual sanity test).
- All performance tests meet existing Service-Level Objectives.
- No breaking changes to legacy CLI workflows.

---

## Appendix  |  Comparison to Original `MCP_PLAN.md`

| Aspect | Original Plan | Alternative Plan (this doc) |
|--------|---------------|------------------------------|
|**Pre-work**|Jumps directly into server skeleton.|Adds foundation phase for type-safety & tooling.|
|**Tool Discovery**|Hard-codes tool list.|Automated introspection registry.|
|**Feature Flags**|Not mentioned.|Present for incremental rollout.|
|**Observability**|Not emphasized.|Dedicated phase with metrics & logging.|
|**Concurrency**|Not discussed.|Explicit thread-pool handling.|
|**Security**|Implicit.|Dedicated security review & static analysis.|
|**Exit Criteria**|Per-phase user checkpoints.|Final holistic exit criteria incl. coverage & SLOs.|
|**Soft-Delete Strategy**|Delete removes record.|Implements reversible soft deletion.|
|**Docs & DX**|Update README.|Generates richer docs site & sample clients.|

---

**Next Steps**  
If this alternative roadmap aligns with project priorities, we can break down Phase 0 tasks into actionable tickets and schedule code pairing sessions. 