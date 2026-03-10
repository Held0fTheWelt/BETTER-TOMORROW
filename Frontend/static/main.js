/**
 * World of Shadows – public frontend
 * Config and shared helpers. API base URL from window.__FRONTEND_CONFIG__.backendApiUrl
 */
(function() {
    function getApiBaseUrl() {
        var c = window.__FRONTEND_CONFIG__;
        return (c && c.backendApiUrl) ? c.backendApiUrl : '';
    }
    window.FrontendConfig = {
        getApiBaseUrl: getApiBaseUrl
    };
})();
