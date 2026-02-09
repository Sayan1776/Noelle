from playwright.sync_api import Page, TimeoutError as PWTimeout


from playwright.sync_api import Page, TimeoutError as PWTimeout


def open_first_result(page: Page):
    # Wait for search results to render
    try:
        page.wait_for_selector("div.s-main-slot", timeout=15000)
    except PWTimeout:
        raise RuntimeError("Search results container not loaded")

    # Force scroll to trigger lazy loading
    page.mouse.wheel(0, 1500)
    page.wait_for_timeout(2000)

    # 🔑 Use ARIA role-based selector (MOST STABLE)
    product_links = page.get_by_role(
        "link",
        name="Pixel 8",
        exact=False
    )

    if product_links.count() == 0:
        page.screenshot(path="amazon_debug.png")
        raise RuntimeError("No product links found via ARIA role (see amazon_debug.png)")

    # Click the first product
    product_links.first.scroll_into_view_if_needed()
    product_links.first.click()
    page.wait_for_load_state("domcontentloaded")




def is_logged_in(page) -> bool:
    # If "Hello, Sign in" exists → NOT logged in
    sign_in = page.locator("#nav-link-accountList-nav-line-1")
    if sign_in.count() == 0:
        return False

    text = sign_in.first.inner_text().lower()
    return "sign in" not in text




def add_to_wishlist(page):
    try:
        # Amazon India uses "Add to List"
        page.wait_for_selector(
            "input#add-to-wishlist-button-submit, \
             span#add-to-wishlist-button, \
             a[data-action='add-to-wishlist']",
            timeout=6000
        )
    except PWTimeout:
        # Check if login prompt exists
        if page.get_by_text("Sign in").count() > 0:
            return "LOGIN_REQUIRED"

        return "WISHLIST_BUTTON_NOT_AVAILABLE"

    # Click wishlist
    page.locator(
        "input#add-to-wishlist-button-submit, \
         span#add-to-wishlist-button, \
         a[data-action='add-to-wishlist']"
    ).first.click()

    page.wait_for_timeout(2000)
    return "ADDED_TO_WISHLIST"