/**
 * World of Shadows – public forum frontend
 * Uses FrontendConfig.apiFetch (main.js) for GET; ManageAuth.apiFetchWithAuth for POST when logged in.
 * API: GET /api/v1/forum/categories, /forum/categories/<slug>, /forum/categories/<slug>/threads,
 *      GET /api/v1/forum/threads/<slug>, /forum/threads/<id>/posts;
 *      POST /api/v1/forum/categories/<slug>/threads, POST /api/v1/forum/threads/<id>/posts
 */
(function() {
    function getApiBase() {
        var fc = window.FrontendConfig;
        return (fc && fc.getApiBaseUrl) ? fc.getApiBaseUrl() : "";
    }

    function apiGet(path) {
        var url = (path.indexOf("/") === 0) ? path : "/api/v1/forum" + (path ? "/" + path : "");
        if (window.ManageAuth && window.ManageAuth.getToken && window.ManageAuth.getToken()) {
            return window.ManageAuth.apiFetchWithAuth(url);
        }
        var fc = window.FrontendConfig;
        var fn = (fc && fc.apiFetch) ? fc.apiFetch : function(u) {
            return fetch((getApiBase() || "") + (u.indexOf("/") === 0 ? u : "/" + u), { headers: { Accept: "application/json" } })
                .then(function(r) { if (!r.ok) throw new Error(r.statusText); return r.json(); });
        };
        return fn(url);
    }

    function apiPost(path, body) {
        var url = "/api/v1/forum" + (path.indexOf("/") === 0 ? path : "/" + path);
        var opts = { method: "POST", body: typeof body === "string" ? body : JSON.stringify(body || {}) };
        if (window.ManageAuth && window.ManageAuth.getToken && window.ManageAuth.getToken()) {
            return window.ManageAuth.apiFetchWithAuth(url, opts);
        }
        var fc = window.FrontendConfig;
        var base = getApiBase();
        var fullUrl = (base ? base.replace(/\/$/, "") : "") + url;
        return fetch(fullUrl, {
            method: "POST",
            headers: { "Accept": "application/json", "Content-Type": "application/json" },
            body: opts.body
        }).then(function(r) {
            if (r.status === 401) throw { status: 401, message: "Please log in to post." };
            if (!r.ok) return r.json().then(function(j) { throw { status: r.status, message: (j && j.error) || r.statusText }; });
            return r.json();
        });
    }

    function formatDate(iso) {
        if (!iso) return "";
        try {
            var d = new Date(iso);
            return isNaN(d.getTime()) ? "" : d.toLocaleDateString(undefined, { dateStyle: "medium" });
        } catch (e) { return ""; }
    }

    function escapeHtml(s) {
        if (s == null) return "";
        var div = document.createElement("div");
        div.textContent = s;
        return div.innerHTML;
    }

    // --- Index: categories list ---
    function initIndex() {
        var loading = document.getElementById("forum-loading");
        var content = document.getElementById("forum-categories");
        var empty = document.getElementById("forum-empty");
        var errEl = document.getElementById("forum-error");

        function showLoading(show) {
            if (loading) loading.hidden = !show;
            if (content) content.hidden = true;
            if (empty) empty.hidden = true;
            if (errEl) errEl.hidden = true;
        }
        function showError(msg) {
            if (loading) loading.hidden = true;
            if (content) content.hidden = true;
            if (empty) empty.hidden = true;
            if (errEl) { errEl.textContent = msg || "Failed to load forum."; errEl.hidden = false; }
        }
        function showList(items) {
            if (loading) loading.hidden = true;
            if (empty) empty.hidden = true;
            if (errEl) errEl.hidden = true;
            if (!content) return;
            content.innerHTML = "";
            items.forEach(function(cat) {
                var card = document.createElement("a");
                card.href = "/forum/categories/" + encodeURIComponent(cat.slug || "");
                card.className = "forum-category-card card card-link";
                var title = document.createElement("h2");
                title.className = "forum-category-title";
                title.textContent = cat.title || "Unnamed";
                card.appendChild(title);
                if (cat.description) {
                    var desc = document.createElement("p");
                    desc.className = "forum-category-desc muted";
                    desc.textContent = cat.description;
                    card.appendChild(desc);
                }
                content.appendChild(card);
            });
            content.hidden = false;
        }

        showLoading(true);
        apiGet("categories")
            .then(function(data) {
                var items = (data && data.items) ? data.items : [];
                if (items.length === 0) {
                    if (loading) loading.hidden = true;
                    if (content) content.hidden = true;
                    if (empty) empty.hidden = false;
                } else showList(items);
            })
            .catch(function(e) { showError(typeof e === "string" ? e : (e && e.message) || "Failed to load."); });
    }

    // --- Category: threads list + new thread modal ---
    function initCategory(categorySlug) {
        var loading = document.getElementById("forum-category-loading");
        var header = document.getElementById("forum-category-header");
        var actions = document.getElementById("forum-category-actions");
        var content = document.getElementById("forum-threads-content");
        var empty = document.getElementById("forum-category-empty");
        var errEl = document.getElementById("forum-category-error");
        var pagination = document.getElementById("forum-category-pagination");
        var paginationInfo = document.getElementById("forum-category-pagination-info");
        var prevBtn = document.getElementById("forum-category-prev");
        var nextBtn = document.getElementById("forum-category-next");
        var state = { page: 1, total: 0, perPage: 20, totalPages: 0, category: null };

        function showLoading(show) {
            if (loading) loading.hidden = !show;
            if (header) header.hidden = true;
            if (actions) actions.hidden = true;
            if (content) content.hidden = true;
            if (empty) empty.hidden = true;
            if (errEl) errEl.hidden = true;
            if (pagination) pagination.hidden = true;
        }
        function showError(msg) {
            if (loading) loading.hidden = true;
            if (header) header.hidden = true;
            if (actions) actions.hidden = true;
            if (content) content.hidden = true;
            if (empty) empty.hidden = true;
            if (errEl) { errEl.textContent = msg || "Failed to load."; errEl.hidden = false; }
            if (pagination) pagination.hidden = true;
        }
        function renderThreads(items, page, total, perPage) {
            if (loading) loading.hidden = true;
            if (empty) empty.hidden = true;
            if (errEl) errEl.hidden = true;
            if (!content) return;
            content.innerHTML = "";
            items.forEach(function(t) {
                var row = document.createElement("div");
                row.className = "forum-thread-row";
                var link = document.createElement("a");
                link.href = "/forum/threads/" + encodeURIComponent(t.slug || "");
                link.className = "forum-thread-link";
                var title = document.createElement("span");
                title.className = "forum-thread-title";
                title.textContent = t.title || "Untitled";
                if (t.is_pinned) {
                    var pin = document.createElement("span");
                    pin.className = "forum-badge forum-badge-pinned";
                    pin.textContent = "Pinned";
                    link.appendChild(pin);
                }
                link.appendChild(title);
                var meta = document.createElement("span");
                meta.className = "forum-thread-meta muted";
                var parts = [];
                if (t.reply_count != null) parts.push(t.reply_count + " replies");
                if (t.last_post_at) parts.push(formatDate(t.last_post_at));
                meta.textContent = parts.join(" · ");
                row.appendChild(link);
                row.appendChild(meta);
                content.appendChild(row);
            });
            content.hidden = false;
            if (actions) actions.hidden = false;
            state.total = total;
            state.totalPages = perPage > 0 ? Math.ceil(total / perPage) : 0;
            if (pagination) {
                pagination.hidden = state.totalPages <= 1;
                if (paginationInfo) paginationInfo.textContent = "Page " + page + " of " + (state.totalPages || 1) + " (" + total + " total)";
                if (prevBtn) prevBtn.disabled = page <= 1;
                if (nextBtn) nextBtn.disabled = page >= state.totalPages;
            }
        }

        function fetchCategory() {
            return apiGet("categories/" + encodeURIComponent(categorySlug));
        }
        function fetchThreads(page) {
            return apiGet("categories/" + encodeURIComponent(categorySlug) + "/threads?page=" + page + "&limit=" + state.perPage);
        }

        showLoading(true);
        fetchCategory()
            .then(function(cat) {
                state.category = cat;
                if (header) {
                    header.innerHTML = "";
                    var h1 = document.createElement("h1");
                    h1.className = "page-header forum-category-name";
                    h1.textContent = cat.title || "Category";
                    header.appendChild(h1);
                    if (cat.description) {
                        var p = document.createElement("p");
                        p.className = "muted";
                        p.textContent = cat.description;
                        header.appendChild(p);
                    }
                    header.hidden = false;
                }
                return fetchThreads(1);
            })
            .then(function(data) {
                var items = (data && data.items) ? data.items : [];
                var total = (data && typeof data.total === "number") ? data.total : items.length;
                var page = (data && typeof data.page === "number") ? data.page : 1;
                var perPage = (data && typeof data.per_page === "number") ? data.per_page : state.perPage;
                state.page = page;
                if (items.length === 0) {
                    if (loading) loading.hidden = true;
                    if (content) content.hidden = true;
                    if (empty) empty.hidden = false;
                    if (actions) actions.hidden = false;
                } else renderThreads(items, page, total, perPage);
            })
            .catch(function(e) { showError(typeof e === "string" ? e : (e && e.message) || "Failed to load."); });

        if (prevBtn) prevBtn.addEventListener("click", function() {
            if (state.page <= 1) return;
            state.page--;
            showLoading(true);
            fetchThreads(state.page).then(function(data) {
                var items = (data && data.items) ? data.items : [];
                var total = (data && typeof data.total === "number") ? data.total : 0;
                var page = (data && typeof data.page === "number") ? data.page : state.page;
                var perPage = (data && typeof data.per_page === "number") ? data.per_page : state.perPage;
                renderThreads(items, page, total, perPage);
            }).catch(function(e) { showError(e && e.message); });
        });
        if (nextBtn) nextBtn.addEventListener("click", function() {
            if (state.page >= state.totalPages) return;
            state.page++;
            showLoading(true);
            fetchThreads(state.page).then(function(data) {
                var items = (data && data.items) ? data.items : [];
                var total = (data && typeof data.total === "number") ? data.total : 0;
                var page = (data && typeof data.page === "number") ? data.page : state.page;
                var perPage = (data && typeof data.per_page === "number") ? data.per_page : state.perPage;
                renderThreads(items, page, total, perPage);
            }).catch(function(e) { showError(e && e.message); });
        });

        // New thread modal
        var newThreadBtn = document.getElementById("forum-new-thread-btn");
        var modal = document.getElementById("forum-new-thread-modal");
        var loginHint = document.getElementById("forum-new-thread-login-hint");
        var form = document.getElementById("forum-new-thread-form");
        var formError = document.getElementById("forum-new-thread-error");
        var titleInput = document.getElementById("forum-new-thread-title-input");
        var contentInput = document.getElementById("forum-new-thread-content");
        var submitBtn = document.getElementById("forum-new-thread-submit");
        var cancelBtn = document.getElementById("forum-new-thread-cancel");

        if (newThreadBtn) newThreadBtn.addEventListener("click", function(e) {
            e.preventDefault();
            if (!modal) return;
            var hasToken = window.ManageAuth && window.ManageAuth.getToken && window.ManageAuth.getToken();
            if (loginHint) loginHint.hidden = !!hasToken;
            if (form) form.hidden = !hasToken;
            if (formError) { formError.hidden = true; formError.textContent = ""; }
            if (titleInput) titleInput.value = "";
            if (contentInput) contentInput.value = "";
            modal.hidden = false;
        });
        if (cancelBtn) cancelBtn.addEventListener("click", function() { if (modal) modal.hidden = true; });
        if (form) form.addEventListener("submit", function(e) {
            e.preventDefault();
            var title = (titleInput && titleInput.value) ? titleInput.value.trim() : "";
            var content = (contentInput && contentInput.value) ? contentInput.value.trim() : "";
            if (!title || !content) {
                if (formError) { formError.textContent = "Title and content are required."; formError.hidden = false; }
                return;
            }
            if (submitBtn) submitBtn.disabled = true;
            apiPost("categories/" + encodeURIComponent(categorySlug) + "/threads", { title: title, content: content })
                .then(function(thread) {
                    if (modal) modal.hidden = true;
                    window.location.href = "/forum/threads/" + encodeURIComponent(thread.slug || thread.id);
                })
                .catch(function(err) {
                    if (formError) {
                        formError.textContent = (err && err.message) || "Failed to create thread.";
                        formError.hidden = false;
                    }
                    if (submitBtn) submitBtn.disabled = false;
                });
        });
    }

    // --- Thread: detail + posts + reply ---
    function initThread(threadSlug) {
        var loading = document.getElementById("forum-thread-loading");
        var header = document.getElementById("forum-thread-header");
        var content = document.getElementById("forum-posts-content");
        var empty = document.getElementById("forum-thread-empty");
        var errEl = document.getElementById("forum-thread-error");
        var pagination = document.getElementById("forum-thread-pagination");
        var paginationInfo = document.getElementById("forum-thread-pagination-info");
        var prevBtn = document.getElementById("forum-thread-prev");
        var nextBtn = document.getElementById("forum-thread-next");
        var replySection = document.getElementById("forum-reply-section");
        var replyLoginHint = document.getElementById("forum-reply-login-hint");
        var replyForm = document.getElementById("forum-reply-form");
        var replyError = document.getElementById("forum-reply-error");
        var replyContent = document.getElementById("forum-reply-content");
        var replySubmit = document.getElementById("forum-reply-submit");
        var state = { thread: null, page: 1, total: 0, perPage: 20, totalPages: 0 };

        var backCategory = document.getElementById("forum-thread-back-category");
        var backCategoryBottom = document.getElementById("forum-thread-back-category-bottom");

        function setBackLink(href) {
            if (backCategory) backCategory.href = href || "#";
            if (backCategoryBottom) backCategoryBottom.href = href || "#";
        }

        function showLoading(show) {
            if (loading) loading.hidden = !show;
            if (header) header.hidden = true;
            if (content) content.hidden = true;
            if (empty) empty.hidden = true;
            if (errEl) errEl.hidden = true;
            if (pagination) pagination.hidden = true;
        }
        function showError(msg) {
            if (loading) loading.hidden = true;
            if (header) header.hidden = true;
            if (content) content.hidden = true;
            if (empty) empty.hidden = true;
            if (errEl) { errEl.textContent = msg || "Failed to load."; errEl.hidden = false; }
            if (pagination) pagination.hidden = true;
        }
        function renderPosts(items, page, total, perPage) {
            if (loading) loading.hidden = true;
            if (empty) empty.hidden = true;
            if (errEl) errEl.hidden = true;
            if (!content) return;
            content.innerHTML = "";
            items.forEach(function(p) {
                var post = document.createElement("article");
                post.className = "forum-post";
                post.dataset.postId = p.id;
                var meta = document.createElement("div");
                meta.className = "forum-post-meta";
                meta.innerHTML = "<span class=\"forum-post-date\">" + escapeHtml(formatDate(p.created_at)) + "</span>";
                if (p.edited_at) meta.innerHTML += " <span class=\"muted\">(edited " + escapeHtml(formatDate(p.edited_at)) + ")</span>";
                var body = document.createElement("div");
                body.className = "forum-post-body";
                body.textContent = p.content || "";
                post.appendChild(meta);
                post.appendChild(body);
                content.appendChild(post);
            });
            content.hidden = false;
            if (replySection) replySection.hidden = false;
            state.total = total;
            state.totalPages = perPage > 0 ? Math.ceil(total / perPage) : 0;
            if (pagination) {
                pagination.hidden = state.totalPages <= 1;
                if (paginationInfo) paginationInfo.textContent = "Page " + page + " of " + (state.totalPages || 1) + " (" + total + " total)";
                if (prevBtn) prevBtn.disabled = page <= 1;
                if (nextBtn) nextBtn.disabled = page >= state.totalPages;
            }
        }

        showLoading(true);
        apiGet("threads/" + encodeURIComponent(threadSlug))
            .then(function(thread) {
                state.thread = thread;
                if (header) {
                    header.innerHTML = "";
                    var h1 = document.createElement("h1");
                    h1.className = "forum-thread-title";
                    h1.textContent = thread.title || "Thread";
                    header.appendChild(h1);
                    var meta = document.createElement("p");
                    meta.className = "forum-thread-meta muted";
                    var parts = [];
                    if (thread.reply_count != null) parts.push(thread.reply_count + " replies");
                    if (thread.view_count != null) parts.push(thread.view_count + " views");
                    if (thread.created_at) parts.push(formatDate(thread.created_at));
                    meta.textContent = parts.join(" · ");
                    header.appendChild(meta);
                    if (thread.category && thread.category.slug) {
                        setBackLink("/forum/categories/" + encodeURIComponent(thread.category.slug));
                    }
                    header.hidden = false;
                }
                var threadId = thread.id;
                return apiGet("threads/" + threadId + "/posts?page=1&limit=" + state.perPage);
            })
            .then(function(data) {
                var items = (data && data.items) ? data.items : [];
                var total = (data && typeof data.total === "number") ? data.total : items.length;
                var page = (data && typeof data.page === "number") ? data.page : 1;
                var perPage = (data && typeof data.per_page === "number") ? data.per_page : state.perPage;
                state.page = page;
                if (items.length === 0) {
                    if (loading) loading.hidden = true;
                    if (content) content.hidden = true;
                    if (empty) empty.hidden = false;
                    if (replySection) replySection.hidden = false;
                } else renderPosts(items, page, total, perPage);
            })
            .catch(function(e) { showError(typeof e === "string" ? e : (e && e.message) || "Failed to load."); });

        function fetchPosts(page) {
            return apiGet("threads/" + state.thread.id + "/posts?page=" + page + "&limit=" + state.perPage);
        }
        if (prevBtn) prevBtn.addEventListener("click", function() {
            if (state.page <= 1 || !state.thread) return;
            state.page--;
            fetchPosts(state.page).then(function(data) {
                var items = (data && data.items) ? data.items : [];
                var total = (data && typeof data.total === "number") ? data.total : 0;
                var page = (data && typeof data.page === "number") ? data.page : state.page;
                var perPage = (data && typeof data.per_page === "number") ? data.per_page : state.perPage;
                renderPosts(items, page, total, perPage);
            }).catch(function(e) { showError(e && e.message); });
        });
        if (nextBtn) nextBtn.addEventListener("click", function() {
            if (state.page >= state.totalPages || !state.thread) return;
            state.page++;
            fetchPosts(state.page).then(function(data) {
                var items = (data && data.items) ? data.items : [];
                var total = (data && typeof data.total === "number") ? data.total : 0;
                var page = (data && typeof data.page === "number") ? data.page : state.page;
                var perPage = (data && typeof data.per_page === "number") ? data.per_page : state.perPage;
                renderPosts(items, page, total, perPage);
            }).catch(function(e) { showError(e && e.message); });
        });

        var hasToken = window.ManageAuth && window.ManageAuth.getToken && window.ManageAuth.getToken();
        if (replyLoginHint) replyLoginHint.hidden = !!hasToken;
        if (replyForm) replyForm.hidden = !hasToken;

        if (replyForm) replyForm.addEventListener("submit", function(e) {
            e.preventDefault();
            if (!state.thread) return;
            var contentText = (replyContent && replyContent.value) ? replyContent.value.trim() : "";
            if (!contentText) return;
            if (replySubmit) replySubmit.disabled = true;
            if (replyError) { replyError.hidden = true; replyError.textContent = ""; }
            apiPost("threads/" + state.thread.id + "/posts", { content: contentText })
                .then(function() {
                    if (replyContent) replyContent.value = "";
                    state.total++;
                    state.totalPages = Math.ceil(state.total / state.perPage);
                    state.page = state.totalPages;
                    return fetchPosts(state.page);
                })
                .then(function(data) {
                    var items = (data && data.items) ? data.items : [];
                    var total = (data && typeof data.total === "number") ? data.total : state.total;
                    var page = (data && typeof data.page === "number") ? data.page : state.page;
                    var perPage = (data && typeof data.per_page === "number") ? data.per_page : state.perPage;
                    state.total = total;
                    renderPosts(items, page, total, perPage);
                    if (content) content.scrollIntoView({ behavior: "smooth" });
                    if (replySubmit) replySubmit.disabled = false;
                })
                .catch(function(err) {
                    if (replyError) {
                        replyError.textContent = (err && err.message) || "Failed to post.";
                        replyError.hidden = false;
                    }
                    if (replySubmit) replySubmit.disabled = false;
                });
        });
    }

    window.ForumApp = {
        initIndex: initIndex,
        initCategory: initCategory,
        initThread: initThread
    };
})();
