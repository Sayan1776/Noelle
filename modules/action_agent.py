from typing import List, Dict, Any
import json
import re
from core.llm import chat

Action = Dict[str, str]


def _extract_json(text: str) -> str | None:
    """Extract the first JSON array found in text."""
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        return match.group(0)
    return None


def _normalize_actions(actions: list[dict]) -> list[dict]:
    """
    Enforce action schema invariants.
    Invalid actions are dropped silently.
    """
    normalized: list[dict] = []

    for a in actions:
        action = a.get("action")
        target = a.get("target")

        # open_browser MUST have a valid target (URL)
        if action == "open_browser" and not target:
            continue

        # search and click MUST have a target
        if action in {"search", "click"} and not target:
            continue

        normalized.append(a)

    return normalized


def plan_actions(
    goal: str,
    allowed_actions: list[str],
    capabilities: Dict[str, Any],
) -> List[Action]:
    messages = [
        {
            "role": "system",
            "content": (
                "You are an action planner for a browser-based AI agent.\n\n"

                "RULES:\n"
                "1. You may ONLY use actions listed in AVAILABLE_ACTIONS.\n"
                "2. `open_browser` is a SPECIAL action and does NOT require CAPABILITIES.\n"
                "3. All other actions MUST reference targets present in CAPABILITIES.\n"
                "4. Some actions may include a `value` field.\n"
                "5. Values may be inferred from the USER GOAL.\n"
                "6. `fill_input` requires:\n"
                "   - target: input name from CAPABILITIES\n"
                "   - value: text to fill\n"
                "7. NEVER invent targets not present in CAPABILITIES.\n"
                "8. Output ONLY a valid JSON array.\n"
                "9. EVERY action MUST include a 'reason'.\n\n"

                "Allowed actions:\n"
                "- open_browser (target: full URL)\n"
                "- fill_input (target: input name, value: text)\n"
                "- click_link (target: visible link text)\n"
                "- click_button (target: visible button text)\n"
            )
        },
        {
            "role": "user",
            "content": f"""
USER GOAL:
{goal}

AVAILABLE_ACTIONS:
{allowed_actions}

CAPABILITIES (ground truth from page):
{capabilities}
"""
        }
    ]

    raw = chat(messages)

    # 🔍 Debug output (keep during development)
    print("\nRAW LLM RESPONSE:\n", raw)

    json_text = _extract_json(raw)
    if not json_text:
        return []

    try:
        data = json.loads(json_text)

        # Handle wrapped responses: { "actions": [...] }
        if isinstance(data, dict) and "actions" in data:
            data = data["actions"]

        if isinstance(data, list):
            return _normalize_actions(data)

    except json.JSONDecodeError:
        pass

    return []
