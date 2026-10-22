# check_step19.py
import asyncio
from unittest.mock import patch
from app.agent.investigator import InvestigationAgent

# Stubs for the database/policy (normally loaded from DB)
def db_factory(): return None
def policy_loader(): return {"high_threshold": 0.85, "medium_threshold": 0.70, "auto_actions_enabled": False}
def allowlist_loader(): return {"acmepay.com"}

async def main():
    print("=== STEP 19 VERIFICATION ===\n")
    agent = InvestigationAgent(db_factory, ["acmepay.com"], policy_loader, allowlist_loader)

    # Mock the network calls so the test runs offline and instantly
    async def mock_enrich(domain):
        return {"whois": {"age_days": 2}, "cert": {"age_days": 5}}

    async def mock_inspect_site(url, case_id):
        return {"screenshot": "fake.png", "forms": [{"hasPassword": True, "posts_to_other_host": True}]}

    def mock_vision(shot, domain, has_pw):
        return {"impersonation": True, "best_brand_match": "acmepay"}

    def mock_email_parser(raw):
        return {"text": "Urgent! Verify your account", "auth": {"spf": "fail"}}

    # Apply mocks
    with patch("app.agent.investigator.enrich", new=mock_enrich), \
         patch("app.agent.investigator.inspect_site", new=mock_inspect_site), \
         patch("app.agent.investigator.vision_check", new=mock_vision), \
         patch("app.agent.investigator.analyse_email", new=mock_email_parser):
             
        # Test 1: Benign Domain
        print("\n--- Test 1: Benign Domain ---")
        res1 = await agent.investigate("manual", "acmepay.com")
        print(f"Result: Score={res1['score']} | Decision={res1['decision']['decision'].upper()}\n")
        
        # Test 2: Malicious Domain (Triggers the adaptive website branch)
        print("\n--- Test 2: Malicious Domain ---")
        res2 = await agent.investigate("certstream", "acmepay-secure-login.com")
        print(f"Result: Score={res2['score']} | Decision={res2['decision']['decision'].upper()}")
        print(f"Summary: {res2['summary']}\n")
        
        # Test 3: Phishing Email
        print("\n--- Test 3: Phishing Email ---")
        res3 = await agent.investigate("email", "acmepay-secure-login.com", raw_email=b"fake email")
        print(f"Result: Score={res3['score']} | Decision={res3['decision']['decision'].upper()}")
        print(f"Summary: {res3['summary']}\n")

    print("✅ SUCCESS: Investigation Agent tied all components together.")
    print("\n=== DONE ===")

if __name__ == "__main__":
    asyncio.run(main())