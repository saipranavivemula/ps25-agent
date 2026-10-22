# gen_url_data.py
import csv
import random

benign_domains = [
    "google.com", "github.com", "microsoft.com", "apple.com", "amazon.com",
    "wikipedia.org", "stackoverflow.com", "python.org", "fastapi.tiangolo.com",
    "nytimes.com", "bbc.co.uk", "reddit.com", "medium.com", "netflix.com",
    "linkedin.com", "zoom.us", "dropbox.com", "spotify.com", "adobe.com", "salesforce.com"
]

phishing_domains = [
    "acmepay-secure-login.com", "acmepay.verify-account.net", "login-acmepay.support",
    "update-billing-amazon.info", "secure-paypal-verify.com", "apple-id-locked.co",
    "microsoft-account-reset.xyz", "netflix-billing-update.club", "github-auth-check.site",
    "google-security-alert.tech", "bankofamerica-login-verify.com", "chase-account-locked.top",
    "wellsfargo-secure-update.net", "instagram-copyright-appeal.com", "facebook-login-alert.cc",
    "whatsapp-verify-number.info", "dhl-package-tracking-fee.com", "fedex-redelivery.top",
    "usps-tracking-update.xyz", "linkedin-job-offer-secure.com"
]

with open("data/urls.csv", mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["url", "label"])
    
    # Write benign (label 0)
    for _ in range(150):
        domain = random.choice(benign_domains)
        path = random.choice(["", "/about", "/login", "/api/v1", "/docs", "/search?q=test"])
        writer.writerow([f"https://{domain}{path}", 0])
        
    # Write phishing (label 1)
    for _ in range(150):
        domain = random.choice(phishing_domains)
        path = random.choice(["/login", "/verify", "/update", "/secure", "/auth", "/id"])
        writer.writerow([f"http://{domain}{path}?id=12345", 1])

print("Generated data/urls.csv with 300 rows (150 benign, 150 phishing).")