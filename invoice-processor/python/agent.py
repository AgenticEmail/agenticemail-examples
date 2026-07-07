"""Invoice processor: extracts, matches, and routes invoices from PDF attachments.

Give an AgenticEmail inbox to Claude. When a vendor emails a PDF invoice, Claude
reads it with PDF vision, extracts the key fields, decides approved vs
needs-review, routes it to your AP team, and confirms receipt with the vendor.
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
INBOX_USERNAME = os.environ.get("INBOX_USERNAME", "invoice-processor")

AP_EMAIL = os.environ.get("AP_EMAIL", "ap@example.com")
AUTO_APPROVE_LIMIT = int(os.environ.get("AUTO_APPROVE_LIMIT", "1000"))

email = AgenticEmail(api_key=os.environ["AGENTICEMAIL_API_KEY"])
claude = Anthropic()  # reads ANTHROPIC_API_KEY

inbox = email.inboxes.create(
    username=INBOX_USERNAME,
    **({"domain": os.environ["INBOX_DOMAIN"]} if os.environ.get("INBOX_DOMAIN") else {}),
)
inbox_email = inbox["id"]
system_prompt = build_system_prompt(inbox_email, AP_EMAIL, AUTO_APPROVE_LIMIT)

EXTRACT_INSTRUCTION = (
    "Extract this invoice. Reply with ONLY a JSON object: "
    '{"vendor":..., "invoice_number":..., "amount": <number>, '
    '"currency":..., "due_date":...}. No prose.'
)


def extract_invoice(pdf_bytes: bytes) -> dict | None:
    b64 = base64.b64encode(pdf_bytes).decode()
    reply = claude.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": b64,
                        },
                    },
                    {"type": "text", "text": EXTRACT_INSTRUCTION},
                ],
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
        print("  could not parse invoice JSON, skipping.")
        return None


def process_attachment(msg: dict, attachment: dict) -> None:
    pdf_bytes = email.messages.get_attachment(inbox_email, msg["id"], attachment["id"])
    invoice = extract_invoice(pdf_bytes)
    if invoice is None:
        return

    vendor = invoice.get("vendor", "unknown vendor")
    invoice_number = invoice.get("invoice_number", "unknown")
    amount = invoice.get("amount")
    currency = invoice.get("currency", "")
    due_date = invoice.get("due_date", "unknown")

    status = "approved" if isinstance(amount, (int, float)) and amount < AUTO_APPROVE_LIMIT else "needs-review"

    summary = (
        f"Invoice {invoice_number} from {vendor}\n"
        f"Amount: {amount} {currency}\n"
        f"Due date: {due_date}\n"
        f"Status: {status}\n"
        f"Received from: {msg['from']}"
    )
    email.messages.send(
        inbox_email,
        to=[AP_EMAIL],
        subject=f"[{status}] Invoice {invoice_number} from {vendor}",
        text=summary,
    )
    email.messages.reply(
        inbox_email,
        msg["id"],
        text=f"Thanks - we received invoice {invoice_number} and it is being processed.",
    )
    print(f"  routed invoice {invoice_number} to {AP_EMAIL} ({status}).")


def main() -> None:
    print(f"Invoice processor inbox: {inbox_email}")
    # Ignore mail that was already in the inbox when we started.
    seen = {m["id"] for m in email.messages.list(inbox_email).get("data", [])}
    print("Waiting for invoices... (Ctrl+C to stop)")
    while True:
        for msg in email.messages.list(inbox_email).get("data", []):
            if msg["id"] in seen:
                continue
            seen.add(msg["id"])
            if msg["direction"] != "inbound":
                continue
            print(f"New email from {msg['from']}: {msg.get('subject') or '(no subject)'}")
            pdfs = [
                a
                for a in (msg.get("attachments") or [])
                if a.get("content_type") == "application/pdf"
            ]
            if not pdfs:
                print("  no PDF attachment, skipping.")
                continue
            for attachment in pdfs:
                process_attachment(msg, attachment)
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
