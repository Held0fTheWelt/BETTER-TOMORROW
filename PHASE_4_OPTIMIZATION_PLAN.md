# Phase 4: Optimization - Implementation Plan

**Phase**: 4 (Optimization)
**Date Started**: 2026-03-15
**Estimated Duration**: 2-3 hours
**Status**: PLANNING

---

## Objective

Optimize the Ollama agent execution system by:
1. Implementing token budgeting and cost tracking
2. Performance optimization (caching, batch operations)
3. Enhanced monitoring and observability
4. Cost analysis and reporting

---

## Tasks Overview

### Task 4.1: Token Budgeting & Cost Tracking (1 hour)
**Purpose**: Track and limit token usage and costs

**Implementation**:
- Create `TokenBudget` class to track usage
- Create `CostTracker` to calculate and report costs
- Add token limits per user/session
- Add cost per model pricing
- Integrate with TaskExecutor for tracking
- Return cost data in SkillResult metadata

**Files**:
- `claudeclockwork/core/budgeting/token_budget.py` (150 lines)
- `claudeclockwork/core/budgeting/cost_tracker.py` (120 lines)
- Update `task_executor.py` for tracking

**Example**:
```python
budget = TokenBudget(limit=100000)
tracker = CostTracker()

executor = TaskExecutor(token_budget=budget, cost_tracker=tracker)
result = executor.execute_task(...)

print(f"Tokens used: {result.metadata['tokens_used']}")
print(f"Cost: ${result.metadata['cost']}")
print(f"Budget remaining: {budget.remaining}")
```

---

### Task 4.2: Performance Optimization (1-1.5 hours)
**Purpose**: Improve execution speed and efficiency

**Implementation 1: Prompt Caching**
- Cache identical prompts across requests
- LRU cache for recent prompts
- Optional per-task basis
- File: `claudeclockwork/core/caching/prompt_cache.py` (100 lines)

**Implementation 2: Batch Operations**
- Support multiple tasks in single API call
- Batch Ollama requests when possible
- Reduce API overhead
- File: `claudeclockwork/core/executor/batch_executor.py` (150 lines)

**Implementation 3: Model Preloading**
- Preload frequently used models into VRAM
- Track model load state
- Optimize for repeated use
- File: `claudeclockwork/workers/model_manager.py` (100 lines)

**Expected Improvements**:
```
Prompt caching:     20-30% latency reduction
Batch operations:   40-50% throughput increase
Model preloading:   50-70% TTFB improvement
```

---

### Task 4.3: Monitoring & Observability (0.5-1 hour)
**Purpose**: Enhanced monitoring and analytics

**Implementation**:
- Create `PerformanceMonitor` class
- Track latency per model
- Track success/failure rates
- Create usage statistics
- Generate performance reports
- Integration with TaskExecutor

**Files**:
- `claudeclockwork/monitoring/performance_monitor.py` (150 lines)
- `claudeclockwork/monitoring/metrics_collector.py` (100 lines)

**Metrics Tracked**:
```python
{
    "total_requests": int,
    "successful_requests": int,
    "failed_requests": int,
    "avg_latency_ms": float,
    "total_tokens": int,
    "total_cost": float,
    "models_used": dict,
    "errors": dict,
}
```

---

## Detailed Implementation

### Task 4.1: Token Budgeting

**TokenBudget Class**:
```python
class TokenBudget:
    def __init__(self, limit: int = 100000):
        self.limit = limit
        self.used = 0
        self.requests = []

    def record_usage(self, tokens: int, model: str, cost: float):
        """Record token usage for a request."""
        self.used += tokens
        self.requests.append({
            "tokens": tokens,
            "model": model,
            "cost": cost,
            "timestamp": datetime.now(),
        })

    def remaining(self) -> int:
        """Get remaining token budget."""
        return max(0, self.limit - self.used)

    def is_exceeded(self) -> bool:
        """Check if budget exceeded."""
        return self.used >= self.limit

    def usage_percentage(self) -> float:
        """Get usage as percentage."""
        return (self.used / self.limit) * 100
```

**CostTracker Class**:
```python
class CostTracker:
    # Pricing per model
    PRICING = {
        "qwen2.5-coder:32b": 0.00,     # Local Ollama
        "qwen2.5:72b": 0.00,           # Local Ollama
        "llama3.3:70b": 0.00,          # Local Ollama
        "claude-sonnet-4-6": 0.003,    # Per 1K tokens
        "claude-opus-4-6": 0.015,      # Per 1K tokens
    }

    def calculate_cost(self, model: str, tokens: int) -> float:
        """Calculate cost for tokens on specific model."""
        price_per_1k = self.PRICING.get(model, 0.003)
        return (tokens / 1000) * price_per_1k

    def total_cost(self) -> float:
        """Get total cost for all tracked requests."""
        return sum(req.get("cost", 0) for req in self.requests)
```

---

### Task 4.2: Performance Optimization

**Prompt Cache**:
```python
class PromptCache:
    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0

    def get(self, prompt_hash: str) -> Optional[str]:
        """Get cached result for prompt."""
        if prompt_hash in self.cache:
            self.hits += 1
            return self.cache[prompt_hash]
        self.misses += 1
        return None

    def set(self, prompt_hash: str, result: str):
        """Cache result for prompt."""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry (simplified)
            self.cache.pop(next(iter(self.cache)))
        self.cache[prompt_hash] = result

    def hit_rate(self) -> float:
        """Get cache hit rate."""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0
```

**Batch Executor**:
```python
class BatchExecutor:
    def execute_batch(self, tasks: List[Task]) -> List[SkillResult]:
        """Execute multiple tasks efficiently."""
        # Group by model for batch operations
        by_model = {}
        for task in tasks:
            model = task.routing.model_name
            if model not in by_model:
                by_model[model] = []
            by_model[model].append(task)

        results = []
        for model, model_tasks in by_model.items():
            # Execute batch for each model
            batch_results = self._execute_model_batch(model, model_tasks)
            results.extend(batch_results)
        return results
```

---

### Task 4.3: Monitoring

**PerformanceMonitor**:
```python
class PerformanceMonitor:
    def __init__(self):
        self.requests = []
        self.errors = {}
        self.model_stats = {}

    def record_request(self, result: SkillResult):
        """Record request for analytics."""
        self.requests.append({
            "success": result.success,
            "model": result.metadata.get("model"),
            "latency_ms": result.metadata.get("latency_ms"),
            "tokens": result.metadata.get("tokens_used"),
            "cost": result.metadata.get("cost"),
            "error": result.error,
        })

    def get_statistics(self) -> dict:
        """Get usage statistics."""
        return {
            "total_requests": len(self.requests),
            "successful": sum(1 for r in self.requests if r["success"]),
            "failed": sum(1 for r in self.requests if not r["success"]),
            "avg_latency_ms": self._avg_latency(),
            "total_tokens": sum(r.get("tokens", 0) for r in self.requests),
            "total_cost": sum(r.get("cost", 0) for r in self.requests),
        }
```

---

## Integration Points

### TaskExecutor Integration
```python
class TaskExecutor:
    def __init__(self, token_budget=None, cost_tracker=None,
                 prompt_cache=None, perf_monitor=None):
        self.token_budget = token_budget or TokenBudget()
        self.cost_tracker = cost_tracker or CostTracker()
        self.prompt_cache = prompt_cache or PromptCache()
        self.perf_monitor = perf_monitor or PerformanceMonitor()

    def execute_task(self, task_id, escalation_level, inputs, ...):
        # Check budget
        if self.token_budget.is_exceeded():
            return SkillResult(
                success=False,
                error="Token budget exceeded"
            )

        # Check cache
        prompt_hash = hash(inputs.get("prompt", ""))
        cached = self.prompt_cache.get(prompt_hash)
        if cached:
            return cached

        # Execute task...
        result = ...

        # Track cost and tokens
        cost = self.cost_tracker.calculate_cost(
            result.metadata["model"],
            result.metadata["tokens_used"]
        )
        self.token_budget.record_usage(
            result.metadata["tokens_used"],
            result.metadata["model"],
            cost
        )

        # Monitor performance
        self.perf_monitor.record_request(result)

        return result
```

---

## CLI Commands for Phase 4

```bash
# Show cost statistics
$ python3 -m claudeclockwork.cli stats
{
  "total_requests": 42,
  "successful": 40,
  "failed": 2,
  "avg_latency_ms": 1523,
  "total_tokens": 125000,
  "total_cost": "$0.42"
}

# Check token budget
$ python3 -m claudeclockwork.cli budget
{
  "limit": 1000000,
  "used": 125000,
  "remaining": 875000,
  "usage_percentage": 12.5
}

# Reset tracking
$ python3 -m claudeclockwork.cli reset-stats
✓ Statistics reset

# Show cache stats
$ python3 -m claudeclockwork.cli cache-stats
{
  "size": 256,
  "max_size": 1000,
  "hits": 1234,
  "misses": 5678,
  "hit_rate": "17.8%"
}
```

---

## Performance Goals

| Metric | Baseline | Target | Method |
|--------|----------|--------|--------|
| Avg Latency | 1500ms | 500-700ms | Caching + preloading |
| Throughput | 1 task/s | 2-3 tasks/s | Batch operations |
| Cache Hit Rate | 0% | 30-40% | Prompt caching |
| Cost per Task | $0.003 | $0.001 | Optimization |
| Memory Usage | Variable | Optimized | Model management |

---

## Testing Strategy

### Unit Tests
- TokenBudget calculation
- CostTracker pricing
- PromptCache hit/miss
- PerformanceMonitor stats

### Integration Tests
- TaskExecutor with budget
- Batch operations
- Cache invalidation
- Monitor accuracy

### Performance Tests
- Latency reduction measurement
- Throughput improvement
- Cache effectiveness
- Memory usage

---

## Documentation

- Usage guide for token budgeting
- Cost tracking and reporting
- Performance tuning guide
- Batch operations examples
- Monitoring dashboard setup

---

## Timeline

```
Task 4.1 (Token Budgeting):     1 hour
Task 4.2 (Performance):         1-1.5 hours
Task 4.3 (Monitoring):          0.5-1 hour
Testing & Documentation:        0.5-1 hour
──────────────────────────────
Total Phase 4:                  3-4.5 hours
```

---

## Success Criteria

- ✅ Token budget implemented and working
- ✅ Cost tracking per model/task
- ✅ Prompt caching working (>15% hit rate)
- ✅ Batch operations implemented
- ✅ Performance monitor collecting stats
- ✅ CLI commands for monitoring
- ✅ 20%+ latency improvement
- ✅ All tests passing
- ✅ Documentation complete

---

## Status

Ready to implement Phase 4.

Estimated time: **3-4 hours**

All dependencies in place, no blockers.
