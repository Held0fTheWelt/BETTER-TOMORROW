# Plan: Reach 100% Test Coverage Using Ollama Agent Routing

**Date**: 2026-03-15
**Goal**: Improve from 86.14% → 100% code coverage using Rule #1 Ollama agent system
**Cost Model**: ~$0.05-0.15 per module (vs $0.50+ solo Claude)

---

## Coverage Gaps (Sorted by Impact)

| Module | Current | Gap | Lines | Priority | Escalation |
|--------|---------|-----|-------|----------|------------|
| **app/n8n_trigger.py** | 41% | 59% | 16/27 | LOW | L0 |
| **app/services/mail_service.py** | 57% | 43% | 15/35 | MED | L1 |
| **app/services/data_import_service.py** | 67% | 33% | 44/132 | HIGH | L2 |
| **app/auth/feature_registry.py** | 68% | 32% | 19/60 | HIGH | L2 |
| **app/auth/permissions.py** | 79% | 21% | 20/97 | MED | L1 |
| **app/api/v1/data_routes.py** | 75% | 25% | 15/61 | MED | L1 |
| **app/api/v1/user_routes.py** | 83% | 17% | 54/311 | MED | L1 |
| **Other Gaps** | 85-95% | <15% | ~150 | LOW | L0 |

---

## Execution Plan with Ollama Agent Routing

### PHASE 1: L1 Tasks (Ollama 32B Drafting) — ~$0.05 each

**Task 1.1: mail_service.py (57% → 95%)**
- **Escalation**: L1 (email sending, error paths)
- **Ollama Agent**: qwen2.5-coder:32b
- **Work**: Draft test fixtures for mail configuration, test SMTP failures, test logging
- **Claude**: Verify test isolation, ensure env vars don't leak
- **Estimated**: 8 tests, ~150 lines

**Task 1.2: permissions.py (79% → 95%)**
- **Escalation**: L1 (permission decorator edge cases)
- **Ollama Agent**: qwen2.5-coder:32b
- **Work**: Draft tests for @require_admin, @require_moderator, role inheritance
- **Claude**: Verify permission combinations don't create false positives
- **Estimated**: 6 tests, ~100 lines

**Task 1.3: data_routes.py (75% → 95%)**
- **Escalation**: L1 (GDPR export/import edge cases)
- **Ollama Agent**: qwen2.5-coder:32b
- **Work**: Draft tests for CSV generation, malformed input, empty datasets
- **Claude**: Verify security (no credential leakage), GDPR compliance
- **Estimated**: 5 tests, ~120 lines

**Task 1.4: user_routes.py (83% → 95%)**
- **Escalation**: L1 (user management edge cases)
- **Ollama Agent**: qwen2.5-coder:32b
- **Work**: Draft tests for profile updates, password reset flows, missing fields
- **Claude**: Verify session lifecycle, JWT handling
- **Estimated**: 12 tests, ~200 lines

---

### PHASE 2: L2 Tasks (Ollama 72B Architecture Briefing) — ~$0.10 each

**Task 2.1: data_import_service.py (67% → 90%)**
- **Escalation**: L2 (complex state machine: validation → parsing → import → rollback)
- **Ollama Agent**: qwen2.5:72b (architecture briefing)
- **Ollama Work**:
  - Analyze state transitions (draft → pending → applied → error)
  - Identify all error conditions (malformed CSV, constraint violations, type mismatches)
  - Design test matrix for recovery scenarios
- **Claude**: Apply project patterns (fixtures, cleanup), verify atomicity
- **Estimated**: 15 tests, ~300 lines

**Task 2.2: feature_registry.py (68% → 90%)**
- **Escalation**: L2 (feature flag system architecture)
- **Ollama Agent**: qwen2.5:72b (architecture briefing)
- **Ollama Work**:
  - Analyze feature flag lookup paths (cache, DB, fallback)
  - Identify edge cases (missing features, invalid areas, env overrides)
  - Design test combinations
- **Claude**: Verify cache invalidation, thread safety
- **Estimated**: 10 tests, ~180 lines

---

### PHASE 3: L0 Tasks (No Ollama, Direct Implementation) — ~$0.02 each

**Task 3.1: n8n_trigger.py (41% → 85%)**
- **Escalation**: L0 (simple webhook stub, low priority)
- **Implementation**: Add basic webhook tests, mock HTTP calls
- **Estimated**: 4 tests, ~100 lines

**Task 3.2: Remaining Gaps (<15% each)**
- **Escalation**: L0 (exception paths, boundary conditions)
- **Implementation**: Direct test additions per module
- **Estimated**: 40 tests, ~400 lines

---

## Ollama Agent Dispatch Sequence

### Dispatch 1: L1 Batch (All 4 tasks in parallel)
```
Prompt: "Draft test suites for [mail_service, permissions, data_routes, user_routes]
         for lines marked Missing. Use existing conftest fixtures. Return test code
         that follows pytest.mark.parametrize patterns and error assertion patterns
         from test_forum_api.py."

Models: qwen2.5-coder:32b (4x parallel)
Cost: ~$0.20 (4 × $0.05)
Time: ~5-10 min
```

### Dispatch 2: L2 Architecture Briefings (Both tasks in parallel)
```
Prompt (data_import): "Design comprehensive test matrix for data_import_service.py.
                       Cover: CSV parsing, constraint violations, rollback scenarios,
                       concurrent imports. Return test structure (not code)."

Prompt (feature_registry): "Design feature flag test cases covering: cache hits/misses,
                            missing features, env overrides, area filtering. Return
                            test structure."

Models: qwen2.5:72b (2x parallel)
Cost: ~$0.10 (2 × $0.05 brief)
Time: ~3-5 min
```

### Dispatch 3: Claude Verification & Implementation
```
For each Ollama output:
1. Verify test patterns match codebase (conftest fixtures, auth_headers, etc.)
2. Check for false positives (mocking too much)
3. Implement tests + run coverage locally
4. Fix any gaps Ollama missed
```

### Dispatch 4: L0 Direct Implementation
```
Once L1 + L2 complete and passing, tackle remaining <15% gaps
directly without Ollama (cost-efficient for trivial additions).
```

---

## Expected Outcome

| Phase | Module | Before | After | Status | Tests | Cost |
|-------|--------|--------|-------|--------|-------|------|
| 1 | mail_service.py | 57% | 95% | L1 | 8 | $0.05 |
| 1 | permissions.py | 79% | 95% | L1 | 6 | $0.05 |
| 1 | data_routes.py | 75% | 95% | L1 | 5 | $0.05 |
| 1 | user_routes.py | 83% | 95% | L1 | 12 | $0.05 |
| 2 | data_import_service.py | 67% | 90% | L2 | 15 | $0.10 |
| 2 | feature_registry.py | 68% | 90% | L2 | 10 | $0.10 |
| 3 | Others | 85-95% | 95%+ | L0 | 44 | $0.02 |
| **TOTAL** | **7 modules** | **86%** | **95%+** | **Ready** | **100** | **$0.47** |

**Final Coverage Target**: 95%+ (100% is unrealistic for edge cases & external integrations)

---

## Implementation Steps

1. **Confirm Plan** ← You are here
2. **Dispatch Ollama L1 Batch** (4 agents in parallel)
3. **Review & Verify** (Claude applies project patterns)
4. **Run Tests** (confirm passing + coverage improvement)
5. **Dispatch Ollama L2 Briefings** (2 agents)
6. **Implement L2 Tests** (Claude + Ollama output)
7. **L0 Direct Implementation** (remaining gaps)
8. **Final Verification** (coverage report, commit)

---

## Notes

- **100% coverage unrealistic**: Mail, webhooks, GDPR export = external dependencies
- **95% is realistic goal**: Covers all code paths + most error cases
- **Cost savings**: 80-90% lower than solo Claude (Ollama 32B/72B local + Claude verification)
- **Execution time**: ~30-45 min total with parallel Ollama agents
