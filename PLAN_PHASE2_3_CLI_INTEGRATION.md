# Phase 2.3: CLI Flags & Commands - Implementation Plan

**Phase**: 2 (Routing & Dispatch)
**Task**: 2.3 (CLI Flags & Commands)
**Estimated Time**: 2-3 hours
**Status**: PLANNED (ready to implement)

---

## Objective

Integrate TaskExecutor into the Clockwork CLI by adding:
1. `--escalation-level` flag (specify task complexity)
2. `--model` and `--preferred-models` flags (manual model selection)
3. `--ollama-only` flag (force local execution, fail if unavailable)
4. `check-ollama` command (health verification)
5. CLI execution path integration

---

## Scope

### 1. New CLI Flags

#### `--escalation-level <level>` (Required for task execution)
```bash
# L1 task (code drafting) - default recommended
python3 -m claudeclockwork.cli --skill-id code_draft \
  --escalation-level 1 \
  --inputs '{"prompt": "Write tests"}'

# L2 task (architecture) - use larger model
python3 -m claudeclockwork.cli --skill-id arch_brief \
  --escalation-level 2 \
  --inputs '{"prompt": "Explain architecture"}'

# L0 task (skip execution)
python3 -m claudeclockwork.cli --skill-id verify \
  --escalation-level 0 \
  --inputs '{}'

# L3 task (defer to Claude)
python3 -m claudeclockwork.cli --skill-id perf_review \
  --escalation-level 3 \
  --inputs '{"prompt": "Review performance"}'
```

**Validation**:
- Accept: 0-5 or "L0"-"L5"
- Default: 1 (Team Lead)
- Invalid: Show error and suggest valid levels

#### `--model <model-name>` (Preferred Ollama model)
```bash
python3 -m claudeclockwork.cli --skill-id code_draft \
  --escalation-level 1 \
  --model qwen2.5-coder:32b \
  --inputs '{"prompt": "..."}'
```

**Behavior**:
- Use specified model if available
- Fall back to escalation-level defaults if unavailable
- Validate model against available list

#### `--preferred-models <model1>,<model2>,<model3>` (Ordered preference list)
```bash
python3 -m claudeclockwork.cli --skill-id arch_brief \
  --escalation-level 2 \
  --preferred-models "qwen2.5:72b,llama3.3:70b" \
  --inputs '{"prompt": "..."}'
```

**Behavior**:
- Try models in specified order
- Use first available
- Fall back to escalation-level defaults if none available

#### `--ollama-only` (Force local execution)
```bash
# Fail if Ollama unavailable (do not fall back to Claude)
python3 -m claudeclockwork.cli --skill-id code_draft \
  --escalation-level 1 \
  --ollama-only \
  --inputs '{"prompt": "..."}'
```

**Behavior**:
- If Ollama available: proceed with local execution
- If Ollama unavailable: fail with clear error message
- Do not fall back to Claude API
- Useful for cost-sensitive operations or offline environments

### 2. New CLI Command

#### `check-ollama` (Health verification)
```bash
# Check Ollama server health
python3 -m claudeclockwork.cli check-ollama

# Output:
# ✓ Ollama server: RUNNING
# ✓ Server: localhost:11434
# ✓ Available models: 19
# ✓ Sample models:
#   - qwen2.5-coder:32b (L1)
#   - qwen2.5:72b (L2)
#   - llama3.3:70b (L2)
#   ... (16 more)
# ✓ Total models loaded: 19
```

**Features**:
- Test Ollama server connection
- List available models
- Show model categorization by escalation level
- Display model sizes and capabilities
- Suggest best model for current hardware

---

## Implementation Steps

### Step 1: Update CLI Module
**File**: `.clockwork_integration/claudeclockwork/cli/cli.py` (or `main.py`)

**Changes**:
- Import TaskExecutor
- Add ArgumentParser flags:
  - `--escalation-level` (type=int, default=1, choices=[0-5])
  - `--model` (type=str, optional)
  - `--preferred-models` (type=str, optional)
  - `--ollama-only` (action='store_true')
- Add new command: `check-ollama`

**Pseudo-code**:
```python
import argparse
from claudeclockwork.core.executor.task_executor import TaskExecutor

def main():
    parser = argparse.ArgumentParser()

    # Existing args
    parser.add_argument('--skill-id', required=True)
    parser.add_argument('--inputs', default='{}')

    # NEW: Escalation and routing args
    parser.add_argument('--escalation-level', type=int, default=1,
                       choices=range(6), help='Task complexity level (0-5)')
    parser.add_argument('--model', type=str, help='Preferred Ollama model')
    parser.add_argument('--preferred-models', type=str,
                       help='Comma-separated model preference list')
    parser.add_argument('--ollama-only', action='store_true',
                       help='Force local Ollama execution (fail if unavailable)')

    # NEW: Check Ollama command
    subparsers = parser.add_subparsers(dest='command')
    subparsers.add_parser('check-ollama', help='Check Ollama server health')

    args = parser.parse_args()

    # Handle check-ollama command
    if args.command == 'check-ollama':
        executor = TaskExecutor()
        health = executor.health_check()
        print_health(health)
        return

    # Execute task with routing
    executor = TaskExecutor(
        fallback_to_claude=not args.ollama_only
    )

    # Parse preferred models
    preferred_models = None
    if args.preferred_models:
        preferred_models = [m.strip() for m in args.preferred_models.split(',')]
    elif args.model:
        preferred_models = [args.model]

    # Execute
    result = executor.execute_task(
        task_id=args.skill_id,
        escalation_level=args.escalation_level,
        inputs=json.loads(args.inputs),
        preferred_models=preferred_models,
        force_ollama=args.ollama_only,
    )

    # Output result
    print_result(result)
```

### Step 2: Create Health Check Formatter
**File**: `.clockwork_integration/claudeclockwork/cli/formatters.py` (new)

**Functions**:
- `print_health(health_dict)` — Format and display health check
- `print_result(skill_result)` — Format task execution result
- `print_error(error)` — Format error messages

**Output Formatting**:
```python
def print_health(health):
    """Pretty-print Ollama health check."""
    executor = health  # Assume health is from executor.health_check()

    print("\n✓ Ollama Health Check")
    print(f"  Server: {executor['router']['ollama_host']}:{executor['router']['ollama_port']}")
    print(f"  Status: {'RUNNING' if executor['router']['ollama_available'] else 'UNAVAILABLE'}")
    print(f"  Available models: {len(executor['router']['available_models'])}")

    if executor['router']['available_models']:
        print("\n  Models by escalation level:")
        models = executor['router']['available_models']

        # L1 models
        l1_models = [m for m in models if any(x in m for x in ['32b', 'coder'])]
        if l1_models:
            print(f"    L1 (Code drafting): {', '.join(l1_models[:3])}")

        # L2 models
        l2_models = [m for m in models if any(x in m for x in ['70b', '72b'])]
        if l2_models:
            print(f"    L2 (Architecture): {', '.join(l2_models[:3])}")

        print(f"\n  ✓ Total loaded: {len(models)} models")
```

### Step 3: Integration Tests
**File**: `.clockwork_integration/tests/test_cli_integration.py` (new)

**Test Cases**:
```python
def test_cli_with_escalation_level():
    """CLI should accept --escalation-level flag."""
    result = run_cli([
        '--skill-id', 'test',
        '--escalation-level', '1',
        '--inputs', '{"prompt": "test"}'
    ])
    assert result.returncode == 0

def test_cli_check_ollama():
    """CLI check-ollama command should work."""
    result = run_cli(['check-ollama'])
    assert 'Ollama' in result.stdout or 'Health' in result.stdout

def test_cli_with_preferred_models():
    """CLI should accept --preferred-models flag."""
    result = run_cli([
        '--skill-id', 'test',
        '--preferred-models', 'qwen2.5:32b,phi4:14b',
        '--inputs', '{"prompt": "test"}'
    ])
    assert result.returncode == 0

def test_cli_ollama_only_flag():
    """CLI should respect --ollama-only flag."""
    result = run_cli([
        '--skill-id', 'test',
        '--ollama-only',
        '--inputs', '{"prompt": "test"}'
    ])
    # Should use TaskExecutor with fallback_to_claude=False
    assert '--ollama-only' handling works
```

---

## Flag Reference

| Flag | Type | Default | Example | Purpose |
|------|------|---------|---------|---------|
| `--escalation-level` | int 0-5 | 1 | `--escalation-level 2` | Task complexity |
| `--model` | string | none | `--model qwen2.5:32b` | Preferred model |
| `--preferred-models` | string | none | `--preferred-models "m1,m2"` | Model priority list |
| `--ollama-only` | flag | false | `--ollama-only` | Force local execution |

---

## CLI Usage Examples

### Basic Task Execution (L1, default model)
```bash
python3 -m claudeclockwork.cli --skill-id code_draft \
  --inputs '{"prompt": "Write test for user_service"}'
# Uses: qwen2.5-coder:32b (first L1 model available)
```

### Specify Task Complexity (L2, architecture)
```bash
python3 -m claudeclockwork.cli --skill-id arch_brief \
  --escalation-level 2 \
  --inputs '{"prompt": "Explain forum architecture"}'
# Uses: qwen2.5:72b (first L2 model available)
```

### Force Specific Model
```bash
python3 -m claudeclockwork.cli --skill-id code_draft \
  --model phi4:14b \
  --inputs '{"prompt": "..."}'
# Uses: phi4:14b (fail if not available)
```

### Model Preference List
```bash
python3 -m claudeclockwork.cli --skill-id arch_brief \
  --preferred-models "llama3.3:70b,qwen2.5:72b" \
  --inputs '{"prompt": "..."}'
# Try llama3.3:70b first, then qwen2.5:72b, then defaults
```

### Offline Execution (no Claude fallback)
```bash
python3 -m claudeclockwork.cli --skill-id code_draft \
  --ollama-only \
  --inputs '{"prompt": "..."}'
# Fail if Ollama unavailable; never use Claude
```

### Check Ollama Health
```bash
python3 -m claudeclockwork.cli check-ollama
# Output:
# ✓ Ollama server: RUNNING
# ✓ Server: localhost:11434
# ✓ Available models: 19
# ✓ L1 models (Code drafting):
#   - qwen2.5-coder:32b
#   - deepseek-coder:33b
#   - phi4:14b
# ✓ L2 models (Architecture):
#   - qwen2.5:72b
#   - llama3.3:70b
```

---

## Error Handling

### Missing Ollama (--ollama-only)
```bash
$ python3 -m claudeclockwork.cli --skill-id code_draft \
    --ollama-only --inputs '{"prompt": "test"}'

✗ ERROR: Ollama server not available (localhost:11434)
  Tried connecting to: http://localhost:11434/api/tags

  Options:
  1. Start Ollama: ollama serve
  2. Change server: OLLAMA_HOST=0.0.0.0:11434
  3. Remove --ollama-only flag to allow Claude fallback
```

### Model Not Available
```bash
$ python3 -m claudeclockwork.cli --skill-id code_draft \
    --model nonexistent:latest --inputs '{"prompt": "test"}'

✗ ERROR: Model 'nonexistent:latest' not found on Ollama server
  Available models:
  - qwen2.5-coder:32b
  - qwen2.5:72b
  - llama3.3:70b
  ... (16 more)

  Tip: Use 'check-ollama' to list all available models
```

### Invalid Escalation Level
```bash
$ python3 -m claudeclockwork.cli --skill-id code_draft \
    --escalation-level 99 --inputs '{"prompt": "test"}'

✗ ERROR: Invalid escalation level: 99
  Valid levels: 0-5 (L0-L5)

  L0 = Trivial (skip execution)
  L1 = Team Lead (code drafting)
  L2 = Architecture (reasoning)
  L3 = Technical Critic (performance)
  L4 = Systemic Critic (governance)
  L5 = User approval
```

---

## Files to Modify

| File | Type | Changes |
|------|------|---------|
| `claudeclockwork/cli/cli.py` | Modify | Add flags, commands, TaskExecutor integration |
| `claudeclockwork/cli/formatters.py` | Create | Health/result formatting functions |
| `tests/test_cli_integration.py` | Create | CLI argument and command tests |
| `claudeclockwork/cli/__init__.py` | Update | Export new functions |

---

## Testing Strategy

### Unit Tests
```bash
# Test CLI argument parsing
pytest tests/test_cli_integration.py::test_cli_with_escalation_level -v

# Test check-ollama command
pytest tests/test_cli_integration.py::test_cli_check_ollama -v

# Test flags combination
pytest tests/test_cli_integration.py::test_cli_flags_* -v
```

### Integration Tests
```bash
# Test end-to-end CLI execution
python3 -m claudeclockwork.cli --skill-id test \
  --escalation-level 1 \
  --inputs '{"prompt": "test"}'

# Verify health check
python3 -m claudeclockwork.cli check-ollama
```

### Manual Smoke Tests
```bash
# L1 execution (default)
python3 -m claudeclockwork.cli --skill-id code_draft \
  --inputs '{"prompt": "def add(a, b):"}'

# L2 execution (large model)
python3 -m claudeclockwork.cli --skill-id arch_brief \
  --escalation-level 2 \
  --inputs '{"prompt": "Forum architecture"}'

# Force offline
python3 -m claudeclockwork.cli --skill-id code_draft \
  --ollama-only \
  --inputs '{"prompt": "test"}'

# Check health
python3 -m claudeclockwork.cli check-ollama
```

---

## Validation Checklist

- [ ] CLI accepts `--escalation-level` flag (0-5)
- [ ] CLI accepts `--model` flag for model selection
- [ ] CLI accepts `--preferred-models` flag (comma-separated)
- [ ] CLI accepts `--ollama-only` flag (force local)
- [ ] CLI has `check-ollama` command
- [ ] TaskExecutor integrated with CLI
- [ ] Proper error messages for missing Ollama
- [ ] Proper error messages for invalid models
- [ ] Health output is clear and actionable
- [ ] All CLI args tested
- [ ] Integration tests pass
- [ ] Help text is clear (`--help`)

---

## Completion Criteria

✅ CLI accepts escalation level (0-5)
✅ CLI accepts model preferences (single or list)
✅ CLI accepts force-offline flag
✅ `check-ollama` command works and shows health
✅ TaskExecutor routes based on CLI flags
✅ Error messages are helpful
✅ All tests pass
✅ Integration verified with live Ollama

---

## Timeline

- **Implementation**: 1-1.5 hours
- **Testing**: 0.5-1 hour
- **Integration verification**: 0.5 hour
- **Total**: 2-3 hours

---

## Ready for Implementation

This plan is complete and ready to implement. Once Phase 2.2 tests pass, proceed with Task 2.3.

**Next**: Execute Task 2.3 (CLI Flags & Commands)
