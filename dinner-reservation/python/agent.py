"""Dinner reservation agent: emails a restaurant and books your table over email.

Give an AgenticEmail inbox to Claude. It sends the opening reservation request,
then handles every reply - accepting an in-window time, confirming the booking,
and reporting back to you - all in-thread.
"""

import os
import time

from agenticemail import AgenticEmail
from anthropic import Anthropic

from prompt import build_system_prompt

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")
POLL_SECONDS = int(os.environ.get("POLL_SECONDS", "10"))
INBOX_USERNAME = os.environ.get("INBOX_USERNAME", "dinner-reservation")

USER_NAME = os.environ.get("USER_NAME", "Sam")
PARTY_SIZE = os.environ.get("PARTY_SIZE", "2")
DATE_WINDOW = os.environ.get("DATE_WINDOW", "Friday 7-8pm")
AREA = os.environ.get("AREA", "downtown")
PREFERENCES = os.environ.get("PREFERENCES", "Italian, quiet")
RESTAURANT_EMAIL = os.environ.get("RESTAURANT_EMAIL", "restaurant@example.com")

email = AgenticEmail(api_key=os.environ["AGENTICEMAIL_API_KEY"])
claude = Anthropic()  # reads ANTHROPIC_API_KEY

inbox = email.inboxes.create(
    username=INBOX_USERNAME,
    **({"domain": os.environ["INBOX_DOMAIN"]} if os.environ.get("INBOX_DOMAIN") else {}),
)
inbox_email = inbox["id"]
system_prompt = build_system_prompt(
    inbox_email, USER_NAME, PARTY_SIZE, DATE_WINDOW, AREA, PREFERENCES
)


def answer(message: str) -> str:
    reply = claude.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": message}],
    )
    return "".join(b.text for b in reply.content if b.type == "text")


def main() -> None:
    print(f"Dinner reservation agent inbox: {inbox_email}")
    # Send the opening reservation request before we start listening for replies.
    opener = answer("Write the opening reservation request email to the restaurant.")
    email.messages.send(
        inbox_email, to=[RESTAURANT_EMAIL], subject="Table request", text=opener
    )
    print(f"Sent request to {RESTAURANT_EMAIL}.")
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
