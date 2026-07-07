"""Receipt & expense parser: turns forwarded receipt photos and PDFs into clean expense rows.

Give an AgenticEmail inbox to Claude. When someone forwards or photographs a
receipt and sends it here, Claude reads the image or PDF with its vision,
extracts the merchant, date, total, tax, and payment method, categorises the
expense, flags anything unusual, routes a clean row to your expense system, and
confirms with the sender - all from an inbox it owns.
"""

import base64
import json
import os
import time

from agenticemail import AgenticEmail
from anthropic import Anthropic

from prompt import build_system_prompt

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")
POLL_SECONDS = int(os.environ.get("POLL_SECONDS", "10"))
INBOX_USERNAME = os.environ.get("INBOX_USERNAME", "receipt-parser")

EXPENSE_EMAIL = os.environ.get("EXPENSE_EMAIL", "expenses@example.com")
FLAG_LIMIT = int(os.environ.get("FLAG_LIMIT", "500"))

email = AgenticEmail(api_key=os.environ["AGENTICEMAIL_API_KEY"])
claude = Anthropic()  # reads ANTHROPIC_API_KEY

inbox = email.inboxes.create(
    username=INBOX_USERNAME,
    **({"domain": os.environ["INBOX_DOMAIN"]} if os.environ.get("INBOX_DOMAIN") else {}),
)
inbox_email = inbox["id"]
system_prompt = build_system_prompt(inbox_email, EXPENSE_EMAIL, FLAG_LIMIT)

EXTRACT_INSTRUCTION = (
    "Extract this receipt. Reply with ONLY a JSON object: "
    '{"merchant":..., "date":..., "total": <number>, "currency":..., '
    '"category":..., "tax":..., "payment_method":...}. No prose.'
)


def receipt_block(content_type: str, data_b64: str) -> dict | None:
    if content_type.startswith("image/"):
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": content_type,
                "data": data_b64,
            },
        }
    if content_type == "application/pdf":
        return {
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": "application/pdf",
                "data": data_b64,
            },
        }
    return None


def extract_receipt(content_type: str, raw_bytes: bytes) -> dict | None:
    block = receipt_block(content_type, base64.b64encode(raw_bytes).decode())
    if block is None:
        return None
    reply = claude.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": [block, {"type": "text", "text": EXTRACT_INSTRUCTION}],
            }
        ],
    )
    raw = "".join(b.text for b in reply.content if b.type == "text")
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1:
        print("  could not find JSON in Claude's reply, skipping.")
        return None
    try:
        return json.loads(raw[start : end + 1])
    except json.JSONDecodeError:
        print("  could not parse receipt JSON, skipping.")
        return None


def process_attachment(msg: dict, attachment: dict) -> None:
    raw_bytes = email.messages.get_attachment(inbox_email, msg["id"], attachment["id"])
    receipt = extract_receipt(attachment["content_type"], raw_bytes)
    if receipt is None:
        return

    merchant = receipt.get("merchant", "unknown merchant")
    date = receipt.get("date", "unknown")
    total = receipt.get("total")
    currency = receipt.get("currency", "")
    category = receipt.get("category", "other")
    tax = receipt.get("tax", "n/a")
    payment_method = receipt.get("payment_method", "unknown")

    flagged = isinstance(total, (int, float)) and total > FLAG_LIMIT
    status = "FLAG" if flagged else "ok"

    row = (
        f"Merchant: {merchant}\n"
        f"Date: {date}\n"
        f"Category: {category}\n"
        f"Total: {total} {currency}\n"
        f"Tax: {tax}\n"
        f"Payment method: {payment_method}\n"
        f"Status: {status}\n"
        f"Received from: {msg['from']}"
    )
    email.messages.send(
        inbox_email,
        to=[EXPENSE_EMAIL],
        subject=f"Expense: {merchant} {total} {currency}" + (" [FLAG]" if flagged else ""),
        text=row,
    )
    email.messages.reply(
        inbox_email,
        msg["id"],
        text=f"Recorded {merchant} for {total} {currency}.",
    )
    print(f"  routed expense for {merchant} to {EXPENSE_EMAIL} ({status}).")


def main() -> None:
    print(f"Receipt parser inbox: {inbox_email}")
    # Ignore mail that was already in the inbox when we started.
    seen = {m["id"] for m in email.messages.list(inbox_email).get("data", [])}
    print("Waiting for receipts... (Ctrl+C to stop)")
    while True:
        for msg in email.messages.list(inbox_email).get("data", []):
            if msg["id"] in seen:
                continue
            seen.add(msg["id"])
            if msg["direction"] != "inbound":
                continue
            print(f"New email from {msg['from']}: {msg.get('subject') or '(no subject)'}")
            receipts = [
                a
                for a in (msg.get("attachments") or [])
                if a.get("content_type", "").startswith("image/")
                or a.get("content_type") == "application/pdf"
            ]
            if not receipts:
                print("  no image or PDF attachment, skipping.")
                continue
            for attachment in receipts:
                process_attachment(msg, attachment)
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
