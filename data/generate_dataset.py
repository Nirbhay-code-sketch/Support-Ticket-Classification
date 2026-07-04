"""
generate_dataset.py
--------------------
Generates a synthetic but realistic customer-support ticket dataset for
training the classifier. Replace this with your real ticket export
(CSV with columns: text, category, priority) when available.

Categories : Billing, Technical, Account, Product, General
Priority   : High, Medium, Low
"""

import csv
import random
from pathlib import Path

random.seed(42)

CATEGORY_TEMPLATES = {
    "Billing": [
        "I was charged twice for my subscription this month",
        "My invoice shows an incorrect amount, please fix it",
        "I want a refund for the last payment",
        "The billing cycle date changed without notice",
        "Can you explain the extra charge on my card",
        "My coupon code did not apply at checkout",
        "I need a copy of my last 3 invoices",
        "Payment failed but money was deducted from my account",
    ],
    "Technical": [
        "The app crashes every time I try to upload a file",
        "I am getting a 500 error when logging in",
        "The dashboard is not loading any data",
        "Server keeps timing out during checkout",
        "The mobile app freezes on the home screen",
        "API returns null instead of the expected response",
        "The website is down for everyone in my team",
        "Getting error code E1023 on export",
    ],
    "Account": [
        "I forgot my password and the reset link is not working",
        "I cannot log into my account anymore",
        "Please help me change my registered email address",
        "My account got suspended without explanation",
        "I want to delete my account permanently",
        "Two-factor authentication is not sending codes",
        "I need to transfer ownership of my account",
        "My profile information keeps reverting to old data",
    ],
    "Product": [
        "Does this plan support exporting to Excel",
        "I would like to request a dark mode feature",
        "How do I integrate this with Slack",
        "Is there a way to bulk import contacts",
        "Can the product support multiple languages",
        "I need a feature to schedule recurring reports",
        "What is the difference between the pro and team plans",
        "Suggestion: add keyboard shortcuts for navigation",
    ],
    "General": [
        "What are your customer support working hours",
        "Just wanted to say the new update looks great",
        "How can I contact your sales team",
        "Where can I find your terms of service",
        "Do you have an affiliate program",
        "I would like to give feedback about my experience",
        "Can you point me to the onboarding guide",
        "Thank you for the quick help last time",
    ],
}

URGENT_MODIFIERS = [
    "This is urgent, ", "ASAP - ", "Critical issue: ", "Emergency: ",
    "This is blocking my entire team, ", "We are losing money because of this, ",
]

MEDIUM_MODIFIERS = [
    "Please help soon, ", "This needs attention, ", "Fairly important: ",
]

LOW_MODIFIERS = [
    "No rush, but ", "Whenever you have time, ", "Just a small note: ",
    "Low priority - ",
]


def build_row(category: str, base: str) -> dict:
    roll = random.random()
    if roll < 0.30:
        text = random.choice(URGENT_MODIFIERS) + base.lower()
        priority = "High"
    elif roll < 0.70:
        text = base if random.random() < 0.5 else random.choice(MEDIUM_MODIFIERS) + base.lower()
        priority = "Medium"
    else:
        text = random.choice(LOW_MODIFIERS) + base.lower()
        priority = "Low"

    # Technical + Billing skew slightly more urgent (realistic pattern)
    if category in ("Technical", "Billing") and random.random() < 0.25:
        priority = "High"

    return {"text": text, "category": category, "priority": priority}


def main(n_per_category: int = 60, out_path: str = "tickets.csv"):
    rows = []
    for category, templates in CATEGORY_TEMPLATES.items():
        for _ in range(n_per_category):
            base = random.choice(templates)
            rows.append(build_row(category, base))
    random.shuffle(rows)

    out_file = Path(__file__).parent / out_path
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "category", "priority"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} tickets -> {out_file}")


if __name__ == "__main__":
    main()
