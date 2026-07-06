"""Approval Inbox: turns your inbox into an approval queue.

Give an AgenticEmail inbox to Claude. Systems email it approval requests, Claude
summarises each one, and the approver replies "approve" or "reject" in-thread.
"""

import os
import time

from agenticemail import AgenticEmail
from anthropic import Anthropic

from prompt import build_system_prompt

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")
POLL_SECONDS = int(os.environ.get("POLL_SECONDS", "10"))
INBOX_USERNAME = os.environ.get("INBOX_USERNAME", "approval-inbox")

APPROVER_NAME = os.environ.get("APPROVER_NAME", "Alex")

email = AgenticEmail(api_key=os.environ["AGENTICEMAIL_API_KEY"])
claude = Anthropic()  # reads ANTHROPIC_API_KEY

inbox = email.inboxes.create(username=INBOX_USERNAME)
inbox_email = inbox["id"]
system_prompt = build_system_prompt(inbox_email, APPROVER_NAME)


def answer(message: str) -> str:
    reply = claude.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": message}],
    )
    return reply.content[0].text


def main() -> None:
    print(f"Approval inbox: {inbox_email}")
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
