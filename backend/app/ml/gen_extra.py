import random
import pandas as pd

random.seed(7)
BRANDS = ["SwiftWallet", "GreenLeaf Bank", "CloudBox", "ShopKart", "Zentra", "StreamNest", "CampusConnect"]
NAMES = ["Priya", "Rahul", "Karthik", "Anita", "Arjun", "Meena", "Suresh", "Divya", "Kiran", "Neha"]
BOSSES = ["Mr. Sharma", "Ms. Iyer", "Dr. Rao", "your manager", "the director", "your HOD"]
CITIES = ["Mumbai", "Lagos", "Moscow", "Hanoi", "Delhi", "Dubai", "Kyiv"]
DEVICES = ["laptop", "phone", "tablet", "browser"]
MONTHS = ["October", "November", "December", "January"]
WHEN = ["tomorrow", "tonight", "within 24 hours", "by 5 PM today", "in 2 hours"]


def slug(b): return b.lower().replace(" ", "")


def fill(t):
    b = random.choice(BRANDS)
    return t.format(
        brand=b, name=random.choice(NAMES), boss=random.choice(BOSSES), city=random.choice(CITIES),
        device=random.choice(DEVICES), month=random.choice(MONTHS), when=random.choice(WHEN),
        amt=f"{random.choice([500, 750, 1250, 2000, 4999, 9800, 18240]):,}",
        fee=random.choice([199, 299, 499, 999]), n=random.choice([2, 3, 5, 10]),
        num=random.randint(10000, 99999), hrs=random.choice([2, 3, 4]),
        bad=random.choice([f"http://{slug(b)}-secure-login.com/verify", "https://bit.ly/3xK9aQ",
                           f"http://update-{slug(b)}.in/account", f"www.{slug(b)}-support.net/help"]),
        good=f"https://www.{slug(b)}.com/help",
    )


GREET = ["", "", "Dear {name}, ", "Hello, ", "Hi {name}, ", "Dear customer, "]
CLOSE = ["", "", " Regards, {name}", " Thanks.", " Please do not reply to this email.", " Team {brand}"]

PHISH = {
    "boss_vouchers": [
        "I need a quick favour and it has to stay confidential. Buy {n} {brand} vouchers of Rs {amt} each and message me the codes, I will refund you this evening.",
        "This is {boss}. I am travelling and cannot take calls. Please arrange {n} gift vouchers worth Rs {amt} and send the codes here, it is urgent.",
        "Are you at your desk? I am in a meeting and need you to purchase {n} {brand} cards for a client. Send me the numbers once done.",
    ],
    "job_scam": [
        "We found your profile online. Work from home {hrs} hours a day and earn Rs {amt} per week. Pay a refundable registration fee of Rs {fee} to begin: {bad}",
        "Part time online job, no experience needed. Earn Rs {amt} daily by simple tasks. Deposit Rs {fee} to activate your account and message us on WhatsApp.",
        "Congratulations, you are shortlisted for a data entry role at {brand}. To confirm your seat, pay the training kit fee of Rs {fee} {when}.",
    ],
    "hr_attachment": [
        "The revised salary structure for {month} is attached. Open the document and sign in with your email password to view it.",
        "Your appraisal letter is ready. Download the secure document here {bad} and enter your login details to access it.",
        "HR update: payroll details have changed. You must review the attached form {when} using your company credentials.",
    ],
    "invoice_threat": [
        "Final demand: invoice #{num} of Rs {amt} is overdue. Legal proceedings will start {when} unless you pay. Open the invoice here: {bad}",
        "Payment overdue notice from {brand} collections. Pay Rs {amt} {when} to avoid penalty and police complaint. Details: {bad}",
        "Your account is in default. Download the attached statement and settle Rs {amt} immediately or your case will be sent to court.",
    ],
    "new_device": [
        "Your {brand} account was accessed from a {device} in {city}. If this was not you, log in now to secure it: {bad}",
        "Suspicious activity detected on your {brand} account. Confirm your identity {when} or the account will be limited. {bad}",
        "We blocked a sign-in from {city}. Verify your details at {bad} or your {brand} access will be suspended.",
    ],
}
LEGIT = {
    "boss_normal": [
        "Can you share the slides for the {month} review before the meeting? Thanks.",
        "I am travelling {when} so please send the report to the team instead. We can talk on Monday.",
        "Please join the 3 PM call with the client. Agenda is in the calendar invite.",
    ],
    "recruiter": [
        "Thank you for applying to {brand}. Your interview is scheduled for Monday at 11 AM. Please carry your ID card and reply to confirm.",
        "We have received your application. Our team will contact you within a week. There is no fee at any stage of our hiring process.",
    ],
    "hr_real": [
        "The holiday calendar for next year is attached for your reference. No action is needed.",
        "Reminder: please submit your timesheet by Friday through the HR portal. Contact your manager for any help.",
        "The health insurance policy has been renewed. You can read the details on the intranet: {good}",
    ],
    "invoice_real": [
        "Reminder: invoice #{num} of Rs {amt} is due next week. You can pay from the {brand} app. Ignore this if you have already paid.",
        "Thank you for your payment of Rs {amt}. Your receipt is attached for your records.",
        "Your {month} statement is ready. View it any time at {good}",
    ],
    "signin_real": [
        "We noticed a sign-in to your {brand} account from a new {device}. If this was you, no action is needed. If not, change your password from the app settings.",
        "Your password was changed successfully. If you did not make this change, contact support through the official app.",
        "New login on your {brand} account from {city}. This is just a notification, nothing is required from you.",
    ],
}


def make(cats, label, per_template):
    rows = []
    for cat, temps in cats.items():
        for t in temps:
            for _ in range(per_template):
                text = fill(random.choice(GREET) + t + random.choice(CLOSE))
                rows.append({"text": text, "label": label, "category": cat})
    return rows


rows = make(PHISH, 1, 60) + make(LEGIT, 0, 90)
df = pd.DataFrame(rows).drop_duplicates("text").sample(frac=1, random_state=7)
df[["text", "label"]].to_csv("data/extra_emails.csv", index=False)
print(df.groupby(["label", "category"]).size())
print("\nTotal:", len(df), "| phishing:", int(df.label.sum()))
for _, r in df.sample(4, random_state=1).iterrows():
    print(f"\n[{r.label}] {r.text}")