"""End-to-end smoke test for the AgenticEmail examples.

Exercises the exact SDK path every example relies on - create an inbox, send,
receive the round-trip, reply - plus the Claude text-block extraction that the
examples use. Run it before publishing a change; wire it into CI (see
.github/workflows/smoke.yml) so every push is verified.

Reuses one inbox via a fixed client_id, so it does not accumulate inboxes or
hit a plan limit. Skips gracefully if the API keys are not set.

    pip install agenticemail anthropic
    export AGENTICEMAIL_API_KEY=am_...
    export ANTHROPIC_API_KEY=sk-ant-...   # optional
    export INBOX_DOMAIN=yourdomain.com    # optional, if your org has >1 domain
    python scripts/smoke_test.py
"""

import os
import random
import sys
import time

from agenticemail import AgenticEmail

KEY = os.environ.get("AGENTICEMAIL_API_KEY")
if not KEY:
    print("SKIP: AGENTICEMAIL_API_KEY not set")
    sys.exit(0)

email = AgenticEmail(api_key=KEY)

create_kwargs = {
    "username": os.environ.get("SMOKE_INBOX_USERNAME", "smoke-test"),
    "client_id": "smoke-test-inbox",
}
if os.environ.get("INBOX_DOMAIN"):
    create_kwargs["domain"] = os.environ["INBOX_DOMAIN"]

inbox = email.inboxes.create(**create_kwargs)
inbox_email = inbox["id"]
print("inbox:", inbox_email)

token = f"smoke-{random.randint(100000, 999999)}"
email.messages.send(
    inbox_email, to=[inbox_email], subject=f"Smoke {token}", text=f"round-trip {token}"
)
print("sent round-trip:", token)

inbound = None
for _ in range(30):
    for m in email.messages.list(inbox_email).get("data", []):
        if m["direction"] == "inbound" and token in (m.get("subject") or ""):
            inbound = m
            break
    if inbound:
        break
    time.sleep(5)

assert inbound, "FAIL: round-trip inbound not received within 150s"
assert inbound.get("text"), "FAIL: inbound message has no text body"
print("inbound received:", inbound["id"])

reply = email.messages.reply(inbox_email, inbound["id"], text="ack")
assert reply.get("direction") == "outbound", "FAIL: reply was not created"
print("reply ok:", reply["id"])

anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
if anthropic_key:
    from anthropic import Anthropic

    claude = Anthropic()
    resp = claude.messages.create(
        model=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5"),
        max_tokens=1024,
        system="Reply with the single word OK.",
        messages=[{"role": "user", "content": "say ok"}],
    )
    text = "".join(b.text for b in resp.content if b.type == "text")
    assert text.strip(), "FAIL: no text block in Claude response (content-block bug)"
    print("claude extraction ok:", text.strip()[:40])
else:
    print("SKIP: ANTHROPIC_API_KEY not set, skipping the Claude extraction check")

print("PASS: smoke test green")
