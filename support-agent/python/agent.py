"""Support agent: triages, answers, and escalates over email.

Give an AgenticEmail inbox to Claude. When a customer emails for help, Claude
classifies the request, answers what it can, and escalates the rest - all
in-thread.
"""

import os
import time

from agenticemail import AgenticEmail
from anthropic import Anthropic

from prompt import build_system_prompt

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")
POLL_SECONDS = int(os.environ.get("POLL_SECONDS", "10"))
INBOX_USERNAME = os.environ.get("INBOX_USERNAME", "support-agent")

ESCALATION_EMAIL = os.environ.get("ESCALATION_EMAIL", "support-lead@example.com")

email = AgenticEmail(api_key=os.environ["AGENTICEMAIL_API_KEY"])
claude = Anthropic()  # reads ANTHROPIC_API_KEY

inbox = email.inboxes.create(
    username=INBOX_USERNAME,
    **({"domain": os.environ["INBOX_DOMAIN"]} if os.environ.get("INBOX_DOMAIN") else {}),
)
inbox_email = inbox["id"]
system_prompt = build_system_prompt(inbox_email, ESCALATION_EMAIL)


def answer(message: str) -> str:
    reply = claude.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": message}],
    )
    return "".join(b.text for b in reply.content if b.type == "text")


def main() -> None:
    print(f"Support agent inbox: {inbox_email}")
    # Ignore mail that was already in the inbox when we started.
    seen = {m["id"] for m in email.messages.list(inbox_email).get("data", [])}
    print("Waiting for email... (Ctrl+C to stop)")
    while True:
        for msg in email.messages.list(inbox_email).get("data", []):
            if msg["id"] in seen:
                continue
            seen.add(msg["id"])
            if msg["direction"] != "inbound":
                continue
            print(f"New email from {msg['from']}: {msg.get('subject') or '(no subject)'}")
            prompt = (
                f"From: {msg['from']}\n"
                f"Subject: {msg.get('subject') or ''}\n\n"
                f"{msg.get('text') or ''}"
            )
            email.messages.reply(inbox_email, msg["id"], text=answer(prompt))
            print("  replied.")
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
