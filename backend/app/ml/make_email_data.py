"""Build a SYNTHETIC email dataset (phishing = 1, legitimate = 0).

Synthetic data is only a starting point: it is easier than real email.
Always report real numbers from data/test_demo.csv or a real dataset.
"""
import csv
import pathlib
import random

rng = random.Random(42)

BRANDS = ["AcmePay", "AcmeBank", "NovaMail", "CloudBox", "ShopKart", "StreamNest", "TravelEase", "CampusConnect"]
NAMES = ["Priya", "Rahul", "Ananya", "Karthik", "Meera", "Arjun", "Sneha", "Vikram"]
SEND = ["Security Team", "Customer Support", "Accounts Team", "Billing Department", "Help Desk"]
TLDS = ["com", "net", "info", "online", "co", "xyz"]
WORDS = ["secure", "login", "verify", "account", "update", "support", "billing", "alert", "help"]


def fake_link(brand: str) -> str:
    b = brand.lower()
    host = rng.choice([
        f"{b}-{rng.choice(WORDS)}.{rng.choice(TLDS)}",
        f"{rng.choice(WORDS)}-{b}.{rng.choice(TLDS)}",
        f"{b}{rng.choice(WORDS)}.{rng.choice(TLDS)}",
        f"{b.replace('m', 'rn', 1)}.{rng.choice(TLDS)}",
        f"{rng.choice(WORDS)}.{b}.{rng.choice(WORDS)}-{rng.randint(10, 99)}.{rng.choice(TLDS)}",
    ])
    return f"http://{host}/{rng.choice(WORDS)}?id={rng.randint(1000, 99999)}"


def real_link(brand: str) -> str:
    return f"https://www.{brand.lower()}.com/{rng.choice(['help', 'account', 'orders', 'blog', 'support'])}"


def typo(text: str, rate: float) -> str:
    out = []
    for ch in text:
        if ch.isalpha() and rng.random() < rate:
            out.append(rng.choice(["", ch + ch, ch.upper() if ch.islower() else ch.lower()]))
        else:
            out.append(ch)
    return "".join(out)


# ---------------- phishing ----------------
P_TOPICS = {
    "suspension": (
        ["Your {b} account will be suspended", "Account limited: action needed", "Your {b} account has been locked"],
        ["We detected unusual activity on your account.", "Your account has been flagged for a policy violation.",
         "Several failed sign-in attempts were recorded."]),
    "password": (
        ["Your {b} password expires today", "Password expiry notice", "Update your password now"],
        ["Your password will expire in 24 hours.", "For your safety you must renew your password.",
         "Your current password is no longer secure."]),
    "payment": (
        ["Payment failed for your {b} order", "Invoice #{num} is overdue", "We could not process your payment"],
        ["Your last payment was declined.", "An outstanding balance remains on your account.",
         "Your card on file could not be charged."]),
    "parcel": (
        ["Delivery attempt failed", "Your parcel is on hold", "Pay a small fee to release your package"],
        ["We could not deliver your parcel today.", "Your package is held at our depot.",
         "A customs fee is required before delivery."]),
    "prize": (
        ["Congratulations, you have been selected", "Claim your reward now", "You won a gift card"],
        ["You are our lucky winner this month.", "Your loyalty reward is waiting for you.",
         "You have been selected for an exclusive cash prize."]),
    "kyc": (
        ["Complete your KYC today", "KYC verification pending", "Your {b} wallet will be blocked"],
        ["Your KYC documents are incomplete.", "RBI rules require immediate verification of your profile.",
         "Your wallet will be frozen without verification."]),
    "refund": (
        ["Tax refund available", "You are eligible for a refund", "Refund of Rs {num} pending"],
        ["A refund is waiting to be credited to your account.", "We found an overpayment on your file.",
         "Confirm your bank details to receive your refund."]),
    "document": (
        ["Shared document: {num}.pdf", "Salary revision letter attached", "Payroll update for this month"],
        ["A confidential document was shared with you.", "HR has uploaded your revised salary details.",
         "Please review the attached payroll file."]),
}
P_THREAT = ["Failure to act will result in permanent closure.", "This is your final warning.",
            "Your access will be removed within 24 hours.", "Delay may lead to loss of funds.",
            "You have only 12 hours left."]
P_CTA = ["Verify your identity here:", "Log in to confirm your details:", "Click the link below to restore access:",
         "Confirm your password and card number at:", "Update your information immediately:", "Sign in now to avoid closure:"]
P_GREET = ["Dear customer,", "Dear user,", "Attention,", "Hello {name},", "Dear account holder,", ""]
P_CLOSE = ["Thank you for your cooperation.", "{s}", "Regards, {s}", "Do not ignore this message.", ""]

# ---------------- legitimate ----------------
L_TOPICS = {
    "newsletter": (
        ["{b} monthly newsletter", "What is new at {b}", "Product update from {b}"],
        ["Here is a roundup of this month's features and tips.", "We have shipped three new features since last month.",
         "Read our latest blog post about getting more from your plan."], True),
    "order": (
        ["Your {b} order has shipped", "Order confirmation #{num}", "Thanks for your purchase"],
        ["Your order is on its way and should arrive in 3 to 5 days.", "We have received your order and will update you when it ships.",
         "Your receipt is attached for your records."], True),
    "meeting": (
        ["Meeting tomorrow at 10 AM", "Project review on Friday", "Agenda for the team sync"],
        ["Please find the agenda for our meeting below.", "The project review has moved to conference room B.",
         "Could you share your slides before the sync?"], False),
    "college": (
        ["Timetable update for next week", "Library notice", "Exam schedule published"],
        ["The class timetable has changed for Monday and Tuesday.", "Library books are due for return by the end of this week.",
         "The internal exam schedule has been uploaded to the notice board."], False),
    "otp": (
        ["Your one-time password", "{b} login code", "Verification code"],
        ["Your one-time password is {num}. It is valid for 10 minutes. Never share this code with anyone.",
         "Use code {num} to finish signing in. If you did not request it, ignore this email.",
         "Your verification code is {num}. {b} staff will never ask you for this code."], False),
    "reset": (
        ["Password reset requested", "Reset your {b} password", "Password change confirmation"],
        ["You asked to reset your password. If this was you, use the button below. If not, you can safely ignore this email.",
         "Your password was changed successfully. If you did not make this change, contact support through our official app.",
         "We received a request to reset your password. This link works for one hour."], True),
    "statement": (
        ["Your monthly statement is ready", "Statement for October", "Your invoice from {b}"],
        ["Your statement is now available in your online account.", "Your invoice for this month is attached.",
         "Thank you for being a customer. Your next payment is due on the 5th."], True),
    "renewal": (
        ["Your subscription renews soon", "Plan renewal reminder", "Your {b} plan"],
        ["Your plan renews automatically next week. No action is needed.", "You can manage or cancel your plan any time in settings.",
         "We will charge your saved payment method on the renewal date."], True),
    "hard": (  # legitimate but sounds urgent: the tricky cases
        ["Action required: confirm your email address", "Important: security notice", "Urgent: class cancelled today"],
        ["Please confirm your email address to finish creating your account.", "We noticed a sign-in from a new device. If this was you, no action is needed.",
         "Today's lecture is cancelled because the professor is unwell."], True),
}
L_GREET = ["Hi {name},", "Hello {name},", "Dear {name},", "Hi team,", ""]
L_CLOSE = ["Thanks,", "Best regards, {s}", "Regards, {s}", "Cheers, {name}", "Have a great day.", ""]


def fill(text: str, brand: str, name: str, sender: str) -> str:
    return (text.replace("{b}", brand)
                .replace("{name}", name)
                .replace("{num}", str(rng.randint(100000, 999999)))
                .replace("{s}", sender))


def make_phish() -> tuple[str, str]:
    topic = rng.choice(list(P_TOPICS))
    subjects, bodies = P_TOPICS[topic]
    brand, name, sender = rng.choice(BRANDS), rng.choice(NAMES), rng.choice(SEND)
    subject = fill(rng.choice(subjects), brand, name, sender)
    parts = [fill(rng.choice(P_GREET), brand, name, sender), fill(rng.choice(bodies), brand, name, sender)]
    if rng.random() < 0.8:
        parts.append(rng.choice(P_THREAT))
    parts.append(rng.choice(P_CTA) + " " + fake_link(brand))
    parts.append(fill(rng.choice(P_CLOSE), brand, name, sender))
    body = " ".join(p for p in parts if p)
    text = f"{subject}. {body}"
    if rng.random() < 0.25:
        text = text.upper() if rng.random() < 0.3 else text
    return typo(text, 0.01 if rng.random() < 0.35 else 0.0), topic


def make_legit() -> tuple[str, str]:
    topic = rng.choice(list(L_TOPICS))
    subjects, bodies, may_link = L_TOPICS[topic]
    brand, name, sender = rng.choice(BRANDS), rng.choice(NAMES), rng.choice(SEND)
    subject = fill(rng.choice(subjects), brand, name, sender)
    parts = [fill(rng.choice(L_GREET), brand, name, sender), fill(rng.choice(bodies), brand, name, sender)]
    if may_link and rng.random() < 0.7:
        parts.append(rng.choice(["Details:", "Read more:", "View it here:", "Manage your account:"]) + " " + real_link(brand))
    parts.append(fill(rng.choice(L_CLOSE), brand, name, sender))
    body = " ".join(p for p in parts if p)
    return typo(f"{subject}. {body}", 0.01 if rng.random() < 0.1 else 0.0), topic


def main(n_each: int = 2200, out: str = "data/emails.csv") -> None:
    rows, seen = [], set()
    for label, maker in ((1, make_phish), (0, make_legit)):
        made = 0
        while made < n_each:
            text, topic = maker()
            key = text.lower()
            if key in seen:
                continue
            seen.add(key)
            rows.append({"text": text, "label": label, "kind": topic, "source": "synthetic"})
            made += 1
    rng.shuffle(rows)
    path = pathlib.Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["text", "label", "kind", "source"])
        w.writeheader()
        w.writerows(rows)
    print("wrote", len(rows), "rows to", path)
    print("phishing:", sum(r["label"] for r in rows), "| legitimate:", sum(1 - r["label"] for r in rows))


if __name__ == "__main__":
    main()