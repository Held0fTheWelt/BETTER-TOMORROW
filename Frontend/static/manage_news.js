/**
 * News management: list (with drafts), filters, pagination, create/edit, publish, unpublish, delete.
 */
(function() {
    var api = window.ManageAuth && window.ManageAuth.apiFetchWithAuth;
    if (!api) return;

    function $(id) { return document.getElementById(id); }
    function formatDate(iso) {
        if (!iso) return "";
        var d = new Date(iso);
        return isNaN(d.getTime()) ? "" : d.toLocaleDateString(undefined, { dateStyle: "short" });
    }

    var state = {
        page: 1,
        total: 0,
        perPage: 20,
        totalPages: 0,
        selectedId: null,
        items: [],
    };

    function getListParams() {
        var status = ($("manage-news-status") || {}).value;
        var params = {
            page: state.page,
            limit: state.perPage,
            q: ($("manage-news-q") || {}).value.trim() || undefined,
            category: ($("manage-news-category") || {}).value.trim() || undefined,
            sort: ($("manage-news-sort") || {}).value || "published_at",
            direction: ($("manage-news-direction") || {}).value || "desc",
        };
        if (status === "published") {
            params.published_only = "1";
        } else {
            params.include_drafts = "1";
        }
        return params;
    }

    function buildListUrl(params) {
        var parts = [];
        for (var k in params) if (params[k] !== undefined && params[k] !== "") parts.push(encodeURIComponent(k) + "=" + encodeURIComponent(params[k]));
        return "/api/v1/news" + (parts.length ? "?" + parts.join("&") : "");
    }

    function showLoading(show) {
        var loading = $("manage-news-loading");
        var wrap = $("manage-news-table-wrap");
        var empty = $("manage-news-empty");
        var err = $("manage-news-error");
        var pag = $("manage-news-pagination");
        if (loading) loading.hidden = !show;
        if (wrap) wrap.hidden = true;
        if (empty) empty.hidden = true;
        if (err) err.hidden = true;
        if (pag) pag.hidden = true;
    }

    function showError(msg) {
        showLoading(false);
        var wrap = $("manage-news-table-wrap");
        var empty = $("manage-news-empty");
        var err = $("manage-news-error");
        var pag = $("manage-news-pagination");
        if (wrap) wrap.hidden = true;
        if (empty) empty.hidden = true;
        if (err) { err.textContent = msg || "Failed to load."; err.hidden = false; }
        if (pag) pag.hidden = true;
    }

    function renderList(items, page, total, perPage) {
        showLoading(false);
        state.items = items || [];
        state.total = total || 0;
        state.perPage = perPage || 20;
        state.totalPages = perPage ? Math.ceil(total / perPage) : 0;

        var err = $("manage-news-error");
        var empty = $("manage-news-empty");
        var wrap = $("manage-news-table-wrap");
        var tbody = $("manage-news-tbody");
        var pag = $("manage-news-pagination");
        var pagInfo = $("manage-news-pagination-info");
        var prevBtn = $("manage-news-prev");
        var nextBtn = $("manage-news-next");

        if (err) err.hidden = true;
        if (items.length === 0) {
            if (empty) empty.hidden = false;
            if (wrap) wrap.hidden = true;
            if (pag) pag.hidden = true;
            return;
        }
        if (empty) empty.hidden = true;
        if (wrap) wrap.hidden = false;
        if (tbody) {
            tbody.innerHTML = "";
            items.forEach(function(item) {
                var tr = document.createElement("tr");
                tr.dataset.id = item.id;
                if (state.selectedId === item.id) tr.classList.add("selected");
                tr.innerHTML =
                    "<td>" + (item.title || "").replace(/</g, "&lt;") + "</td>" +
                    "<td>" + (item.is_published ? "Published" : "Draft") + "</td>" +
                    "<td>" + (item.category || "").replace(/</g, "&lt;") + "</td>" +
                    "<td>" + formatDate(item.updated_at || item.created_at) + "</td>";
                tr.addEventListener("click", function() { selectArticle(item.id); });
                tbody.appendChild(tr);
            });
        }
        if (pag) {
            pag.hidden = state.totalPages <= 1;
            if (pagInfo) pagInfo.textContent = "Page " + page + " of " + (state.totalPages || 1) + " (" + total + " total)";
            if (prevBtn) prevBtn.disabled = page <= 1;
            if (nextBtn) nextBtn.disabled = page >= state.totalPages;
        }
    }

    function fetchList() {
        var params = getListParams();
        showLoading(true);
        api(buildListUrl(params))
            .then(function(data) {
                var items = data.items || [];
                var status = ($("manage-news-status") || {}).value;
                if (status === "draft") {
                    items = items.filter(function(i) { return !i.is_published; });
                }
                var total = (status === "draft") ? items.length : (typeof data.total === "number" ? data.total : items.length);
                var page = typeof data.page === "number" ? data.page : 1;
                var perPage = typeof data.per_page === "number" ? data.per_page : 20;
                renderList(items, page, total, perPage);
            })
            .catch(function(e) {
                showError(e.message || "Failed to load news.");
            });
    }

    function selectArticle(id) {
        state.selectedId = id;
        var tbody = $("manage-news-tbody");
        if (tbody) {
            [].forEach.call(tbody.querySelectorAll("tr"), function(tr) {
                tr.classList.toggle("selected", parseInt(tr.dataset.id, 10) === id);
            });
        }
        var form = $("manage-news-form");
        var empty = $("manage-news-editor-empty");
        if (!id) {
            if (form) form.hidden = true;
            if (empty) empty.hidden = false;
            return;
        }
        if (empty) empty.hidden = true;
        if (form) form.hidden = false;
        api("/api/v1/news/" + id)
            .then(function(article) {
                ($("manage-news-id") || {}).value = article.id;
                ($("manage-news-title") || {}).value = article.title || "";
                ($("manage-news-slug") || {}).value = article.slug || "";
                ($("manage-news-summary") || {}).value = article.summary || "";
                ($("manage-news-content") || {}).value = article.content || "";
                ($("manage-news-category-edit") || {}).value = article.category || "";
                ($("manage-news-cover") || {}).value = article.cover_image || "";
                ($("manage-news-published") || {}).checked = !!article.is_published;
                var pubBtn = $("manage-news-publish-btn");
                var unpubBtn = $("manage-news-unpublish-btn");
                if (pubBtn) pubBtn.hidden = !!article.is_published;
                if (unpubBtn) unpubBtn.hidden = !article.is_published;
                ($("manage-news-editor-title") || {}).textContent = "Edit article";
            })
            .catch(function(e) {
                showError(e.message || "Failed to load article.");
            });
    }

    function showFormEmpty() {
        state.selectedId = null;
        ($("manage-news-id") || {}).value = "";
        ($("manage-news-title") || {}).value = "";
        ($("manage-news-slug") || {}).value = "";
        ($("manage-news-summary") || {}).value = "";
        ($("manage-news-content") || {}).value = "";
        ($("manage-news-category-edit") || {}).value = "";
        ($("manage-news-cover") || {}).value = "";
        ($("manage-news-published") || {}).checked = false;
        var form = $("manage-news-form");
        var empty = $("manage-news-editor-empty");
        if (form) form.hidden = true;
        if (empty) empty.hidden = false;
        ($("manage-news-editor-title") || {}).textContent = "Create / Edit";
    }

    function showFormSuccess(msg) {
        var el = $("manage-news-form-success");
        var err = $("manage-news-form-error");
        if (err) { err.hidden = true; err.textContent = ""; }
        if (el) { el.textContent = msg || "Saved."; el.hidden = false; }
        setTimeout(function() { if (el) el.hidden = true; }, 3000);
    }

    function showFormError(msg) {
        var el = $("manage-news-form-error");
        var ok = $("manage-news-form-success");
        if (ok) ok.hidden = true;
        if (el) { el.textContent = msg || "Error."; el.hidden = false; }
    }

    function onSave(e) {
        e.preventDefault();
        var idEl = $("manage-news-id");
        var id = (idEl && idEl.value) ? idEl.value.trim() : "";
        var title = ($("manage-news-title") || {}).value.trim();
        var slug = ($("manage-news-slug") || {}).value.trim();
        var content = ($("manage-news-content") || {}).value.trim();
        if (!title || !slug || !content) {
            showFormError("Title, slug, and content are required.");
            return;
        }
        var payload = {
            title: title,
            slug: slug,
            summary: ($("manage-news-summary") || {}).value.trim() || null,
            content: content,
            category: ($("manage-news-category-edit") || {}).value.trim() || null,
            cover_image: ($("manage-news-cover") || {}).value.trim() || null,
            is_published: !!($("manage-news-published") || {}).checked,
        };
        var saveBtn = $("manage-news-save");
        if (saveBtn) saveBtn.disabled = true;
        var req = id
            ? api("/api/v1/news/" + id, { method: "PUT", body: JSON.stringify(payload) })
            : api("/api/v1/news", { method: "POST", body: JSON.stringify(payload) });
        req.then(function(article) {
            showFormSuccess(id ? "Updated." : "Created.");
            if (saveBtn) saveBtn.disabled = false;
            state.selectedId = article.id;
            if (idEl) idEl.value = article.id;
            fetchList();
        }).catch(function(e) {
            showFormError(e.message || "Save failed.");
            if (saveBtn) saveBtn.disabled = false;
        });
    }

    function onPublish() {
        var id = ($("manage-news-id") || {}).value;
        if (!id) return;
        api("/api/v1/news/" + id + "/publish", { method: "POST" })
            .then(function() {
                showFormSuccess("Published.");
                selectArticle(parseInt(id, 10));
                fetchList();
            })
            .catch(function(e) {
                showFormError(e.message || "Publish failed.");
            });
    }

    function onUnpublish() {
        var id = ($("manage-news-id") || {}).value;
        if (!id) return;
        api("/api/v1/news/" + id + "/unpublish", { method: "POST" })
            .then(function() {
                showFormSuccess("Unpublished.");
                selectArticle(parseInt(id, 10));
                fetchList();
            })
            .catch(function(e) {
                showFormError(e.message || "Unpublish failed.");
            });
    }

    function onDelete() {
        var id = ($("manage-news-id") || {}).value;
        if (!id) return;
        if (!confirm("Delete this article? This cannot be undone.")) return;
        api("/api/v1/news/" + id, { method: "DELETE" })
            .then(function() {
                showFormEmpty();
                fetchList();
            })
            .catch(function(e) {
                showFormError(e.message || "Delete failed.");
            });
    }

    function onNew() {
        showFormEmpty();
        var form = $("manage-news-form");
        var empty = $("manage-news-editor-empty");
        if (empty) empty.hidden = true;
        if (form) form.hidden = false;
        ($("manage-news-editor-title") || {}).textContent = "New article";
        var pubBtn = $("manage-news-publish-btn");
        var unpubBtn = $("manage-news-unpublish-btn");
        if (pubBtn) pubBtn.hidden = true;
        if (unpubBtn) unpubBtn.hidden = true;
    }

    document.addEventListener("DOMContentLoaded", function() {
        var applyBtn = $("manage-news-apply");
        var newBtn = $("manage-news-new");
        var form = $("manage-news-form");
        var saveBtn = $("manage-news-save");
        var pubBtn = $("manage-news-publish-btn");
        var unpubBtn = $("manage-news-unpublish-btn");
        var delBtn = $("manage-news-delete-btn");
        var prevBtn = $("manage-news-prev");
        var nextBtn = $("manage-news-next");

        if (applyBtn) applyBtn.addEventListener("click", function() { state.page = 1; fetchList(); });
        if (newBtn) newBtn.addEventListener("click", onNew);
        if (form) form.addEventListener("submit", onSave);
        if (pubBtn) pubBtn.addEventListener("click", onPublish);
        if (unpubBtn) unpubBtn.addEventListener("click", onUnpublish);
        if (delBtn) delBtn.addEventListener("click", onDelete);
        if (prevBtn) prevBtn.addEventListener("click", function() {
            if (state.page > 1) { state.page--; fetchList(); }
        });
        if (nextBtn) nextBtn.addEventListener("click", function() {
            if (state.page < state.totalPages) { state.page++; fetchList(); }
        });

        fetchList();
    });
})();
