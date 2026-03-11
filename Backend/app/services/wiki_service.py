"""Wiki: page and translation lookup. Supports DB-backed pages with fallback."""

from flask import current_app

from app.extensions import db
from app.i18n import get_default_language, normalize_language
from app.models import WikiPage, WikiPageTranslation


def get_wiki_page_by_key(key: str):
    """Return WikiPage by key or None."""
    if not key or not isinstance(key, str):
        return None
    return WikiPage.query.filter_by(key=key.strip()).first()


def get_wiki_translation(page_id: int, language_code: str) -> WikiPageTranslation | None:
    """Return WikiPageTranslation for page and language, or None."""
    if not page_id or not language_code:
        return None
    return WikiPageTranslation.query.filter_by(
        page_id=page_id,
        language_code=language_code.strip().lower(),
    ).first()


def get_effective_wiki_translation(page: WikiPage, lang: str | None):
    """Return translation for page using fallback: lang -> first translation -> config default."""
    codes = []
    if lang and normalize_language(lang):
        codes.append(normalize_language(lang))
    # No explicit "default_language" on WikiPage; use first translation or config default
    first = WikiPageTranslation.query.filter_by(page_id=page.id).first()
    if first and first.language_code not in codes:
        codes.append(first.language_code)
    codes.append(get_default_language())
    for code in codes:
        t = get_wiki_translation(page.id, code)
        if t:
            return t
    return None


def get_wiki_markdown_for_display(lang: str | None = None) -> str | None:
    """
    Return markdown content for the default wiki page (key=index) in the given or default language.
    Used for backward-compatible wiki display. Returns None if no page in DB.
    """
    page = get_wiki_page_by_key("index")
    if not page:
        return None
    trans = get_effective_wiki_translation(page, lang)
    if not trans:
        return None
    return trans.content_markdown or ""
