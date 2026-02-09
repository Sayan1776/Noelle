from playwright.sync_api import sync_playwright
from pathlib import Path

from playwright.sync_api import sync_playwright


class BrowserAgent:
    def __init__(self, headless: bool = False):
        self.playwright = sync_playwright().start()
        profile_dir = Path(__file__).resolve().parent.parent / "browser_profile"
        # Persistent profile (keeps login)
        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir= str(profile_dir),
            headless=headless
        )

        self.page = self.context.new_page()

    def open_browser(self, url: str):
        self.page.goto(url)
        self.page.wait_for_load_state("domcontentloaded")
        self.accept_cookies_if_present()

    def accept_cookies_if_present(self):
        selectors = [
            "input#sp-cc-accept",
            "button#sp-cc-accept",
            "button:has-text('Accept')"
        ]
        for selector in selectors:
            try:
                btn = self.page.locator(selector)
                if btn.count() > 0:
                    btn.first.click()
                    self.page.wait_for_timeout(1000)
                    return
            except:
                pass

    def search(self, query: str):
        self.page.wait_for_selector("#twotabsearchtextbox", timeout=10000)
        box = self.page.locator("#twotabsearchtextbox").first
        box.fill(query)
        box.press("Enter")

        try:
            self.page.wait_for_selector("div.s-main-slot", timeout=10000)
        except:
            self.page.wait_for_timeout(3000)

    def close(self):
        try:
            self.context.close()
        except:
            pass
        try:
            self.playwright.stop()
        except:
            pass
