"""Inbox Zero Agent: drafts replies while you sleep - you review and send.

Give an AgenticEmail inbox to Claude. For every new email, Claude writes a
reply in your voice and saves it as a draft. Nothing is ever sent
automatically - you review each draft and send it yourself.
"""

import os
import time

from agenticemail import AgenticEmail
from anthropic import Anthropic

from prompt import build_system_prompt

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")
POLL_SECONDS = int(os.environ.get("POLL_SECONDS", "10"))
INBOX_USERNAME = os.environ.get("INBOX_USERNAME", "inbox-zero-agent")

USER_NAME = os.environ.get("USER_NAME", "Alex")

email = AgenticEmail(api_key=os.environ["AGENTICEMAIL_API_KEY"])
claude = Anthropic()  # reads ANTHROPIC_API_KEY

inbox = email.inboxes.create(username=INBOX_USERNAME)
inbox_email = inbox["id"]
system_prompt = build_system_prompt(inbox_email, USER_NAME)


def draft_reply(message: str) -> str:
    reply = claude.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": message}],
    )
    return "".join(b.text for b in reply.content if b.type == "text")


def main() -> None:
    print(f"Inbox Zero Agent inbox: {inbox_email}")
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
            email.drafts.create(
                inbox_email,
                to=[msg["from"]],
                subject=f"Re: {msg.get('subject') or ''}",
                text=draft_reply(prompt),
            )
            print("  drafted (not sent).")
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
