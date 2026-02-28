"""
modules/web_browse.py
Fully generic web browsing handler for the agent pipeline.

Handles ANY website — not just hardcoded ones.

Pipeline:
1. Resolve URL (keyword shortcuts → LLM fallback → Google)
2. Launch browser + navigate
3. Scan page capabilities (generic)
4. Auto-detect or LLM-plan interactions
5. Request user approval
6. Execute interactions
7. Extract + summarize page content
8. Return summary for agent synthesis
"""

from core.llm import chat
from modules.browser_agent import BrowserAgent
from modules.browser_capabilities import scan_capabilities, extract_page_text
from modules.action_agent import plan_actions
from modules.approval import request_approval
from skills.generic import fill_input, click_link, click_button

import re
import atexit

# ──────────────────────────────────────────────
# Singleton browser (reused across calls)
# ──────────────────────────────────────────────
_browser_instance: BrowserAgent | None = None


def _get_browser() -> BrowserAgent:
    global _browser_instance
    if _browser_instance is None:
        _browser_instance = BrowserAgent()
        atexit.register(_browser_instance.close)
    return _browser_instance


# ──────────────────────────────────────────────
# QUICK SHORTCUTS (convenience, not a limitation)
# ──────────────────────────────────────────────
SITE_SHORTCUTS = {
    "amazon": "https://www.amazon.in/",
    "flipkart": "https://www.flipkart.com/",
    "youtube": "https://www.youtube.com/",
    "wikipedia": "https://en.wikipedia.org/",
    "github": "https://github.com/",
    "reddit": "https://www.reddit.com/",
    "twitter": "https://x.com/",
    "x.com": "https://x.com/",
    "stackoverflow": "https://stackoverflow.com/",
    "linkedin": "https://www.linkedin.com/",
    "imdb": "https://www.imdb.com/",
    "myntra": "https://www.myntra.com/",
    "swiggy": "https://www.swiggy.com/",
    "zomato": "https://www.zomato.com/",
}


def _resolve_target(user_input: str) -> dict:
    """
    Determine where to browse and what to do.
    Works for ANY website — uses shortcuts, direct URLs, or LLM resolution.

    Returns: {"url": str, "search_query": str|None, "goal": str}
    """
    text = user_input.lower()

    # ── 1. Check if user provided a direct URL ──
    url_match = re.search(r'(https?://\S+)', user_input)
    if url_match:
        return {
            "url": url_match.group(1),
            "search_query": None,
            "goal": user_input,
        }

    # ── 2. Check shortcuts for quick mapping ──
    matched_site = None
    for key, url in SITE_SHORTCUTS.items():
        if key in text:
            matched_site = url
            break

    if matched_site:
        search_query = _extract_search_query(user_input)
        return {
            "url": matched_site,
            "search_query": search_query,
            "goal": user_input,
        }

    # ── 3. LLM resolves the URL for ANY other site ──
    resolved = _llm_resolve_url(user_input)
    return resolved


def _llm_resolve_url(user_input: str) -> dict:
    """
    Ask the LLM to determine the URL for any website the user mentions.
    Falls back to Google search if no specific site is identified.
    """
    messages = [
        {
            "role": "system",
            "content": (
                "You are a URL resolver.\n"
                "Given a user's browsing request, determine:\n"
                "1. The full URL to navigate to (include https://)\n"
                "2. What to search for on the page (if applicable)\n\n"
                "If the user mentions a specific website or service, give its URL.\n"
                "If no specific site is mentioned, use Google: https://www.google.com/\n\n"
                "RESPOND IN EXACTLY THIS FORMAT (2 lines, nothing else):\n"
                "URL: <full url>\n"
                "QUERY: <search query or NONE>"
            )
        },
        {"role": "user", "content": user_input}
    ]

    response = _strip_think_tags(chat(messages))

    url = "https://www.google.com/"
    search_query = None

    for line in response.splitlines():
        line = line.strip()
        if line.upper().startswith("URL:"):
            parsed_url = line.split(":", 1)[1].strip()
            if parsed_url and not parsed_url.startswith("http"):
                parsed_url = "https://" + parsed_url
            if parsed_url:
                url = parsed_url
        elif line.upper().startswith("QUERY:"):
            q = line.split(":", 1)[1].strip()
            if q.upper() != "NONE" and q:
                search_query = q

    # If URL is Google and no query, extract one from the user input
    if "google.com" in url and not search_query:
        search_query = _extract_search_query(user_input)

    return {
        "url": url,
        "search_query": search_query,
        "goal": user_input,
    }


def _strip_think_tags(text: str) -> str:
    """Strip <think>...</think> blocks from deepseek-r1 model output."""
    cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    return cleaned.strip()


def _extract_search_query(user_input: str) -> str:
    """
    Extract the search query from natural language using keyword stripping.
    No LLM call needed — fast and reliable.

    "search jackets on myntra" → "jackets"
    "find iPhone 16 price on Amazon" → "iPhone 16 price"
    "open Amazon" → None
    """
    text = user_input.strip()

    # Phrases to remove (action phrases + site names) — WHOLE WORDS ONLY
    noise_phrases = [
        "search for", "search on", "search", "find",
        "look up", "look for", "browse for", "browse",
        "show me", "get me", "buy",
        "go to", "visit", "navigate to", "open",
    ]

    # Single noise words (articles, prepositions) — matched as whole words
    noise_singles = ["on", "in", "at", "from", "the", "a", "an"]

    # Start with the lowercase text for matching
    query = text.lower()

    # Remove multi-word phrases first (longest first)
    for phrase in sorted(noise_phrases, key=len, reverse=True):
        query = re.sub(r'\b' + re.escape(phrase) + r'\b', ' ', query)

    # Remove site names as whole words
    for site_key in SITE_SHORTCUTS:
        query = re.sub(r'\b' + re.escape(site_key) + r'\b', ' ', query)

    # Remove single noise words as whole words
    for word in noise_singles:
        query = re.sub(r'\b' + re.escape(word) + r'\b', ' ', query)

    # Collapse whitespace
    query = re.sub(r'\s+', ' ', query).strip()

    if not query or len(query) < 2:
        return None

    # Preserve original casing from user input
    original_words = user_input.split()
    query_words = query.split()
    result_words = []
    for qw in query_words:
        for ow in original_words:
            if ow.lower() == qw.lower():
                result_words.append(ow)
                break
        else:
            result_words.append(qw)

    return " ".join(result_words) if result_words else None



def _summarize_page(page_text: str, goal: str) -> str:
    """
    Use LLM to extract relevant information from raw page text.
    Produces a concise summary the persona can relay.
    """
    if not page_text or page_text.startswith("[Error"):
        return page_text

    truncated = page_text[:2000]

    messages = [
        {
            "role": "system",
            "content": (
                "You are reading a web page for the user.\n"
                "Extract ONLY the information relevant to their goal.\n"
                "Be concise and factual. List key findings.\n"
                "If you see products and prices, list them.\n"
                "If you see search results, summarize the top results.\n"
                "If you see article content, summarize the key points.\n"
                "Do NOT add information not present in the page.\n"
                "Maximum 8 lines."
            )
        },
        {
            "role": "user",
            "content": f"Goal: {goal}\n\nPage content:\n{truncated}"
        }
    ]

    return chat(messages)


def _try_search_on_page(browser, search_query: str, capabilities: dict) -> bool:
    """
    Attempt to find and use a search input on the current page.
    Uses an escalating set of fallback strategies to work on ANY site.
    Returns True if search was executed successfully.
    """
    page = browser.page

    # ── Strategy 1: Use capabilities-detected search selector ──
    search_selector = capabilities.get("inputs", {}).get("search")
    if search_selector:
        try:
            page.wait_for_selector(search_selector, timeout=5000)
            box = page.locator(search_selector).first
            box.click()
            box.fill(search_query)
            box.press("Enter")
            page.wait_for_timeout(3000)
            return True
        except Exception:
            print("  ⚠️ Strategy 1 (capabilities) failed, trying next...")

    # ── Strategy 2: ARIA role=searchbox ──
    try:
        searchbox = page.get_by_role("searchbox")
        if searchbox.count() > 0:
            searchbox.first.click()
            searchbox.first.fill(search_query)
            searchbox.first.press("Enter")
            page.wait_for_timeout(3000)
            return True
    except Exception:
        pass

    # ── Strategy 3: Any visible input with search-related attributes ──
    search_selectors = [
        "input[type='search']:visible",
        "input[name*='search' i]:visible",
        "input[name*='query' i]:visible",
        "input[name='q']:visible",
        "input[placeholder*='search' i]:visible",
        "input[placeholder*='find' i]:visible",
        "input[aria-label*='search' i]:visible",
        "input[class*='search' i]:visible",
        "input[id*='search' i]:visible",
        "input[data-testid*='search' i]:visible",
    ]

    for sel in search_selectors:
        try:
            loc = page.locator(sel)
            if loc.count() > 0:
                loc.first.click()
                page.wait_for_timeout(500)
                loc.first.fill(search_query)
                loc.first.press("Enter")
                page.wait_for_timeout(3000)
                return True
        except Exception:
            continue

    # ── Strategy 4: Click any visible text input near top of page ──
    try:
        all_inputs = page.locator(
            "input[type='text']:visible, "
            "input:not([type]):visible:not([type='hidden'])"
        )
        count = all_inputs.count()
        if count > 0:
            # Try the first visible input (often the search bar)
            first_input = all_inputs.first
            first_input.click()
            page.wait_for_timeout(500)
            first_input.fill(search_query)
            first_input.press("Enter")
            page.wait_for_timeout(3000)
            return True
    except Exception:
        pass

    # ── Strategy 5: Try Ctrl+K or "/" (common search shortcuts) ──
    try:
        page.keyboard.press("Control+k")
        page.wait_for_timeout(1000)

        # Check if a new focused input appeared
        focused = page.locator("*:focus")
        if focused.count() > 0:
            focused.first.fill(search_query)
            focused.first.press("Enter")
            page.wait_for_timeout(3000)
            return True
    except Exception:
        pass

    return False



# ──────────────────────────────────────────────
# MAIN ENTRY POINT
# ──────────────────────────────────────────────

def handle_browse(user_input: str) -> str:
    """
    Main entry point for the browse tool.
    Handles ANY website — known or unknown.

    Returns: summarized page content for the agent to synthesize.
    """
    INTERACTION_ACTIONS = ["fill_input", "click_link", "click_button"]

    print("\n🌐 Browser Agent activated...")

    # ── STEP 1: Resolve target ──
    target = _resolve_target(user_input)
    url = target["url"]
    goal = target["goal"]
    search_query = target.get("search_query")

    print(f"🔗 Target: {url}")
    print(f"🎯 Goal: {goal}")
    if search_query:
        print(f"🔍 Search query: {search_query}")

    # ── STEP 2: Get browser ──
    browser = _get_browser()

    # ── STEP 3: If it's a Google search, go directly via URL ──
    if "google.com" in url and search_query:
        from urllib.parse import quote_plus
        search_url = f"https://www.google.com/search?q={quote_plus(search_query)}"
        print(f"🔍 Searching Google for: {search_query}")

        entry_plan = [{
            "action": "open_browser",
            "target": search_url,
            "reason": f"Google search: {search_query}",
        }]
        if not request_approval(entry_plan):
            return "[Browse cancelled — user did not approve]"

        try:
            browser.open_browser(search_url)
            browser.page.wait_for_timeout(3000)
        except Exception as e:
            return f"[Google search failed: {e}]"

        raw_text = extract_page_text(browser.page, max_chars=2000)
        print("📝 Summarizing results...")
        summary = _summarize_page(raw_text, goal)
        return f"[Google Search Results for: {search_query}]\n\n{summary}"

    # ── STEP 4: Navigate to target site ──
    entry_plan = [{
        "action": "open_browser",
        "target": url,
        "reason": f"Navigate to {url} for: {goal}",
    }]

    if not request_approval(entry_plan):
        return "[Browse cancelled — user did not approve navigation]"

    try:
        print("🚀 Opening browser...")
        browser.open_browser(url)
        print("✅ Page loaded.")
    except Exception as e:
        return f"[Browser navigation failed: {e}]"

    # ── STEP 5: Scan capabilities (works on ANY site) ──
    capabilities = scan_capabilities(browser.page)

    cap_summary = []
    if capabilities["inputs"]:
        cap_summary.append(f"inputs: {list(capabilities['inputs'].keys())}")
    if capabilities["buttons"]:
        cap_summary.append(f"buttons: {len(capabilities['buttons'])} found")
    if capabilities["links"]:
        cap_summary.append(f"links: {len(capabilities['links'])} found")
    if capabilities["requires_login"]:
        cap_summary.append("⚠️ login required")
    if cap_summary:
        print(f"🧠 Capabilities: {', '.join(cap_summary)}")

    # ── STEP 6: If we have a search query, try to use site's search ──
    if search_query:
        print(f"🔍 Searching for: {search_query}")
        search_success = _try_search_on_page(browser, search_query, capabilities)
        if search_success:
            print("✅ Search executed on site.")
        else:
            print("⚠️ No search input found — will try interaction planning.")

    # ── STEP 7: LLM-driven interaction planning (for ANY page) ──
    # Re-scan capabilities after search (page may have changed)
    if search_query:
        capabilities = scan_capabilities(browser.page)

    interaction_actions = plan_actions(
        goal=goal,
        allowed_actions=INTERACTION_ACTIONS,
        capabilities=capabilities,
    )

    if interaction_actions:
        print("\n🛑 Planned interactions:")
        for i, a in enumerate(interaction_actions, 1):
            print(f"  {i}. {a['action']} → {a.get('target', 'N/A')}")
            print(f"     Reason: {a.get('reason', 'N/A')}")

        if request_approval(interaction_actions):
            print("\n🚀 Executing interactions...")
            for action in interaction_actions:
                act = action["action"]
                act_target = action.get("target")

                if act == "fill_input":
                    selector = capabilities.get("inputs", {}).get(act_target)
                    if not selector:
                        print(f"  ❌ No input for '{act_target}'")
                        continue
                    value = action.get("value", "")
                    result = fill_input(browser.page, selector, value)
                    print(f"  ✅ fill_input → {result}")

                elif act == "click_button":
                    if not act_target:
                        continue
                    result = click_button(browser.page, act_target)
                    print(f"  ✅ click_button → {result}")

                elif act == "click_link":
                    if not act_target:
                        continue
                    result = click_link(browser.page, act_target)
                    print(f"  ✅ click_link → {result}")

            # Wait for page to update after interactions
            browser.page.wait_for_timeout(2000)

    # ── STEP 8: Extract + summarize page content ──
    raw_text = extract_page_text(browser.page, max_chars=2000)
    print("📝 Summarizing page content...")
    summary = _summarize_page(raw_text, goal)

    result = f"[Browser Result from {url}]\nGoal: {goal}\n\n{summary}"
    print("✅ Browse complete.\n")
    return result
