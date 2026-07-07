# AgenticEmail examples

Working AI email agents you can clone and run in minutes. Each one gives an
agent its own [AgenticEmail](https://agenticemail.dev) inbox - it sends,
receives, and runs full email threads on its own.

Every example ships in **Python** and **TypeScript**, mirrors a template at
[agenticemail.dev/build](https://agenticemail.dev/build), and is self-contained:
clone the folder, set two environment variables, and run.

## Examples

**Productivity**

| Example | What it does |
| --- | --- |
| [scheduling-agent](./scheduling-agent) | Email it to book time - it knows your rules and offers slots. |
| [inbox-zero-agent](./inbox-zero-agent) | Drafts replies while you sleep - you review and send. |

**Sales & outbound**

| Example | What it does |
| --- | --- |
| [gtm-agent](./gtm-agent) | Personalised outreach, reply classification, warm handoff. |

**Support**

| Example | What it does |
| --- | --- |
| [support-agent](./support-agent) | Triage, respond, escalate, follow up, close. |

**Recruiting**

| Example | What it does |
| --- | --- |
| [ai-recruiter](./ai-recruiter) | Screen inbound applicants, coordinate interviews, keep candidates warm. |

**Finance**

| Example | What it does |
| --- | --- |
| [invoice-processor](./invoice-processor) | Claude reads PDF invoices, matches, and routes them by amount. |
| [receipt-parser](./receipt-parser) | Claude vision reads receipt photos and PDFs into clean expense rows. |

**Verification**

| Example | What it does |
| --- | --- |
| [signup-verification-agent](./signup-verification-agent) | Give a browser agent an inbox to catch signup links and 2FA codes. |

**Personal**

| Example | What it does |
| --- | --- |
| [newsletter-digest](./newsletter-digest) | A daily digest of everything that hit your inbox. |

## Quickstart

1. Get an AgenticEmail API key at [app.agenticemail.dev/keys](https://app.agenticemail.dev/keys) (free tier, no credit card).
2. Get an Anthropic API key at [console.anthropic.com](https://console.anthropic.com).
3. Pick an example and a language:

   **Python** (3.10+)
   ```bash
   cd scheduling-agent/python
   pip install -r requirements.txt
   export AGENTICEMAIL_API_KEY="am_..."
   export ANTHROPIC_API_KEY="sk-ant-..."
   python agent.py
   ```

   **TypeScript** (Node 18+)
   ```bash
   cd scheduling-agent/typescript
   npm install
   export AGENTICEMAIL_API_KEY="am_..."
   export ANTHROPIC_API_KEY="sk-ant-..."
   npm start
   ```

4. Email the address the agent prints on startup, and watch it work.

Each example's own README lists the config (timezone, escalation address,
approval limits, and so on) you can tune.

## How they work

Every agent uses two SDKs:

- [`agenticemail`](https://github.com/AgenticEmail/agenticemail-python) ([npm](https://github.com/AgenticEmail/agenticemail-typescript)) - the inbox: create it, poll for new mail, send and reply.
- [`anthropic`](https://docs.anthropic.com) - Claude reads each message under the agent's system prompt and writes the response.

The loop is the same shape across examples: create an inbox, list new inbound
messages, hand each one to Claude with the system prompt, and send back what
Claude writes. The prompt lives in its own module (`prompt.py` / `src/prompt.ts`)
so it is easy to edit.

## Prefer to skip the code?

Connect AgenticEmail to Claude Code, Cursor, Windsurf, or Cline over MCP and
your existing agent gets an inbox with zero glue code - see
[agenticemail.dev/build](https://agenticemail.dev/build).

## Verify it works

Every example uses the same inbox path (create, send, receive, reply). One
smoke test exercises it end-to-end against the live API, plus the Claude
text-block extraction the agents rely on:

```bash
pip install agenticemail anthropic
export AGENTICEMAIL_API_KEY="am_..."
export ANTHROPIC_API_KEY="sk-ant-..."   # optional
export INBOX_DOMAIN="yourdomain.com"    # optional, if your org has >1 domain
python scripts/smoke_test.py
```

It reuses a single inbox (fixed `client_id`) so it never accumulates inboxes.
CI ([.github/workflows/smoke.yml](./.github/workflows/smoke.yml)) runs it on
every push and weekly - add `AGENTICEMAIL_API_KEY` (and optionally
`ANTHROPIC_API_KEY`, `INBOX_DOMAIN`) as repo secrets to enable it.

> Multiple verified domains on your org? Set `INBOX_DOMAIN` - `create()` needs a
> domain when there is no default.

## Learn more

- Docs: [agenticemail.dev/docs](https://agenticemail.dev/docs)
- API reference: [api.agenticemail.dev/docs](https://api.agenticemail.dev/docs)

## License

Apache-2.0
