"""Signup and verification agent: catches confirmation links and 2FA codes.

Give an AgenticEmail inbox to a browser-automation agent. When a service
emails a verification code or magic link to the inbox, Claude extracts it as
structured JSON your automation can act on.
"""

import json
import os
import time

from agenticemail import AgenticEmail
from anthropic import Anthropic

from prompt import build_system_prompt

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")
POLL_SECONDS = int(os.environ.get("POLL_SECONDS", "5"))
INBOX_USERNAME = os.environ.get("INBOX_USERNAME", "verification-agent")

FORWARD_TO = os.environ.get("FORWARD_TO", "")

email = AgenticEmail(api_key=os.environ["AGENTICEMAIL_API_KEY"])
claude = Anthropic()  # reads ANTHROPIC_API_KEY

inbox = email.inboxes.create(
    username=INBOX_USERNAME,
    **({"domain": os.environ["INBOX_DOMAIN"]} if os.environ.get("INBOX_DOMAIN") else {}),
)
inbox_email = inbox["id"]
system_prompt = build_system_prompt(inbox_email)


def extract(message: str) -> dict | None:
    resp = claude.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": message}],
    )
    raw = "".join(b.text for b in resp.content if b.type == "text")
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        return json.loads(raw[start : end + 1])
    except json.JSONDecodeError:
        return None


def main() -> None:
    print(f"Verification agent inbox: {inbox_email}")
    print("Sign up for a service with this address, then watch the code appear.")
    seen = {m["id"] for m in email.messages.list(inbox_email).get("data", [])}
    while True:
        for msg in email.messages.list(inbox_email).get("data", []):
            if msg["id"] in seen:
                continue
            seen.add(msg["id"])
            if msg["direction"] != "inbound":
                continue
            body = (
                f"From: {msg['from']}\n"
                f"Subject: {msg.get('subject') or ''}\n\n"
                f"{msg.get('text') or ''}"
            )
            result = extract(body)
            if not result or not (result.get("code") or result.get("link")):
                print(f"  {msg['from']}: no verification code or link found")
                continue
            print(
                f"  service={result.get('service')} "
                f"code={result.get('code')} link={result.get('link')}"
            )
            if FORWARD_TO:
                email.messages.send(
                    inbox_email,
                    to=[FORWARD_TO],
                    subject=f"Verification from {result.get('service')}",
                    text=json.dumps(result, indent=2),
                )
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
