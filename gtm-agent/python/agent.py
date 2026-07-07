"""GTM agent: runs outbound over email, classifies replies, hands off warm leads.

Give an AgenticEmail inbox to Claude. It sends a first-touch cold email, then
classifies every reply and responds - warm leads get a call and a CC to you.
"""

import os
import time

from agenticemail import AgenticEmail
from anthropic import Anthropic

from prompt import build_system_prompt

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")
POLL_SECONDS = int(os.environ.get("POLL_SECONDS", "10"))
INBOX_USERNAME = os.environ.get("INBOX_USERNAME", "gtm-agent")

USER_NAME = os.environ.get("USER_NAME", "Sam")
PROSPECT_EMAIL = os.environ.get("PROSPECT_EMAIL", "prospect@example.com")

email = AgenticEmail(api_key=os.environ["AGENTICEMAIL_API_KEY"])
claude = Anthropic()  # reads ANTHROPIC_API_KEY

inbox = email.inboxes.create(
    username=INBOX_USERNAME,
    **({"domain": os.environ["INBOX_DOMAIN"]} if os.environ.get("INBOX_DOMAIN") else {}),
)
inbox_email = inbox["id"]
system_prompt = build_system_prompt(inbox_email, USER_NAME)


def answer(message: str) -> str:
    reply = claude.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": message}],
    )
    return "".join(b.text for b in reply.content if b.type == "text")


def main() -> None:
    print(f"GTM agent inbox: {inbox_email}")
    # Send the first-touch cold email before we start listening for replies.
    opener = answer(
        f"Write a first-touch cold email to the prospect at {PROSPECT_EMAIL}. "
        "They are a growth lead at an early-stage SaaS company."
    )
    email.messages.send(inbox_email, to=[PROSPECT_EMAIL], subject="Quick question", text=opener)
    print(f"Sent opener to {PROSPECT_EMAIL}.")
    # Ignore mail that was already in the inbox when we started.
    seen = {m["id"] for m in email.messages.list(inbox_email).get("data", [])}
    print("Waiting for replies... (Ctrl+C to stop)")
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
