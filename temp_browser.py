from modules.action_agent import plan_actions
from modules.approval import request_approval
from modules.browser_agent import BrowserAgent
from skills.amazon import open_first_result, add_to_wishlist


# -----------------------------
# Helpers
# -----------------------------

def normalize_url(url: str) -> str:
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return "https://" + url


# -----------------------------
# Main
# -----------------------------

print("=" * 70)
print("PHASE 2.2 — AMAZON WISHLIST SKILL SANDBOX")
print("=" * 70)

# 🔒 EXPLICIT, SIDE-EFFECT-AUTHORIZING GOAL
goal = (
    "Open Amazon India and search for Pixel 8."
)

# -----------------------------
# PLAN
# -----------------------------

actions = plan_actions(goal)

if not actions:
    print("❌ No actions generated.")
    raise SystemExit(1)

# -----------------------------
# APPROVAL
# -----------------------------

approved = request_approval(actions)
if not approved:
    print("❌ Actions rejected by user.")
    raise SystemExit(1)

print("\n🚀 Executing approved actions...\n")

# -----------------------------
# EXECUTION
# -----------------------------

browser = BrowserAgent(headless=False)

try:
    # ---- Phase 2.1: Generic browser actions ----
    for action in actions:
        name = action.get("action")
        target = action.get("target")

        if not isinstance(name, str):
            raise RuntimeError("Invalid action: missing 'action'")

        if not isinstance(target, str):
            raise RuntimeError(f"Invalid action '{name}': missing 'target'")

        print(f"▶ Executing: {name} → {target}")

        if name == "open_browser":
            browser.open_browser(normalize_url(target))

        elif name == "search":
            browser.search(target)

        else:
            raise RuntimeError(f"Unsupported action: {name}")

    # ---- Phase 2.2: Amazon site-specific skills ----
    print("\n🧠 Amazon skill: open first search result")
    open_first_result(browser.page)

    print("🧠 Amazon skill: add to wishlist")
    result = add_to_wishlist(browser.page)
    print("✅", result)

    print("\n✅ Phase 2.2 execution completed successfully.")

finally:
    try:
        input("\nPress Enter to close browser...")
    finally:
        browser.close()
