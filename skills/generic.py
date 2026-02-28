from playwright.sync_api import Page



def fill_input(page: Page, selector: str, value: str) -> str:
    field = page.locator(selector)
    if field.count() == 0:
        return "INPUT_NOT_FOUND"

    field.first.fill(value)
    field.first.press("Enter")
    page.wait_for_load_state("domcontentloaded")
    return "INPUT_FILLED"


def click_button(page: Page, label: str) -> str:
    btn = page.get_by_role("button", name=label)
    if btn.count() == 0:
        return "BUTTON_NOT_FOUND"

    btn.first.click()
    page.wait_for_load_state("domcontentloaded")
    return "BUTTON_CLICKED"


def click_link(page: Page, text: str) -> str:
    # Try partial match on accessible name
    links = page.get_by_role("link").filter(has_text=text)

    if links.count() == 0:
        return "LINK_NOT_FOUND"

    links.first.click()
    page.wait_for_load_state("domcontentloaded")
    return "LINK_CLICKED"