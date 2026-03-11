/**
 * Wiki editor: load GET /api/v1/wiki, edit in textarea, client-side preview, save PUT /api/v1/wiki.
 */
(function() {
    var api = window.ManageAuth && window.ManageAuth.apiFetchWithAuth;
    if (!api) return;

    function $(id) { return document.getElementById(id); }

    var initialContent = "";
    var dirty = false;

    function setDirty() {
        dirty = true;
        var el = $("manage-wiki-dirty");
        if (el) el.hidden = false;
    }

    function clearDirty() {
        dirty = false;
        var el = $("manage-wiki-dirty");
        if (el) el.hidden = true;
    }

    function updatePreview() {
        var textarea = $("manage-wiki-content");
        var preview = $("manage-wiki-preview");
        if (!textarea || !preview) return;
        var raw = textarea.value || "";
        if (typeof marked !== "undefined") {
            try {
                preview.innerHTML = marked.parse(raw);
            } catch (e) {
                preview.textContent = raw || "(empty)";
            }
        } else {
            preview.textContent = raw || "(empty)";
        }
    }

    function loadWiki() {
        var loading = $("manage-wiki-loading");
        var err = $("manage-wiki-error");
        var wrap = $("manage-wiki-editor-wrap");
        if (loading) loading.hidden = false;
        if (err) err.hidden = true;
        if (wrap) wrap.hidden = true;

        api("/api/v1/wiki")
            .then(function(data) {
                initialContent = data.content || "";
                var ta = $("manage-wiki-content");
                if (ta) ta.value = initialContent;
                dirty = false;
                if (loading) loading.hidden = true;
                if (wrap) wrap.hidden = false;
                updatePreview();
            })
            .catch(function(e) {
                if (loading) loading.hidden = true;
                if (err) {
                    err.textContent = e.message || "Failed to load wiki.";
                    err.hidden = false;
                }
            });
    }

    function onSave() {
        var ta = $("manage-wiki-content");
        if (!ta) return;
        var content = ta.value;
        var saveBtn = $("manage-wiki-save");
        var savedEl = $("manage-wiki-saved");
        if (saveBtn) saveBtn.disabled = true;
        api("/api/v1/wiki", { method: "PUT", body: JSON.stringify({ content: content }) })
            .then(function() {
                initialContent = content;
                clearDirty();
                if (savedEl) { savedEl.hidden = false; setTimeout(function() { savedEl.hidden = true; }, 3000); }
                if (saveBtn) saveBtn.disabled = false;
            })
            .catch(function(e) {
                if (savedEl) savedEl.hidden = true;
                var err = $("manage-wiki-error");
                if (err) { err.textContent = e.message || "Save failed."; err.hidden = false; }
                if (saveBtn) saveBtn.disabled = false;
            });
    }

    function checkUnload(e) {
        if (dirty) {
            e.preventDefault();
            e.returnValue = "";
        }
    }

    document.addEventListener("DOMContentLoaded", function() {
        var ta = $("manage-wiki-content");
        var saveBtn = $("manage-wiki-save");
        if (ta) {
            ta.addEventListener("input", function() {
                setDirty();
                updatePreview();
            });
            ta.addEventListener("change", updatePreview);
        }
        if (saveBtn) saveBtn.addEventListener("click", onSave);
        window.addEventListener("beforeunload", checkUnload);

        loadWiki();
    });
})();
