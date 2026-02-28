"""
skills/web_search.py
Google search skill — navigates to Google, searches, extracts results text.
"""

from playwright.sync_api import Page


def search_google(page: Page, query: str) -> str:
    """
    Navigate to Google, search for query, and return the visible results text.
    """
    from urllib.parse import quote_plus

    search_url = f"https://www.google.com/search?q={quote_plus(query)}"

    try:
        page.goto(search_url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

        # Try to extract search result snippets
        from modules.browser_capabilities import extract_page_text
        return extract_page_text(page, max_chars=3000)

    except Exception as e:
        return f"[Google search failed: {e}]"
