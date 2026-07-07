"""Newsletter digest: one daily summary of everything that hit your inbox.

Point an AgenticEmail inbox at your newsletters and updates. Once a day this
reads every message that arrived, groups it by theme, and emails you a single
scannable digest - no dashboard, just your morning read.
"""

import datetime
import os

from agenticemail import AgenticEmail
from anthropic import Anthropic

from prompt import build_system_prompt

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")
INBOX_USERNAME = os.environ.get("INBOX_USERNAME", "newsletter-digest")

USER_EMAIL = os.environ.get("USER_EMAIL", "you@example.com")

email = AgenticEmail(api_key=os.environ["AGENTICEMAIL_API_KEY"])
claude = Anthropic()  # reads ANTHROPIC_API_KEY

inbox = email.inboxes.create(
    username=INBOX_USERNAME,
    **({"domain": os.environ["INBOX_DOMAIN"]} if os.environ.get("INBOX_DOMAIN") else {}),
)
inbox_email = inbox["id"]
system_prompt = build_system_prompt(inbox_email, USER_EMAIL)


def main() -> None:
    print(f"Newsletter digest inbox: {inbox_email}")
    messages = email.messages.list(inbox_email).get("data", [])
    inbound = [m for m in messages if m["direction"] == "inbound"]
    if not inbound:
        print("Nothing to digest yet - subscribe this inbox to a few newsletters and run again.")
        return

    items = ""
    for msg in inbound:
        text = (msg.get("text") or "")[:1500]
        items += (
            f"From: {msg['from']}\n"
            f"Subject: {msg.get('subject') or ''}\n"
            f"{text}\n\n---\n\n"
        )

    today = datetime.date.today().isoformat()
    reply = claude.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": items}],
    )
    digest = "".join(b.text for b in reply.content if b.type == "text")

    email.messages.send(
        inbox_email,
        to=[USER_EMAIL],
        subject=f"Your daily digest - {today}",
        text=digest,
    )
    print(f"Digest sent to {USER_EMAIL}.")


if __name__ == "__main__":
    main()
