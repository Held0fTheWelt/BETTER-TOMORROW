# Forum Integration Wave — Delta Note

Frozen: 2026-03-12
Branch: `feature/forum-integration-wave`
Baseline: commit `961df2b` (master)

---

## What already exists

### Forum models (`backend/app/models/forum.py`)

| Entity | Table | Key columns | Indexes |
|--------|-------|-------------|---------|
| `ForumCategory` | `forum_categories` | id, parent_id (FK self), slug (unique, indexed), title, description, sort_order, is_active, is_private, required_role, created_at, updated_at | slug unique index |
| `ForumThread` | `forum_threads` | id, category_id (FK cascade), author_id (FK set-null), slug (unique, indexed), title, status, is_pinned, is_locked, is_featured, view_count, reply_count, last_post_at, last_post_id (FK set-null), created_at, updated_at, deleted_at | slug unique index; thread_id on posts; composite `ix_forum_threads_category_pinned_last_post_at` (migration 026) |
| `ForumPost` | `forum_posts` | id, thread_id (FK cascade, indexed), author_id (FK set-null), parent_post_id (FK self, set-null), content (Text), status, like_count, created_at, updated_at, edited_at, edited_by (FK set-null), deleted_at | thread_id index |
| `ForumPostLike` | `forum_post_likes` | id, post_id (FK cascade), user_id (FK cascade), created_at | unique(post_id, user_id) |
| `ForumReport` | `forum_reports` | id, target_type (thread/post), target_id, reported_by (FK set-null), reason, status (open/reviewed/escalated/resolved/dismissed), handled_by (FK set-null), handled_at, created_at | composite `ix_forum_reports_status_created_at` (migration 026) |
| `ForumThreadSubscription` | `forum_thread_subscriptions` | id, thread_id (FK cascade), user_id (FK cascade), created_at | unique(thread_id, user_id) |
| `ForumThreadBookmark` | `forum_thread_bookmarks` | id, thread_id (FK cascade), user_id (FK cascade), created_at | unique(thread_id, user_id); indexes on thread_id, user_id (migration 025) |
| `ForumTag` | `forum_tags` | id, slug (unique, indexed), label, created_at | slug unique index (migration 025) |
| `ForumThreadTag` | `forum_thread_tags` | id, thread_id (FK cascade, indexed), tag_id (FK cascade, indexed) | unique(thread_id, tag_id); indexes on both FKs (migration 025) |

### Notification model (`backend/app/models/notification.py`)

| Column | Notes |
|--------|-------|
| id, user_id (FK cascade, indexed), event_type (indexed), target_type, target_id, message, is_read, created_at (indexed), read_at | Event types in use: `thread_reply`, `mention` |

### Discussion links (News <-> Forum, Wiki <-> Forum)

**News:**
- `NewsArticle.discussion_thread_id` — nullable FK to `forum_threads.id`, indexed (migration 022).
- `NewsArticleForumThread` — many-to-many related threads table with `article_id`, `thread_id`, `relation_type` (default "related"), created_at; unique constraint and indexes (migration 024).
- `news_service.py` exposes `list_related_threads_for_article()` and `_article_to_public_dict()` includes `discussion_thread_id` + `discussion_thread_slug`.
- `news_routes.py` admin endpoints: `POST/DELETE /api/v1/news/<id>/discussion-thread` (link/unlink), `GET/POST/DELETE /api/v1/news/<id>/related-threads[/<thread_id>]` (CRUD related threads).
- Public news detail returns `discussion_thread_id`, `discussion_thread_slug`, and `related_threads` list.

**Wiki:**
- `WikiPage.discussion_thread_id` — nullable FK to `forum_threads.id`, indexed (migration 022).
- `WikiPageForumThread` — many-to-many related threads table with `page_id`, `thread_id`, `relation_type`, created_at; unique constraint and indexes (migration 024).
- `wiki_service.py` exposes `list_related_threads_for_page()`.
- `wiki_admin_routes.py` has: `POST/DELETE /api/v1/wiki/admin/pages/<id>/discussion-thread` (link/unlink), `GET/POST/DELETE /api/v1/wiki/admin/pages/<id>/related-threads[/<thread_id>]`.
- Public wiki detail returns `discussion_thread_id`, `discussion_thread_slug`, and `related_threads` list.

### Search and filtering

- `GET /api/v1/forum/search` — filters: `q` (ILIKE on title), `category` (slug), `status`, `tag` (slug), `include_content` (boolean for post body ILIKE). Pagination via page/limit. Returns thread results only.
- Search truncates query at 200 chars. Empty queries with no filters return empty results.
- Visibility filtering applied in Python after SQL query (loads all matches, then filters).
- Tag filter joins `ForumThreadTag` + `ForumTag` on slug.

### Likes / reactions

- **Likes only.** `ForumPostLike` model, `like_post()`/`unlike_post()` service, `POST/DELETE /api/v1/forum/posts/<id>/like` routes. Like count tracked on `ForumPost.like_count`. `liked_by_me` flag in post list responses.
- **No reactions model exists.** No emoji-type or multi-type reaction system.

### Moderation and reports

**Reports:**
- Status flow: `open` -> `reviewed` | `escalated` | `resolved` | `dismissed`. Already has `escalated` state.
- Single update: `PUT /api/v1/forum/reports/<id>` with status body.
- Bulk update: `POST /api/v1/forum/reports/bulk-status` with `report_ids` + `status`.
- List: `GET /api/v1/forum/reports` with optional `status` filter.
- Enrichment: `_enrich_report_dict()` adds `thread_slug`, `target_title` for dashboard linking.
- `handled_by`, `handled_at` tracked on resolution.

**Bulk actions:**
- `POST /api/v1/forum/moderation/bulk-threads/status` — bulk lock/unlock/archive/unarchive threads.
- `POST /api/v1/forum/moderation/bulk-posts/hide` — bulk hide/unhide posts.

**Moderation dashboard endpoints:**
- `GET /api/v1/forum/moderation/metrics` — counts: open_reports, hidden_posts, locked_threads, pinned_threads.
- `GET /api/v1/forum/moderation/recent-reports` — enriched recent open reports.
- `GET /api/v1/forum/moderation/recently-handled` — enriched recently handled reports.
- `GET /api/v1/forum/moderation/locked-threads` — list locked threads.
- `GET /api/v1/forum/moderation/pinned-threads` — list pinned threads.
- `GET /api/v1/forum/moderation/hidden-posts` — list hidden posts with thread context.

**Moderation log:**
- `GET /api/v1/forum/moderation/log` — thin wrapper on `list_activity_logs(category="forum")` with q/status/date filters.
- All forum moderation actions log via `log_activity()` with `category="forum"`, specific `action` strings, `target_type`/`target_id`.
- Log entries contain: actor info snapshots, category, action, status, message, route, method, tags, meta, target_type, target_id.

**Single-item moderation routes:**
- Lock/unlock: `POST /api/v1/forum/threads/<id>/lock|unlock`
- Pin/unpin: `POST /api/v1/forum/threads/<id>/pin|unpin`
- Feature/unfeature: `POST /api/v1/forum/threads/<id>/feature|unfeature`
- Archive/unarchive: `POST /api/v1/forum/threads/<id>/archive|unarchive`
- Move: `POST /api/v1/forum/threads/<id>/move`
- Merge: `POST /api/v1/forum/threads/<source_id>/merge`
- Split: `POST /api/v1/forum/threads/<id>/split`
- Hide/unhide posts: `POST /api/v1/forum/posts/<id>/hide|unhide`

### Notifications and subscriptions

- `ForumThreadSubscription` — user subscribes to thread; `POST/DELETE /api/v1/forum/threads/<id>/subscribe`.
- On new reply, `create_notifications_for_thread_reply()` creates `Notification` for all subscribers (except author).
- `@mention` in post content creates `mention` notifications via `_create_mention_notifications_for_post()`.
- `GET /api/v1/notifications` — list notifications, page/limit/unread_only, with thread_slug enrichment.
- `PATCH|PUT /api/v1/notifications/<id>/read` — mark single read.
- `POST|PUT /api/v1/notifications/read-all` — mark all read.

### Tests (`backend/tests/test_forum_api.py`)

1266 lines, 48 test functions covering:
- Category visibility (public, private, inactive, required_role)
- Thread creation (auth, author, hidden, deleted visibility)
- Post creation (auth, author_username, hidden visibility)
- Bookmarks (create, list)
- Bulk report status update
- Search with tag and category filters
- Likes (visibility requirement, increment, decrement, duplicate prevention, liked_by_me flag)
- Reports (submission, status update)
- Moderation (lock/unlock, pin/unpin, hide/unhide posts)
- Own post edit and delete
- Counter recalculation after hide/unhide
- Parent post validation (same-thread only)
- Search (returns visible threads, includes author_username)
- Subscribe/unsubscribe flow
- Notifications (reply creates notification for subscribers, list + mark read, mark all read, thread_slug enrichment)
- Moderation metrics (pinned threads count)
- Moderation recently handled reports
- Moderation locked/pinned/hidden lists
- Move thread
- Archive/unarchive thread
- Thread merge (moves posts, updates counters, requires moderator, merges subscriptions)
- Thread split (creates new thread, moves posts, requires moderator, rejects non-top-level root)
- Mention notifications

### Frontend templates

**Public forum** (`administration-tool/templates/forum/`):
- `index.html` (48 lines) — category list
- `category.html` (66 lines) — thread list in category
- `thread.html` (78 lines) — thread detail with posts
- `notifications.html` (43 lines) — notification list

**Admin** (`administration-tool/templates/manage/forum.html`, 191 lines):
- Moderation dashboard card (metrics, open reports, recently handled, locked/pinned/hidden thread lists)
- Category CRUD editor
- Reports card with status filter

### Migrations (26 total, latest 3)

- `024_news_wiki_related_forum_threads.py` — creates `news_article_forum_threads` and `wiki_page_forum_threads` tables.
- `025_forum_bookmarks_and_tags.py` — creates `forum_thread_bookmarks`, `forum_tags`, `forum_thread_tags` tables.
- `026_forum_moderation_indexes.py` — adds composite indexes: `ix_forum_reports_status_created_at`, `ix_forum_threads_category_pinned_last_post_at`.

### Postman

Collection file: `postman/WorldOfShadows_API.postman_collection.json` (87 occurrences of "forum"/"Forum"). Environment files for Local and Test exist.

---

## What is missing for this wave

### A. Forum <-> News/Wiki integration

| Gap | Detail |
|-----|--------|
| Public "Discuss" entry point for News | Frontend news detail (`news_detail.html` / `news.js`) does not render a "Discuss this article" link or button even though `discussion_thread_slug` is returned by the API. |
| Public "Discuss" entry point for Wiki | Frontend wiki public page (`wiki_public.html`) does not render a discussion link even though the API returns the slug. |
| Admin UI for linking discussion threads (News) | Admin news management (`manage_news.js` / `manage/news.html`) does not surface the discussion-thread link/unlink or related-threads CRUD, even though backend endpoints exist. |
| Admin UI for linking discussion threads (Wiki) | Admin wiki management (`manage_wiki.js` / `manage/wiki.html`) does not surface discussion-thread or related-threads UI, even though backend endpoints exist. |
| Auto-create discussion thread on publish | No mechanism to automatically create a forum thread when a news article or wiki page is published. Currently requires manual linking. |
| Related threads display in public News detail | API returns `related_threads` but frontend does not render them. |
| Related threads display in public Wiki detail | Same gap. |
| Tag-based auto-suggestion for related threads | No endpoint or logic to suggest related threads based on shared tags, category, or content similarity. |

### B. Community comfort

| Gap | Detail |
|-----|--------|
| Bookmark indicator in thread list | Thread list responses do not include `bookmarked_by_me` flag; frontend has no visual indicator. |
| Search hardening (content search default off, large result warning) | Content search (`include_content`) exists but is opt-in. No guard on result set size in SQL — all matches are loaded into Python. |
| Reactions | No reactions model, service, routes, or frontend. Only simple likes exist. Decision needed: skip explicitly or implement. |
| Tag management UI (admin) | No admin endpoint to list/edit/delete tags globally. Tags are created implicitly via thread tagging only. |
| Tag display in thread list | Thread list endpoints (`/forum/categories/<slug>/threads`) do not include tags per thread. Only thread detail and bookmarks list do. |
| Search by multiple tags | Search supports only a single `tag` filter parameter. |

### C. Moderation at operational level

| Gap | Detail |
|-----|--------|
| Moderation log: before/after state | `log_activity()` currently stores only a `message` string and `meta` JSON. No structured before/after snapshots of the modified entity. |
| Report resolution notes | No `resolution_note` or `handler_note` field on `ForumReport` to record why a report was resolved/dismissed. |
| Report filtering by target_type | `GET /api/v1/forum/reports` filters only by `status`. No filter for `target_type`, `reported_by`, date range, or pagination. |
| Report pagination | `list_reports()` returns all matching reports with no pagination (`.all()`). |
| Escalation notification | Setting a report to `escalated` does not notify admins or create any notification/alert. |
| Bulk report actions in admin UI | Backend `bulk-status` endpoint exists, but `manage/forum.html` + `manage_forum.js` do not surface bulk-select UI for reports. |
| Bulk thread/post actions in admin UI | Backend bulk endpoints exist, but admin UI does not expose them (no checkboxes or bulk-action bar). |
| Hide thread (single endpoint) | `POST /forum/threads/<id>/hide` and `POST /forum/threads/<id>/unhide` do not exist as standalone endpoints — thread hiding is done via status change only through archive or direct DB manipulation. The service functions `hide_thread()` and `unhide_thread()` exist but are not exposed via dedicated routes. |

### D. Performance and stability

| Gap | Detail |
|-----|--------|
| In-Python visibility filtering | `forum_category_threads()` fetches up to 1000 threads via `list_threads_for_category(page=1, per_page=1000)` then filters in Python. This is O(N) per request and will not scale. |
| Search loads all matches | `forum_search()` calls `.all()` on the query, applies visibility in Python, then slices. No SQL-level pagination for visibility-filtered results. |
| Missing index on `ForumPost.status` | Post status filtering (hidden, deleted) has no dedicated index. |
| Missing index on `ForumThread.status` | Thread status filtering (deleted, hidden, archived) has no dedicated index. |
| Missing index on `Notification.user_id + is_read` | Notification list for user with unread filter has no composite index. |
| No forum-specific test for related threads (News/Wiki) | `test_forum_api.py` and `test_news_api.py` do not test the related-threads CRUD endpoints or the discussion-thread link/unlink flows. |
| No test for bulk thread status endpoint | `test_forum_api.py` does not test `POST /forum/moderation/bulk-threads/status`. |
| No test for bulk post hide endpoint | `test_forum_api.py` does not test `POST /forum/moderation/bulk-posts/hide`. |
| No test for moderation log endpoint | `test_forum_api.py` does not test `GET /forum/moderation/log`. |
| No test for forum tag CRUD via thread tagging | Only `test_forum_search_filter_by_tag_and_category` creates tags; no dedicated tag lifecycle tests. |
| No test for bookmark removal | `test_thread_bookmark_create_and_list` tests create+list but not unbookmark. |
| Coverage gate | Must remain >= 85%. Any new code must have corresponding tests. |

---

## Expected files to change

### Models
- `backend/app/models/forum.py` — possible: add `ForumPostReaction` (if reactions are pursued), add `resolution_note` field concept (though belongs on ForumReport)
- `backend/app/models/forum.py` — extend `ForumReport` with `resolution_note` field

### Migrations
- New migration `027_*` — add `resolution_note` to `forum_reports`; add indexes on `ForumPost.status`, `ForumThread.status`, `Notification(user_id, is_read)`

### Routes
- `backend/app/api/v1/forum_routes.py` — add hide/unhide thread routes; enhance report list with pagination + filters; add tag listing endpoint; add `bookmarked_by_me` to thread list; add tags to thread list
- `backend/app/api/v1/news_routes.py` — potentially add auto-create discussion thread on publish
- `backend/app/api/v1/wiki_admin_routes.py` — same potential auto-create

### Services
- `backend/app/services/forum_service.py` — add `list_reports` pagination/filters; add tag admin helpers; optimize visibility-filtered queries
- `backend/app/services/news_service.py` — potential auto-create discussion thread helper
- `backend/app/services/wiki_service.py` — same

### Tests
- `backend/tests/test_forum_api.py` — add tests for: bulk thread/post endpoints, moderation log, bookmark removal, tag lifecycle, hide/unhide thread routes, report filtering/pagination, related threads
- `backend/tests/test_news_api.py` — add tests for discussion-thread link/unlink and related-threads CRUD
- `backend/tests/test_wiki_api.py` — same for wiki

### Frontend templates
- `administration-tool/templates/news_detail.html` — add "Discuss" link and related threads display
- `administration-tool/templates/wiki_public.html` — add "Discuss" link and related threads display
- `administration-tool/templates/manage/news.html` — add discussion-thread and related-threads management UI
- `administration-tool/templates/manage/wiki.html` — same
- `administration-tool/templates/manage/forum.html` — add bulk-select UI for reports and threads
- `administration-tool/templates/forum/category.html` — add tag display per thread, bookmark indicator
- `administration-tool/templates/forum/thread.html` — ensure tags render, bookmark button

### Frontend JS
- `administration-tool/static/news.js` — add discuss link rendering, related threads
- `administration-tool/static/manage_news.js` — add discussion/related thread admin UI
- `administration-tool/static/manage_wiki.js` — same
- `administration-tool/static/manage_forum.js` — add bulk-select UI
- `administration-tool/static/forum.js` — add bookmark indicator, tags in list, discuss entry points

### Postman
- `postman/WorldOfShadows_API.postman_collection.json` — add any new endpoints, update existing ones

### Docs
- `backend/docs/FORUM_MODULE.md` — update with new endpoints and models
- `docs/FORUM_INTEGRATION_WAVE_DELTA.md` — this file

---

## Must NOT be broadly refactored

1. **Auth model** — JWT + session dual-auth, `permissions.py` decorators, and role hierarchy must remain as-is. Do not change `require_jwt_admin`, `require_jwt_moderator_or_admin`, or role-checking helpers.

2. **Activity log service** — `log_activity()` interface and `ActivityLog` model must not change shape. Add forum-specific metadata within existing `meta` JSON field; do not add new columns to `activity_logs`.

3. **Multilingual content architecture** — `NewsArticle`/`NewsArticleTranslation` and `WikiPage`/`WikiPageTranslation` patterns, language fallback logic, and translation status flow must not be restructured.

4. **Existing forum soft-delete semantics** — Status values (`open`, `locked`, `archived`, `hidden`, `deleted`) and `deleted_at` field behavior are stable. Do not change the meaning of existing statuses.

5. **Migration numbering** — Continue sequential numbering from 027. Do not renumber or merge existing migrations.

6. **Existing test fixtures** — `conftest.py` fixtures (`test_user`, `auth_headers`, `moderator_user`, `moderator_headers`, `admin_user`, `admin_headers`, etc.) must not be modified. Add new fixtures alongside.

7. **n8n integration** — `n8n_trigger.py` and webhook flow must not be modified in this wave.

8. **Data export/import** — `data_routes.py`, `data_export_service.py`, `data_import_service.py` are out of scope.

9. **Area-based feature access** — `feature_registry.py`, area models, and `allowed_features` in `/auth/me` must not be restructured. New forum features may be registered but the system itself stays.

---

## Highest integrity and performance risks

### 1. In-Python visibility filtering (HIGH)

`forum_category_threads()` loads up to 1000 threads per request and filters in Python. `forum_search()` loads ALL matching threads and filters in Python. Both patterns will cause:
- Increasing latency as thread count grows
- Memory pressure under concurrent load
- Incorrect pagination totals (SQL total != visible total)

**Mitigation:** Push visibility predicates into SQL where possible (join on category access rules, exclude deleted/hidden at query level for non-moderators). Accept that some edge cases (dynamic role checks) may still need Python filtering but limit the window.

### 2. N+1 queries in post list (MEDIUM)

`forum_thread_posts()` iterates over posts and queries `ForumPostLike` per post to compute `liked_by_me`. With 20 posts per page this is 20 extra queries.

**Mitigation:** Batch-load likes for the current user in one query before iterating.

### 3. Moderation log lacks before/after snapshots (MEDIUM)

Current `log_activity()` stores a free-text message. There is no structured diff of what changed (e.g., thread status before vs. after). This makes audit reconstruction unreliable for compliance.

**Mitigation:** Use the existing `meta` JSON field to store `{"before": {...}, "after": {...}}` dicts. Do not add new columns.

### 4. Report list has no pagination (MEDIUM)

`list_reports()` returns `.all()` with no limit. As reports accumulate, this endpoint will slow down and consume memory.

**Mitigation:** Add page/limit to `list_reports()` and `GET /api/v1/forum/reports`.

### 5. Tag normalization edge cases (LOW)

`_normalize_tag_value()` uses a regex that may produce empty slugs for non-Latin input. The backslash before the hyphen in the character class (`[^a-z0-9\\-_]`) is suspicious and may not behave as intended.

**Mitigation:** Verify regex behavior and fix if needed. Add test cases for Unicode and edge-case tag inputs.

### 6. Race condition in like_count (LOW)

`like_post()` reads `post.like_count`, increments in Python, and commits. Under concurrent likes, the count can drift. Same for `unlike_post()`.

**Mitigation:** Use `UPDATE ... SET like_count = like_count + 1` or periodic recount. Accept low risk for current scale.

### 7. Auto-create discussion thread integrity (LOW, new feature)

If auto-creation of discussion threads on news/wiki publish is added, there is a risk of orphaned threads if publish is rolled back, or duplicate threads on retry.

**Mitigation:** Create thread within the same transaction as publish. Use idempotency check (if `discussion_thread_id` already set, skip).
