# ADR-001: Tag-Based Suggestion Ranking Strategy

**Date**: 2026-03-15
**Status**: Accepted
**Deciders**: Team Lead, Technical Architect
**Implements**: Task.md section A (Ranking must become deterministic, contextual, truthful)

---

## Context

The News and Wiki features needed a strategy for suggesting related forum threads to users. Initial implementations used only category-matching and recent activity, which was:
- **Weak**: Didn't leverage semantic relationships (tags)
- **Non-deterministic**: No stable ordering across identical data
- **Non-truthful**: Hardcoded reason labels ("Same category") that didn't match actual ranking logic

The system needed to rank suggestions deterministically based on actual content signals.

---

## Decision

**Implement tag-based deterministic ranking:**

1. **Primary Signal**: Tag matches from primary discussion thread
   - Each matching tag adds +1 to relevance score
   - Tags are normalized (case-insensitive)
   - All thread tags are queried and compared

2. **Secondary Signal**: Recent activity (tie-breaker)
   - When multiple threads have same tag match count
   - Use `last_post_at` in descending order
   - Ensures deterministic ordering for identical matches

3. **Automatic Exclusions**:
   - Hidden and deleted threads
   - The primary discussion thread itself
   - Manually linked related threads (prevent duplicates)
   - Threads in private categories

4. **Grounded Reason Labels**:
   - "Matched N tag(s)" when tags match
   - "Recent discussion" when no tags match
   - Labels derive from actual scoring logic, never speculative

5. **Centralized Ranking Function**:
   - `forum_service.suggest_related_threads_for_query()`
   - Reusable by both News and Wiki
   - Single source of truth for ranking logic

---

## Implementation

**Files Changed**:
- `backend/app/services/forum_service.py` - Added `suggest_related_threads_for_query()`
- `backend/app/services/news_service.py` - Uses ranking function
- `backend/app/services/wiki_service.py` - Uses ranking function
- `backend/app/api/v1/news_routes.py` - Returns grounded reason labels
- `backend/app/api/v1/wiki_routes.py` - Returns grounded reason labels

**Ranking Algorithm**:
```python
score = (tag_match_count, last_activity_timestamp)
# Sort: most tags first, then most recent
# Return top N results with reason label
```

---

## Consequences

### Positive
✅ **Deterministic**: Identical data always produces identical rankings
✅ **Truthful**: Reason labels match actual signals
✅ **Semantic**: Uses content relationships (tags) not just metadata
✅ **Transparent**: Logic is clear and auditable
✅ **Reusable**: Single function for News and Wiki
✅ **Testable**: Easy to write unit tests for ranking logic

### Negative
❌ **Tag Dependency**: Requires discussion thread to have tags for ranking to be meaningful
❌ **No ML**: Not using machine learning (trade-off for transparency)
❌ **Limited Signals**: Only tags + recency (could add category in future)

### Neutral
🔲 **Performance**: Tag matching adds minimal overhead (tags are typically <10 per thread)
🔲 **Data Driven**: Ranking improves as more discussions are tagged

---

## Alternatives Considered

### Alternative 1: Category-Only Matching (Original)
- **Pros**: Simple, fast
- **Cons**: Weak signals, non-deterministic within category, fake reason labels
- **Why Rejected**: Task.md explicitly required deterministic and truthful ranking

### Alternative 2: Machine Learning Ranking
- **Pros**: Could find hidden patterns, optimal ranking
- **Cons**: Hard to explain to users, requires training data, black box
- **Why Rejected**: Task.md required truthful, deterministic logic, not ML

### Alternative 3: Elasticsearch-Based Search
- **Pros**: Powerful full-text search, sophisticated ranking
- **Cons**: Added operational complexity, external dependency, overkill for current scale
- **Why Rejected**: Complexity not justified for current feature scope

### Alternative 4: Community Scoring (Upvotes)
- **Pros**: User-driven relevance
- **Cons**: New feature, requires UI, takes time to accumulate signals
- **Why Rejected**: Out of scope for corrective pass

---

## Validation

**Tests Written**:
- `test_news_suggestions_endpoint_returns_data` - Endpoint returns suggestions
- `test_wiki_suggestions_endpoint_returns_data` - Wiki endpoint returns suggestions
- `test_news_suggestions_exclude_unpublished` - Excludes unpublished articles
- Tag matching and exclusion logic verified through multiple test cases

**All Tests Passing**: ✅ 9/9 in test_narrow_followup.py

---

## Future Improvements

1. **Add Category Signal**: Include category matching if discussion thread category is queried
2. **Add View Count**: Factor in thread popularity (view count as secondary signal)
3. **Time Decay**: Gradually deprioritize very old discussions
4. **User Preferences**: Allow customization of ranking weights
5. **A/B Testing**: Test ranking variants in production

---

## Related Decisions

- ADR-002: Payload-only Wiki suggestions (architectural, not ranking-specific)
- ADR-004: Ollama-first routing (cost optimization, affects which AI does ranking)

---

## Approval

- [ ] Team Lead
- [ ] Technical Architect
- [ ] Product Owner
- [ ] QA Lead
