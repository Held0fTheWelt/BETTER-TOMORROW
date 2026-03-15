# Plan: Pure Ollama Agent Execution via Clockwork Integration

**Date**: 2026-03-15
**Status**: Planning
**Objective**: Replace fake Claude agents with true Ollama agent dispatch using Clockwork system

---

## Problem Statement

**Current State:**
- Using Claude Code Agent tool → dispatches Claude subagents (not Ollama)
- Calling them "Ollama agents" was incorrect nomenclature
- No access to actual Ollama model execution

**Desired State:**
- True Ollama model execution (qwen2.5:32b, qwen2.5:72b, etc.)
- Proper Rule #1 implementation with local-first architecture
- Clockwork system for agent orchestration, contracts, and governance

---

## Architecture: Clockwork Integration

### System Overview
```
WorldOfShadows Project
├── .clockwork_integration/      (← Copied Clockwork system)
│   ├── claudeclockwork/         (Python package)
│   ├── .claude/                 (Governance + agent definitions)
│   │   ├── agents/              (Worker definitions)
│   │   ├── skills/              (109+ manifest skills)
│   │   ├── contracts/           (JSON schemas)
│   │   └── tools/               (Skill runners)
│   └── README.md                (Framework docs)
├── backend/                     (WorldOfShadows app)
├── PLAN_PURE_OLLAMA_AGENTS.md   (← This file)
└── INTEGRATION_STATUS.md        (To track implementation)
```

### Key Components to Implement

| Component | Location | Purpose | Status |
|-----------|----------|---------|--------|
| **OllamaWorker** | `claudeclockwork/workers/ollama_worker.py` | Direct Ollama model invocation | ❌ TODO |
| **OllamaRouter** | `claudeclockwork/router/ollama_router.py` | Route tasks to local Ollama | ❌ TODO |
| **Ollama Client** | `claudeclockwork/localai/ollama_client.py` | HTTP wrapper for Ollama API | ❌ TODO |
| **Agent Skills** | `.claude/skills/ollama_*.md` | Skill definitions for Ollama agents | ❌ TODO |
| **Skill Runners** | `.claude/tools/skills/ollama_*.py` | Executable skill scripts | ❌ TODO |
| **CLI Integration** | `claudeclockwork/cli/ollama_commands.py` | `--model qwen2.5:32b` CLI flag | ❌ TODO |

---

## Task Breakdown

### Phase 1: Core Infrastructure (Setup)

**Task 1.1: Verify Clockwork System**
- Check if `.clockwork_integration/` copy completed successfully
- Verify `claudeclockwork/` Python package is functional
- Test Ollama connectivity (already running on localhost:11434)
- Confirm 19 models available

**Task 1.2: Set Up Ollama Client**
- Create `claudeclockwork/localai/ollama_client.py`:
  - HTTP wrapper for Ollama API (`http://localhost:11434/api/generate`)
  - Response streaming support
  - Error handling for connection failures
  - Model availability check
- Add to `claudeclockwork/localai/__init__.py` exports

**Task 1.3: Create OllamaWorker**
- Create `claudeclockwork/workers/ollama_worker.py`:
  - Implements Worker interface (from `claudeclockwork/core/executor/executor.py`)
  - Takes prompt + model name + config
  - Calls OllamaClient
  - Returns structured result (model, tokens, latency, output)
- Register in worker registry

---

### Phase 2: Routing & Dispatch (Integration)

**Task 2.1: Create OllamaRouter**
- Create `claudeclockwork/router/ollama_router.py`:
  - Parses task escalation level (L0-L5)
  - Selects appropriate model based on complexity:
    - L0: no Ollama (skip)
    - L1: qwen2.5-coder:32b or phi4:14b
    - L2: qwen2.5:72b or llama3.3:70b
    - L3+: escalate to Claude API
  - Returns (worker_type, model, config)
- Integrate with existing router in `claudeclockwork/router/`

**Task 2.2: Update Executor**
- Modify `claudeclockwork/core/executor/executor.py`:
  - Add `model` parameter to execution context
  - Route to OllamaWorker if model specified
  - Fall back to Claude if Ollama unavailable
- Add Ollama error handling (retry logic, fallback)

**Task 2.3: CLI Integration**
- Update `claudeclockwork/cli/main.py`:
  - Add `--model <name>` flag (e.g., `--model qwen2.5:32b`)
  - Add `--ollama-only` flag (pure Ollama, fail if unavailable)
  - Add `--check-ollama` command (verify Ollama connectivity)
- Example:
  ```bash
  python3 -m claudeclockwork.cli --model qwen2.5:32b --skill-id draft_tests --inputs '{...}'
  ```

---

### Phase 3: Skill Definitions (Governance)

**Task 3.1: Create Ollama Skill Definitions**
- Create `.claude/skills/ollama_code_draft.md`:
  - Skill: Draft code/tests using Ollama 32B model
  - Input contract: prompt, language, constraints
  - Output contract: code, tokens_used, model_name
- Create `.claude/skills/ollama_architecture_brief.md`:
  - Skill: Architecture analysis using Ollama 72B
  - Input: codebase_path, question
  - Output: architecture_doc, concerns, model_name
- Create `.claude/skills/ollama_code_review.md`:
  - Skill: Code review using Ollama 32B
  - Input: code, review_type
  - Output: issues[], suggestions[], model_name

**Task 3.2: Create Skill Runners**
- Create `.claude/tools/skills/ollama_draft_code.py`:
  - Script runner for OllamaWorker
  - Takes prompt from stdin or file
  - Calls Ollama, returns result as JSON
- Create `.claude/tools/skills/ollama_architecture_brief.py`
- Create `.claude/tools/skills/ollama_code_review.py`
- Pattern: Use `claudeclockwork/workers/dispatcher.py` for execution

**Task 3.3: Update Skill Registry**
- Update `.claude/config/skills.yaml`:
  - Register 3 new Ollama skills
  - Set escalation_level (L1 or L2)
  - Set preferred_models
- Example:
  ```yaml
  ollama_code_draft:
    skill_id: ollama_code_draft
    description: Draft code using local Ollama 32B model
    escalation_level: L1
    preferred_models: [qwen2.5-coder:32b, deepseek-coder:33b]
    input_contract: ollama_draft_input.schema.json
    output_contract: ollama_draft_output.schema.json
  ```

---

### Phase 4: Governance & Contracts (Validation)

**Task 4.1: Define Input/Output Contracts**
- Create `.claude/contracts/schemas/ollama_draft_input.schema.json`:
  ```json
  {
    "type": "object",
    "properties": {
      "prompt": {"type": "string", "minLength": 10},
      "language": {"enum": ["python", "javascript", "sql"]},
      "model": {"type": "string", "pattern": "^[a-z0-9:._-]+$"},
      "max_tokens": {"type": "integer", "minimum": 100, "maximum": 4096}
    },
    "required": ["prompt"]
  }
  ```
- Create `.claude/contracts/schemas/ollama_draft_output.schema.json`:
  ```json
  {
    "type": "object",
    "properties": {
      "output": {"type": "string"},
      "model": {"type": "string"},
      "tokens_used": {"type": "integer"},
      "latency_ms": {"type": "integer"}
    },
    "required": ["output", "model"]
  }
  ```

**Task 4.2: Update Governance Policies**
- Update `.claude/governance/execution_protocol.md`:
  - Clarify Ollama vs Claude decision criteria
  - Add Ollama-specific error handling
  - Define fallback behavior (Ollama → Claude)
- Update `.claude/governance/model_escalation_policy.md`:
  - Specify model selection per task complexity
  - Define cost model for Ollama (local $0) vs Claude

---

### Phase 5: Implementation (Use in WorldOfShadows)

**Task 5.1: Test Ollama Dispatch**
- Write `tests/test_ollama_worker.py`:
  - Test OllamaClient connectivity
  - Test model availability
  - Test prompt execution (small test)
  - Test error handling (connection failure)
- Run: `python3 -m pytest tests/test_ollama_worker.py -v`

**Task 5.2: Create Example Skill Execution**
- File: `examples/ollama_test_draft.py`
  - Example: Dispatch L1 task to Ollama 32B
  - Verify output contract compliance
  - Measure latency and token usage

**Task 5.3: Integrate with WorldOfShadows Project**
- Update `PLAN_100PCT_COVERAGE.md`:
  - Use Ollama dispatch instead of fake Claude agents
  - Replace all Agent tool calls with Clockwork CLI calls
- Create `scripts/ollama_dispatch.sh`:
  - Wrapper script for common Ollama tasks
  - Example: `./scripts/ollama_dispatch.sh draft_tests mail_service.py`

---

## Implementation Checklist

### Phase 1: Core Infrastructure
- [ ] Task 1.1: Verify Clockwork system copy
- [ ] Task 1.2: Implement OllamaClient
- [ ] Task 1.3: Implement OllamaWorker

### Phase 2: Routing & Dispatch
- [ ] Task 2.1: Implement OllamaRouter
- [ ] Task 2.2: Update Executor for Ollama support
- [ ] Task 2.3: Add CLI flags and commands

### Phase 3: Skill Definitions
- [ ] Task 3.1: Create skill definition files (3 skills)
- [ ] Task 3.2: Create skill runner scripts (3 runners)
- [ ] Task 3.3: Register skills in YAML

### Phase 4: Governance & Contracts
- [ ] Task 4.1: Define JSON schemas (input/output)
- [ ] Task 4.2: Update governance policies

### Phase 5: Implementation
- [ ] Task 5.1: Write unit tests
- [ ] Task 5.2: Create example execution
- [ ] Task 5.3: Integrate with WorldOfShadows

---

## Estimated Timeline

| Phase | Tasks | Est. Hours | Model |
|-------|-------|-----------|-------|
| 1 | 3 | 2-3h | Claude (setup) |
| 2 | 3 | 3-4h | Ollama 32B (routing) + Claude (verification) |
| 3 | 3 | 2-3h | Ollama 32B (runners) |
| 4 | 2 | 1-2h | Claude (contracts) |
| 5 | 3 | 2-3h | Ollama 32B (tests) + Claude (integration) |
| **TOTAL** | **14** | **10-15h** | **Mixed** |

---

## Success Criteria

✅ **Core Functionality:**
- [ ] `python3 -m claudeclockwork.cli --model qwen2.5:32b --skill-id ollama_code_draft --inputs '{"prompt": "..."}' ` returns valid output
- [ ] OllamaClient successfully communicates with Ollama on localhost:11434
- [ ] Router correctly selects models based on escalation level

✅ **Governance:**
- [ ] All Ollama skill outputs validate against defined schemas
- [ ] Execution protocol documents Ollama escalation paths
- [ ] Contracts ensure reproducibility

✅ **Integration:**
- [ ] `pytest tests/test_ollama_worker.py -v` all pass
- [ ] Example script executes and returns expected result
- [ ] WorldOfShadows test coverage plan uses Ollama dispatch

---

## Known Gaps

1. **Ollama Model Selection:** Need to validate all 19 available models; some may not support streaming
2. **Error Recovery:** Need robust fallback (Ollama unavailable → Claude)
3. **Cost Tracking:** Need telemetry for Ollama token usage (local cost = $0, but track for metrics)
4. **Skill Marketplace:** Clockwork has 109+ skills; may need custom skill definitions for test generation

---

## Next Step

**Immediate Action:**
1. Confirm `.clockwork_integration/` copy completed
2. Start with Task 1.1 (verify Clockwork system)
3. Then Task 1.2 (implement OllamaClient)
4. Iterate through phases in order

**User Confirmation Needed:**
- Approve implementation timeline?
- Any model preferences (qwen vs llama vs deepseek)?
- Priority: Phase 2 routing before Phase 3 skills?
