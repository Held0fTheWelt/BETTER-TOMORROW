# ADR-002: Wiki Payload-Only Suggestions vs Dedicated Endpoint

**Date**: 2026-03-15
**Status**: Accepted
**Deciders**: Team Lead, Technical Architect
**Implements**: Task.md section D (Wiki API/docs/Postman must become fully consistent)

---

## Context

Wiki page API needed to expose suggestion candidates. Two approaches were possible:

1. **Payload-Only**: Include suggestions in main wiki page response (`GET /api/v1/wiki/<page_id>`)
2. **Dedicated Endpoint**: Create dedicated `/api/v1/wiki/<page_id>/suggested-threads` endpoint

News already had both approaches. Wiki needed consistency decision.

---

## Decision

**Implement Payload-Only approach as primary**, with backward-compatible dedicated endpoint.

### Reasoning for Payload-Only

1. **Coherence**: Single response contains all discussion context (primary, related, suggested)
2. **Simplicity**: No additional HTTP round-trip needed by clients
3. **Efficiency**: Single API call gets complete data
4. **Consistency with News**: Follows established pattern from news_service
5. **Smaller API Surface**: Fewer endpoints to maintain

### Implementation

**Primary**: `GET /api/v1/wiki/<page_id>` returns:
```json
{
  "id": 1,
  "title": "Wiki Page",
  "discussion": { /* primary thread */ },
  "related_threads": [ /* manually linked */ ],
  "suggested_threads": [ /* auto-suggested */ ]
}
```

**Backward Compatible**: `GET /api/v1/wiki/<page_id>/suggested-threads` also available
- Returns same suggestions
- Provided for clients that prefer dedicated endpoint
- No duplication of ranking logic

---

## Consequences

### Positive
✅ **Single Request**: Clients get complete context in one call
✅ **Consistent**: Matches News implementation pattern
✅ **Simple**: Fewer endpoints, easier to test and document
✅ **Efficient**: No extra HTTP round-trip
✅ **Backward Compatible**: Old clients can still use dedicated endpoint

### Negative
❌ **Larger Payload**: Wiki response includes suggestions (still <2KB)
❌ **Tight Coupling**: Wiki payload evolves with suggestions
❌ **Not RESTful**: Suggestions aren't separate resource

### Neutral
🔲 **Caching**: Entire payload cached together (good or bad depending on suggestion freshness needs)

---

## Alternatives Considered

### Alternative 1: Dedicated Endpoint Only
- **Pros**: Strict REST, separate resources, smaller primary payload
- **Cons**: Extra HTTP call, inconsistent with News, forces client to make multiple requests
- **Why Rejected**: Violates consistency requirement, less efficient

### Alternative 2: Both Equally (Current State)
- **Pros**: Maximum flexibility
- **Cons**: Maintains two code paths, duplication, confusing API surface
- **Why Rejected**: Not coherent, violates decision-making requirement

### Alternative 3: GraphQL
- **Pros**: Clients request exactly what they want
- **Cons**: Major architectural change, overkill for current scale
- **Why Rejected**: Out of scope, complexity not justified

---

## Documentation Impact

### Updated in Docs
- API Reference: Wiki endpoints documented with payload structure
- Postman: Single wiki detail request with suggestions included
- Code comments: Clear that payload-only is primary approach

### Clear Statement
"Wiki suggestions are included in the main page payload. The dedicated `/suggested-threads` endpoint is available for backward compatibility but is not the primary integration point."

---

## Future Evolution

If requirements change:
1. **Lazy Loading**: Could move suggestions to separate endpoint if payload becomes too large
2. **Partial Requests**: Could support `?include=suggestions` flag for client control
3. **Real-Time Updates**: Could implement SSE for suggestion updates without re-fetching

---

## Related Decisions

- ADR-001: Tag-based ranking (what suggestions are, not how they're delivered)
- ADR-004: Ollama-first routing (cost implications of rendering suggestions)

---

## Validation

**Tests Written**:
- `test_wiki_page_detail_includes_suggested_threads` - Payload includes suggestions
- `test_wiki_suggestions_endpoint_returns_parity_with_news` - Both methods consistent

**All Tests Passing**: ✅ 9/9 in test_narrow_followup.py

---

## Approval

- [ ] Team Lead
- [ ] Technical Architect
- [ ] API Designer
- [ ] Documentation Owner
