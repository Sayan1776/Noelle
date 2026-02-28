from pathlib import Path
from typing import Optional
from playwright.sync_api import sync_playwright, Page, BrowserContext, Playwright
from urllib.parse import urlparse


class BrowserAgent:
    """
    Lazy-initialized browser agent.
    The browser is NOT launched until open_browser() is called.
    This prevents a blank tab from appearing before the user approves.
    """
    playwright: Optional[Playwright]
    context: Optional[BrowserContext]
    page: Optional[Page]
    headless: bool
    _launched: bool

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.playwright = None
        self.context = None
        self.page = None
        self._launched = False

    # --------------------------------------------------
    # Internal: start browser only when needed
    # --------------------------------------------------
    def _ensure_browser(self) -> None:
        """Launch Playwright and create a page ONLY when first needed."""
        if self._launched and self.page is not None:
            return

        self.playwright = sync_playwright().start()

        profile_dir = Path(__file__).resolve().parent.parent / "browser_profile"

        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=self.headless,
        )

        self.page = self.context.new_page()
        self._launched = True

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------
    def open_browser(self, url: str):
        """Navigate to a URL. Launches the browser on first call."""
        parsed = urlparse(url)
        if not parsed.scheme:
            raise ValueError(f"Invalid URL passed to open_browser: {url}")

        # Launch browser on-demand (only here, not in __init__)
        self._ensure_browser()

        self.page.goto(url)
        self.page.wait_for_load_state("domcontentloaded")
        self.accept_cookies_if_present()

    def accept_cookies_if_present(self) -> None:
        if self.page is None:
            return

        selectors = [
            "input#sp-cc-accept",
            "button#sp-cc-accept",
            "button:has-text('Accept')",
            "button:has-text('Accept All')",
            "button:has-text('Got it')",
            "button:has-text('I agree')",
        ]

        for selector in selectors:
            try:
                btn = self.page.locator(selector)
                if btn.count() > 0:
                    btn.first.click()
                    self.page.wait_for_timeout(1000)
                    return
            except Exception:
                pass

    def close(self) -> None:
        try:
            if self.context:
                self.context.close()
        except Exception:
            pass

        try:
            if self.playwright:
                self.playwright.stop()
        except Exception:
            pass

        self._launched = False
        self.page = None
        self.context = None
        self.playwright = None
