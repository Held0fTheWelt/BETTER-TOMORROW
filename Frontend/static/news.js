/**
 * World of Shadows – news pages
 * Fetches news list and detail from backend API. Handles missing API (404) gracefully.
 */
(function() {
    function getApiBase() {
        var c = window.__FRONTEND_CONFIG__;
        return (c && c.backendApiUrl) ? c.backendApiUrl : '';
    }

    function loadList() {
        var container = document.getElementById('news-list');
        var loading = document.getElementById('news-loading');
        var content = document.getElementById('news-list-content');
        var empty = document.getElementById('news-empty');
        var errEl = document.getElementById('news-error');
        var apiUrl = container ? container.getAttribute('data-api-url') : getApiBase();
        if (!apiUrl) apiUrl = getApiBase();

        function showLoading(v) {
            if (loading) loading.hidden = !v;
            if (content) content.hidden = true;
            if (empty) empty.hidden = true;
            if (errEl) errEl.hidden = true;
        }
        function showError(msg) {
            if (loading) loading.hidden = true;
            if (content) content.hidden = true;
            if (empty) empty.hidden = true;
            if (errEl) { errEl.textContent = msg || 'Failed to load news.'; errEl.hidden = false; }
        }
        function showEmpty() {
            if (loading) loading.hidden = true;
            if (content) content.hidden = true;
            if (empty) empty.hidden = false;
            if (errEl) errEl.hidden = true;
        }
        function showItems(items) {
            if (loading) loading.hidden = true;
            if (empty) empty.hidden = true;
            if (errEl) errEl.hidden = true;
            if (!content) return;
            content.innerHTML = '';
            items.forEach(function(item) {
                var link = document.createElement('a');
                link.href = '/news/' + item.id;
                var title = document.createElement('h3');
                title.textContent = item.title || 'Untitled';
                var meta = document.createElement('p');
                meta.className = 'meta';
                meta.textContent = (item.published_at || item.created_at || '') ? new Date(item.published_at || item.created_at).toLocaleDateString() : '';
                var div = document.createElement('div');
                div.className = 'news-item';
                div.appendChild(link);
                link.appendChild(title);
                link.appendChild(meta);
                content.appendChild(div);
            });
            content.hidden = false;
        }

        showLoading(true);
        fetch(apiUrl + '/api/v1/news', { method: 'GET', headers: { 'Accept': 'application/json' } })
            .then(function(res) {
                if (res.status === 404) {
                    showEmpty();
                    return;
                }
                if (!res.ok) {
                    showError('Could not load news.');
                    return;
                }
                return res.json();
            })
            .then(function(data) {
                if (data === undefined) return;
                var items = Array.isArray(data) ? data : (data.items || data.news || []);
                if (items.length === 0) showEmpty();
                else showItems(items);
            })
            .catch(function() { showEmpty(); });
    }

    function loadDetail(id) {
        var container = document.getElementById('news-detail');
        var loading = document.getElementById('news-detail-loading');
        var content = document.getElementById('news-detail-content');
        var errEl = document.getElementById('news-detail-error');
        var apiUrl = container ? container.getAttribute('data-api-url') : getApiBase();
        if (!apiUrl) apiUrl = getApiBase();

        function showLoading(v) {
            if (loading) loading.hidden = !v;
            if (content) content.hidden = true;
            if (errEl) errEl.hidden = true;
        }
        function showError(msg) {
            if (loading) loading.hidden = true;
            if (content) content.hidden = true;
            if (errEl) { errEl.textContent = msg || 'Failed to load article.'; errEl.hidden = false; }
        }
        function showArticle(article) {
            if (loading) loading.hidden = true;
            if (errEl) errEl.hidden = true;
            if (!content) return;
            var title = document.createElement('h1');
            title.textContent = article.title || 'Untitled';
            var meta = document.createElement('p');
            meta.className = 'meta';
            meta.textContent = (article.published_at || article.created_at) ? new Date(article.published_at || article.created_at).toLocaleDateString() : '';
            var body = document.createElement('div');
            body.className = 'body';
            body.textContent = article.content || article.body || '';
            content.innerHTML = '';
            content.appendChild(title);
            content.appendChild(meta);
            content.appendChild(body);
            content.hidden = false;
        }

        showLoading(true);
        fetch(apiUrl + '/api/v1/news/' + id, { method: 'GET', headers: { 'Accept': 'application/json' } })
            .then(function(res) {
                if (res.status === 404) {
                    showError('Article not found.');
                    return;
                }
                if (!res.ok) {
                    showError('Could not load article.');
                    return;
                }
                return res.json();
            })
            .then(function(data) {
                if (data) showArticle(data);
            })
            .catch(function() { showError('Could not load article.'); });
    }

    window.NewsApp = { loadList: loadList, loadDetail: loadDetail };
})();
