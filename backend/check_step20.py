# check_step20.py
import os
from app.response.executor import plan_actions, execute_action, rollback_action, get_all_actions

print("=== STEP 20 VERIFICATION ===\n")

# Clean up from previous runs
if os.path.exists("blocklist.txt"):
    os.remove("blocklist.txt")

# 1. Simulate the output from our Policy Engine (Step 18)
mock_decision = {
    "decision": "high",
    "actions": ["block_url", "report_registrar", "ticket"],
    "needs_approval": True
}
mock_evidence = {
    "domain": {"registered_domain": "acmepay-secure-login.com"},
    "summary": "Domain imitates acmepay.com. Password form posts to other host."
}

print("--- 1. Planning Actions ---")
actions = plan_actions(case_id=101, decision=mock_decision, ev=mock_evidence)
for a in actions:
    print(f"Action {a['id']}: {a['type']} (State: {a['state']})")

# 2. Analyst Approves and Executes the block action
print("\n--- 2. Analyst Approves 'block_url' Action ---")
block_action_id = actions[0]["id"]
executed_act = execute_action(block_action_id, approver="analyst_saipranav")
print(f"New State: {executed_act['state']}")

# Verify the file was created
print("\nChecking blocklist.txt...")
if os.path.exists("blocklist.txt"):
    with open("blocklist.txt", "r") as f:
        content = f.read().strip()
        print(f"blocklist.txt content: '{content}'")
        assert "acmepay-secure-login.com" in content
else:
    print("❌ blocklist.txt not found!")

# 3. Execute the report action
print("\n--- 3. Executing 'report_registrar' Action ---")
execute_action(actions[1]["id"])

# 4. Rollback the block
print("\n--- 4. Rolling back 'block_url' Action ---")
rolled_back = rollback_action(block_action_id, who="analyst_saipranav")
print(f"New State: {rolled_back['state']}")

# Verify blocklist is empty again
with open("blocklist.txt", "r") as f:
    content = f.read().strip()
    print(f"blocklist.txt after rollback: '{content}' (Should be empty)")
    assert content == ""

print("\n✅ SUCCESS: Response Executor simulated block, report, and rollback correctly.")
print("\n=== DONE ===")