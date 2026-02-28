# modules/browser_capabilities.py
from playwright.sync_api import Page


def scan_capabilities(page: Page) -> dict:
    capabilities = {
        "links": [],
        "buttons": [],
        "inputs": {},
        "requires_login": False,
    }

    # -----------------------
    # LINKS (filtered)
    # -----------------------
    for link in page.get_by_role("link").all()[:30]:
        try:
            name = link.inner_text().strip()
            if not name:
                continue
            if len(name) > 60:
                continue
            if "\n" in name and len(name.splitlines()) > 2:
                continue

            capabilities["links"].append(name)
        except:
            pass

    # -----------------------
    # BUTTONS
    # -----------------------
    for btn in page.get_by_role("button").all()[:20]:
        try:
            name = btn.inner_text().strip()
            if name:
                capabilities["buttons"].append(name)
        except:
            pass

    # -----------------------
    # INPUTS (generic detection)
    # Scans for ALL visible inputs and maps them semantically
    # -----------------------

    # --- Search inputs (try multiple strategies) ---

    # Strategy 1: Amazon-style ID
    if page.locator("#twotabsearchtextbox").count() > 0:
        capabilities["inputs"]["search"] = "#twotabsearchtextbox"

    # Strategy 2: ARIA label containing "search"
    elif page.locator("input[aria-label*='Search' i]").count() > 0:
        capabilities["inputs"]["search"] = "input[aria-label*='Search' i]"

    # Strategy 3: type="search"
    elif page.locator("input[type='search']").count() > 0:
        capabilities["inputs"]["search"] = "input[type='search']"

    # Strategy 4: name or placeholder containing "search" or "query"
    elif page.locator("input[name*='search' i], input[name*='query' i], input[name*='q']").count() > 0:
        capabilities["inputs"]["search"] = "input[name*='search' i], input[name*='query' i], input[name*='q']"

    # Strategy 5: placeholder text containing "search"
    elif page.locator("input[placeholder*='Search' i], input[placeholder*='search' i]").count() > 0:
        capabilities["inputs"]["search"] = "input[placeholder*='Search' i]"

    # Strategy 6: YouTube-style
    elif page.locator("input#search").count() > 0:
        capabilities["inputs"]["search"] = "input#search"

    # --- Login inputs ---
    if page.locator("input[type='email'], input[name*='email' i]").count() > 0:
        capabilities["inputs"]["email"] = "input[type='email'], input[name*='email' i]"

    if page.locator("input[type='password']").count() > 0:
        capabilities["inputs"]["password"] = "input[type='password']"

    # --- Generic text inputs (catch-all for forms) ---
    generic_inputs = page.locator(
        "input[type='text']:visible, "
        "input:not([type]):visible, "
        "textarea:visible"
    )
    for i in range(min(generic_inputs.count(), 5)):
        try:
            inp = generic_inputs.nth(i)
            # Try to identify by name, placeholder, or aria-label
            name = (
                inp.get_attribute("name") or
                inp.get_attribute("placeholder") or
                inp.get_attribute("aria-label") or
                f"text_input_{i}"
            )
            selector = inp.get_attribute("id")
            if selector:
                selector = f"#{selector}"
            else:
                attr_name = inp.get_attribute("name")
                if attr_name:
                    selector = f"input[name='{attr_name}']"
                else:
                    continue  # Skip if we can't target it

            # Don't override search if already found
            key = name.lower().replace(" ", "_")
            if key not in capabilities["inputs"]:
                capabilities["inputs"][key] = selector
        except:
            pass

    # -----------------------
    # LOGIN DETECTION
    # -----------------------
    if page.get_by_text("Sign in").count() > 0:
        capabilities["requires_login"] = True
    if page.get_by_text("Log in").count() > 0:
        capabilities["requires_login"] = True

    return capabilities


def extract_page_text(page: Page, max_chars: int = 3000) -> str:
    """
    Extract visible text content from the current page.
    Truncates to max_chars to avoid overwhelming the LLM context.
    """
    try:
        raw_text = page.inner_text("body")
        # Collapse excessive whitespace
        import re
        cleaned = re.sub(r'\n{3,}', '\n\n', raw_text)
        cleaned = re.sub(r'[ \t]{2,}', ' ', cleaned)
        cleaned = cleaned.strip()

        if len(cleaned) > max_chars:
            cleaned = cleaned[:max_chars] + "\n\n... [truncated]"

        return cleaned
    except Exception as e:
        return f"[Error extracting page text: {e}]"
