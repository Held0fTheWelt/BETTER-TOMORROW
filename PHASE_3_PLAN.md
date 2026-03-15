# Phase 3: Skills & Manifest - Implementation Plan

**Phase**: 3 (Skills & Manifest)
**Date Started**: 2026-03-15
**Estimated Duration**: 3-4 hours
**Status**: IN PROGRESS

---

## Objective

Complete Phase 3 by:
1. Implementing Claude API execution in TaskExecutor
2. Creating 3 Ollama skill definitions with manifest
3. Registering skills in the Clockwork manifest system
4. Defining JSON input/output contracts
5. Creating comprehensive documentation

---

## Tasks

### Task 3.1: Claude API Integration
**Purpose**: Enable L3-L4 task execution via Claude API

**Implementation**:
- Update `TaskExecutor._execute_claude_task()` to call Claude API
- Use `anthropic` SDK for API calls
- Handle authentication via environment variable
- Return results in SkillResult format
- Add error handling and fallback logic

**Files**:
- `claudeclockwork/core/executor/task_executor.py` (modify `_execute_claude_task`)
- Tests for Claude API execution

**Time**: 1-1.5 hours

### Task 3.2: Ollama Skill Definitions
**Purpose**: Register 3 Ollama skills in manifest system

**Skills**:
1. **code-draft** (L1)
   - Purpose: Draft code, write tests, implement features
   - Input: prompt (string)
   - Output: generated code
   - Model: qwen2.5-coder:32b

2. **architecture-brief** (L2)
   - Purpose: Architecture analysis, system design reasoning
   - Input: prompt (string)
   - Output: architecture explanation
   - Model: qwen2.5:72b

3. **code-review** (L1)
   - Purpose: Review code, provide feedback
   - Input: code (string), prompt (string)
   - Output: review feedback
   - Model: qwen2.5-coder:32b

**Structure**:
```
.claude/skills/
  ├── code-draft/
  │   ├── manifest.json
  │   └── skill.py
  ├── architecture-brief/
  │   ├── manifest.json
  │   └── skill.py
  └── code-review/
      ├── manifest.json
      └── skill.py
```

**Time**: 1.5-2 hours

### Task 3.3: Manifest Registration
**Purpose**: Register skills so they're discoverable by SkillRegistry

**Implementation**:
- Create manifest.json for each skill
- Define inputs/outputs schema
- Register with SkillRegistry
- Verify discovery and loading

**Files**:
- `.claude/skills/*/manifest.json` (3 files)
- `.claude/skills/*/skill.py` (3 files)
- Integration tests

**Time**: 1 hour

---

## Detailed Implementation

### Task 3.1: Claude API Integration

**Current Status**:
```python
def _execute_claude_task(self, task_id, routing_decision, inputs):
    return SkillResult(
        success=False,
        skill_name=task_id,
        error="Claude API execution not yet implemented",
        metadata={...}
    )
```

**New Implementation**:
```python
def _execute_claude_task(self, task_id, routing_decision, inputs):
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

        prompt = inputs.get("prompt", "")
        system_prompt = inputs.get("system_prompt")
        model = routing_decision.model_name
        max_tokens = routing_decision.config.get("max_tokens", 4096)

        # Call Claude API
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=0.7,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )

        output = message.content[0].text
        tokens_used = message.usage.output_tokens

        return SkillResult(
            success=True,
            skill_name=task_id,
            data={
                "output": output,
                "model": model,
                "tokens_used": tokens_used,
                "latency_ms": 0  # Would need to measure
            },
            metadata={...}
        )
    except Exception as e:
        return SkillResult(
            success=False,
            skill_name=task_id,
            error=f"Claude API error: {e}",
            metadata={...}
        )
```

**Environment**:
- Requires `ANTHROPIC_API_KEY` environment variable
- Uses `anthropic` SDK (requires `pip install anthropic`)
- Graceful fallback if key is missing

### Task 3.2: Skill Definitions

**Manifest Structure (manifest.json)**:
```json
{
  "name": "code-draft",
  "version": "1.0.0",
  "category": "code-generation",
  "description": "Draft code, write tests, implement features using Ollama",
  "entrypoint": "skill:CodeDraftSkill",
  "permissions": ["network"],
  "tags": ["ollama", "code", "l1"],
  "inputs": {
    "prompt": {
      "type": "string",
      "description": "Task description or code prompt"
    }
  },
  "outputs": {
    "code": {
      "type": "string",
      "description": "Generated code"
    },
    "model": {
      "type": "string",
      "description": "Model used for generation"
    }
  }
}
```

**Skill Implementation (skill.py)**:
```python
from claudeclockwork.core.base.skill import SkillBase
from claudeclockwork.core.executor.task_executor import TaskExecutor

class CodeDraftSkill(SkillBase):
    def run(self, context, **kwargs):
        executor = TaskExecutor()
        result = executor.execute_task(
            task_id="code_draft",
            escalation_level=1,
            inputs=context.to_dict(),
        )
        return result.to_skill_result_spec(context.request_id)
```

---

## Timeline

```
Task 3.1 (Claude API):      1-1.5 hours
Task 3.2 (Skill Defs):      1.5-2 hours
Task 3.3 (Manifest Reg):    1 hour
Testing & Documentation:    0.5-1 hour
Total:                      4-5 hours (within estimate)
```

---

## Success Criteria

- ✅ Claude API integration complete and working
- ✅ 3 Ollama skills registered in manifest system
- ✅ Skills discoverable via SkillRegistry
- ✅ Manifest.json files valid and complete
- ✅ Skill implementations follow SkillBase contract
- ✅ All skills tested with TaskExecutor
- ✅ Documentation complete

---

## Next Steps After Phase 3

**Phase 4: Optimization**
- Token budgeting and cost tracking
- Performance profiling
- Batch operation support
- Estimated: 2-3 hours

---

**Status**: Ready to implement
