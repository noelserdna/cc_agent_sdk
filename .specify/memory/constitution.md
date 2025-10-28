<!--
SYNC IMPACT REPORT
==================
Version Change: [NONE] → 1.0.0
Rationale: Initial constitution creation for Claude Agent SDK project following agent-first development principles.

Modified Principles:
- New: I. Agent-First Development
- New: II. Verification-Driven Design
- New: III. Type Safety & Validation
- New: IV. Security by Default
- New: V. Observable & Auditable
- New: VI. Test-First for Autonomy
- New: VII. Custom Tools as APIs

Added Sections:
- Technical Standards
- Testing Requirements
- Performance Targets

Removed Sections:
- [None - initial creation]

Templates Status:
✅ plan-template.md: Constitution Check section verified - will reference new principles
✅ spec-template.md: Requirements structure aligns with agent-operable design
✅ tasks-template.md: Task structure supports verification-driven workflow
✅ agent-file-template.md: Will extract from plans following new standards
✅ checklist-template.md: Verification requirements compatible

Follow-up TODOs:
- [None]
-->

# Claude Agent SDK Constitution

## Core Principles

### I. Agent-First Development

Agents are autonomous actors, not scripted workflows. Design systems where agents gather context, take actions, verify results, and iterate independently. Agent-operable interfaces are mandatory for all production features.

**Rationale**: Autonomous agents require self-service APIs and verification mechanisms. Scripted workflows fail when context changes or unexpected conditions arise. Agent-first design ensures resilience and adaptability.

### II. Verification-Driven Design

Every agent operation includes built-in verification. Tools return explicit success/failure indicators. Agents validate their own work before completion. No "fire and forget" operations.

**Rationale**: Autonomous systems cannot rely on human verification loops. Operations must be self-validating to maintain reliability. Explicit verification prevents cascading failures and enables automatic recovery.

### III. Type Safety & Validation

TypeScript strict mode mandatory. All agent tool interfaces use Zod schemas. Runtime validation at every boundary. No `any` types without justification.

**Rationale**: Agents operate on dynamic inputs and external data. Type safety catches errors at compile time. Runtime validation with Zod ensures data integrity across boundaries and provides clear error messages for debugging.

### IV. Security by Default

Agents operate with least privilege. Permission modes are explicit (`default`, `acceptEdits`, `plan`, `bypassPermissions`). Dangerous operations require justification and audit logging via hooks.

**Rationale**: Autonomous agents can execute destructive operations. Explicit permission models prevent accidental harm. Audit logging via hooks enables compliance and forensic analysis.

### V. Observable & Auditable

All agent operations logged through hooks (`onPreToolUse`, `onPostToolUse`). Structured logging with PII redaction. Token usage tracked. Operations must be reproducible for debugging.

**Rationale**: Black-box agent behavior prevents debugging and improvement. Observable systems enable root cause analysis. Structured logs support analytics and compliance. Reproducibility is essential for regression testing.

### VI. Test-First for Autonomy

- **Tool handlers**: 100% unit test coverage (deterministic)
- **Agent workflows**: Integration tests with outcome validation (not exact wording)
- **Regression suites**: Recorded successful conversations
- Test behaviors and outcomes, not internal reasoning paths

**Rationale**: Agent reasoning varies between runs due to LLM non-determinism. Testing exact outputs fails. Behavior-based tests verify correctness while allowing reasoning flexibility. Recorded conversations serve as regression tests.

### VII. Custom Tools as APIs

Domain-specific logic lives in custom tools, not bash scripts. Tools are typed, validated, composable, and include verification strategies. Use built-in tools for generic operations.

**Rationale**: Bash scripts lack type safety, error handling, and composability. Custom tools provide structured interfaces, validation, and better error messages. This improves agent reliability and developer experience.

## Technical Standards

**Language & Runtime**:
- TypeScript 5.x with strict mode enabled
- Node.js LTS version (20.x or later)

**Validation & Type Safety**:
- Zod schemas for all tool inputs/outputs
- No `any` types without documented justification
- Exhaustive error handling on all async operations

**Code Quality**:
- ESLint + Prettier enforced (pre-commit hooks)
- Consistent code style across all modules
- Clear naming conventions (tools use verbs, types use nouns)

**Integration**:
- MCP (Model Context Protocol) servers for external integrations
- Tools must be composable and independently testable
- API responses include verification data

**Error Handling**:
- All async operations wrapped in try-catch
- Errors include context and actionable messages
- Graceful degradation when possible

## Testing Requirements

| Component       | Coverage | Method            | Enforcement          |
|-----------------|----------|-------------------|----------------------|
| Tool Handlers   | 100%     | Unit tests        | Pre-commit hook      |
| Agent Workflows | 80%      | Integration tests | CI pipeline          |
| Error Paths     | 100%     | Fault injection   | Pre-commit + CI      |

**Test Principles**:
- Write tests before implementation (TDD)
- Test behaviors, not implementation details
- Integration tests verify outcomes, not exact agent wording
- Regression tests based on recorded successful conversations
- All tests must be deterministic and reproducible

**Test Structure**:
```
tests/
├── unit/           # Tool handlers, utilities (100% coverage)
├── integration/    # End-to-end agent workflows (80% coverage)
├── fixtures/       # Test data and mocks
└── recordings/     # Successful conversation recordings
```

## Performance Targets

| Metric           | Target       | Measurement           |
|------------------|--------------|-----------------------|
| API Response Time| p95 < 30s    | Per-operation logging |
| Token Usage      | < 50k/op     | Hook-based tracking   |
| Error Rate       | < 5%         | Failure log analysis  |
| System Uptime    | 99%          | Health checks + alerts|

**Performance Monitoring**:
- Token usage tracked via `onPostToolUse` hooks
- Operation timing logged with structured metadata
- Error rates monitored per tool and workflow
- Performance regression tests in CI

**Optimization Guidelines**:
- Minimize token usage through concise prompts
- Cache frequently accessed data
- Use streaming responses for long operations
- Parallelize independent tool calls

## Governance

### Amendment Process

This constitution supersedes all other practices and documentation. Amendments require:

1. **Proposal**: Document proposed changes with rationale
2. **Review**: Team review of impact on existing systems
3. **Migration Plan**: Document required code changes and timeline
4. **Approval**: Consensus from core maintainers
5. **Version Update**: Semantic versioning (MAJOR.MINOR.PATCH)

### Version Semantics

- **MAJOR**: Backward incompatible governance/principle removals or redefinitions
- **MINOR**: New principle/section added or materially expanded guidance
- **PATCH**: Clarifications, wording improvements, typo fixes

### Compliance

- **All PRs**: Must verify compliance with these principles
- **Code Reviews**: Include constitution compliance check
- **Complexity**: Must be justified against simplicity (document in plan.md)
- **Violations**: Require documented justification in technical context section

### Runtime Development Guidance

For agent-specific development guidance (current technologies, project structure, active commands), refer to the auto-generated agent file. The constitution defines immutable principles; the agent file provides runtime context.

**Conflict Resolution**: Constitution principles always take precedence over convenience or historical patterns. When in doubt, choose the path that enhances agent autonomy, verification, and safety.

---

**Version**: 1.0.0 | **Ratified**: 2025-10-27 | **Last Amended**: 2025-10-27
