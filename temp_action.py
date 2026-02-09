from modules.action_agent import plan_actions
from modules.approval import request_approval

print("=" * 70)
print("PHASE 2.0 — ACTION PLANNER SANDBOX")
print("=" * 70)

goal = "Open Amazon and search for Pixel 8"

actions = plan_actions(goal)

if not actions:
    print("❌ No actions generated.")
    exit()
print("\nRAW ACTION PLAN:")
print(actions)

approved = request_approval(actions)

if approved:
    print("\n✅ Actions approved (execution not implemented yet).")
else:
    print("\n❌ Actions rejected.")
