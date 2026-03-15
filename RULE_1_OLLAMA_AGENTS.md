# RULE #1: Ollama Agent Runtime Mode

**Established:** 2026-03-15
**Status:** Active
**Authority:** Claude Clockwork Integration v18

---

## The Rule

**When the user requests "use ollama agents" or "use pure ollama agents":**

1. Invoke the **Claude Clockwork system** from `/mnt/d/ClaudeClockwork/`
2. Use local Ollama models for bulk work (analysis, drafting, reviews)
3. Use Claude API only for verification, corrections, and project-specific context application
4. Follow the **Clockwork execution protocol** and **escalation levels (L0-L5)**
5. Implement the **Ollama integration** for cost-efficient distributed execution

---

## Why This Rule

The Clockwork system achieves **maximum cost reduction on Claude API tokens** by:
- ✅ Ollama 70B/72B models handle briefings and architecture decisions
- ✅ Ollama 32B models handle code drafting (~70% of implementation)
- ✅ Claude verifies, corrects, and applies project patterns
- ✅ Local execution = zero API costs for bulk work
- ✅ Structured contracts ensure reproducibility

---

## Implementation

### Step 1: Check Ollama Availability

```bash
# Is Ollama running?
curl -s http://localhost:11434/api/tags | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('models', [])))"
```

**Models required:**
- `qwen2.5-coder:32b` (implementation drafts)
- `qwen2.5:72b` or `llama3.3:70b` (architecture/briefing)
- `phi4:14b` (architecture decisions, optional)

### Step 2: Classify Task Escalation Level

Use the **Clockwork decision matrix:**

| Level | Who Decides | Typical Situation | Ollama Required |
|-------|------------|-------------------|-----------------|
| L0 | Autonomous | 1 file, no API change | No |
| L1 | Team Lead | 2-5 files, clear boundaries | Optional (recommended) |
| L2 | Architecture Agent | New module, new dependency | Mandatory |
| L3+ | Technical/Systemic Critic | Complex decisions | Mandatory |

### Step 3: Dispatch Ollama Agent

**Pseudo-code (for reference):**

```python
from <CLOCKWORK_PATH>.src.ollama_client import OllamaClient, OllamaUnavailableError

client = OllamaClient()

# For architecture (L2+):
result = client.architecture("Should we refactor X or migrate to Y?")

# For implementation drafts (L1):
result = client.draft("Implement function_name with these params...")

# For code review:
result = client.review(code_content)
```

### Step 4: Verify & Apply

**Claude verifies Ollama output:**
- ✓ Correct module imports?
- ✓ Proper type hints?
- ✓ Project patterns applied?
- ✓ No hardcoded paths?
- → Accept, correct, or request refinement (max 2 iterations)

### Step 5: Implement & Commit

Once verified, apply changes and commit with notation:
```
Co-Authored-By: Claude Haiku + Ollama[model:32b] <distributed>
```

---

## Escalation Rules

### When NOT to Use Ollama (Skip Cost)
- L0 tasks (trivial, 1 file) → direct implementation, no Ollama call

### When Ollama is Optional (Recommended for >50 lines)
- L1 tasks → `brief` or `draft`

### When Ollama is Mandatory (Hard Requirement)
- L2+ tasks → must have Ollama briefing before any implementation

---

## Freeze Protocol (Critical)

**If Ollama is unavailable at task time:**

```
❌ DO NOT silently continue without briefing
✅ DO freeze the affected agent
✅ DO preserve any partial work
✅ DO output FREEZE report with next steps
```

**Resume after user confirms Ollama is running:**
```bash
python3 <CLOCKWORK_PATH>/src/test_ollama.py  # or "test ollama" command
```

---

## Integration with Claude Code

### In This Repository

**When user says "use ollama agents":**

1. Read `/mnt/d/ClaudeClockwork/.claude/governance/ollama_integration.md`
2. Determine escalation level from task context
3. If L1+: Check Ollama availability
4. Dispatch appropriate agent (architecture, draft, review)
5. Verify Claude + Ollama result
6. Implement and commit

### Configuration Files

**Clockwork source:** `/mnt/d/ClaudeClockwork/`
- Governance policies: `.claude/governance/`
- Ollama integration: `ollama_integration.md`
- Execution protocol: `execution_protocol.md`
- Model routing: `model_escalation_policy.md`

**This project reference:** (This file)

---

## Example Workflows

### Workflow A: Bug Fix (L0-L1)

```
User: "Fix the test failures using ollama agents"
  ↓
Claude: Escalation = L1 (multiple test files)
  ↓
Ollama (32b): Draft analysis + fix suggestions
  ↓
Claude: Verify, correct module paths, apply project patterns
  ↓
Commit: "fix: resolve test failures [Ollama-assisted]"
```

### Workflow B: Architecture Decision (L2)

```
User: "Design new module structure using ollama agents"
  ↓
Claude: Escalation = L2 (new module, dependency decision)
  ↓
Ollama (72b/phi4): Full architecture briefing
  ↓
Claude: Verify module placement, dependency graph, patterns
  ↓
Implement based on verified architecture
```

### Workflow C: Code Review (L1)

```
User: "Review these changes using ollama agents"
  ↓
Ollama (14b): Code review with checklist
  ↓
Claude: Filter false positives, add project-specific notes
  ↓
Produce final review report
```

---

## Cost Model

**Typical breakdown (L1 task):**
- Ollama 32B draft: ~$0 (local)
- Claude Haiku verification: ~$0.02-0.05
- **Total:** <$0.10 vs. $0.50+ for Claude solo

**Scaling (L2+):**
- Ollama 72B architecture: ~$0 (local)
- Claude Sonnet review: ~$0.10-0.20
- **Total:** <$0.30 vs. $1.00+ for Claude solo

---

## Status

✅ **Rule #1 Established**
✅ **Clockwork System Located** (`/mnt/d/ClaudeClockwork/`)
✅ **Ollama Integration Documented** (from `ollama_integration.md`)
⏳ **Implementation:** Will execute on next "use ollama agents" request

---

## Next Steps

1. User confirms this rule is understood
2. User provides next task with "use ollama agents" request
3. Claude dispatches appropriate Clockwork agents
4. Local Ollama models handle bulk work
5. Claude provides verification and corrections
6. Cost-efficient execution delivered

---

**See also:**
- Clockwork execution protocol: `/mnt/d/ClaudeClockwork/.claude/governance/execution_protocol.md`
- Ollama integration guide: `/mnt/d/ClaudeClockwork/.claude/governance/ollama_integration.md`
- Model escalation policy: `/mnt/d/ClaudeClockwork/.claude/governance/model_escalation_policy.md`
