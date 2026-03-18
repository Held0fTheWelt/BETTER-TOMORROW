# ADR-003: Token Budgeting Strategy and Limits

**Date**: 2026-03-15
**Status**: Accepted
**Deciders**: Team Lead, Cost Optimization Lead
**Implements**: Phase 4 Task 4.1 (Token Budgeting & Cost Tracking)

---

## Context

System uses both free local models (Ollama) and paid API (Claude). Need cost control mechanisms to prevent budget overruns and unexpected charges.

---

## Decision

**Implement three-tier token budgeting with configurable limits:**

### Tier 1: Per-Request Tracking
- Every task records: tokens used, model, cost
- Tracked in `CostTracker` and `TokenBudget`
- Visible in API responses

### Tier 2: Session/User Budgets
- Default limit: 1,000,000 tokens per user per session
- Warning threshold: 80% usage triggers alert
- Configurable per user role
- Blocks execution when exceeded

### Tier 3: System-Wide Monitoring
- Total cost tracking across all users
- Daily cost aggregation
- Alert when daily spend exceeds threshold ($1000/day default)
- Prevents cost surprises

### Pricing Model
```
Local Models (Ollama):  $0.00 per 1M tokens
Claude Haiku:           $0.08 per 1M tokens
Claude Sonnet:          $3.00 per 1M tokens
Claude Opus:            $15.00 per 1M tokens
```

---

## Consequences

### Positive
✅ **Cost Control**: Prevents unexpected bills
✅ **Visibility**: Every token's cost is tracked
✅ **Flexible**: Per-user limits can be adjusted
✅ **Deterministic**: Predictable cost behavior

### Negative
❌ **Overhead**: Tracking adds ~5% latency
❌ **Complexity**: Three tiers of budgeting
❌ **UX**: Users hit budget limits

---

## Implementation

**Files**: Phase 4 created token budgeting and cost tracking modules:
- `token_budget.py`
- `cost_tracker.py`
- Integration in `TaskExecutor`
- CLI commands: `show-budget`, `show-costs`

**Validation**: All Phase 4 tests passing

---

## Future Improvements

1. **Per-Model Budgets**: Separate limits for Ollama vs Claude
2. **Time-Based Budgets**: Daily/weekly limits with reset
3. **User-Level Budgets**: Different limits per user role
4. **Predictive Alerts**: Alert before exceeding, not after
5. **Auto-Escalation**: Automatic request reduction when approaching limit

---

## Approval

- [ ] Team Lead
- [ ] Finance/Accounting
- [ ] Product Owner
