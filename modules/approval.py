from typing import List, Dict


def request_approval(actions: List[Dict[str, str]]) -> bool:
    """
    Ask the user to approve the planned actions.
    """

    print("\n🛑 ACTION PLAN (REQUIRES APPROVAL):\n")

    for i, action in enumerate(actions, 1):
        action_name = action.get("action", "UNKNOWN")
        target = action.get("target", "N/A")
        reason = action.get("reason", "No reason provided")

        print(f"{i}. {action_name} → {target}")
        print(f"   Reason: {reason}\n")


    choice = input("Approve these actions? (yes/no): ").strip().lower()
    return choice == "yes"
