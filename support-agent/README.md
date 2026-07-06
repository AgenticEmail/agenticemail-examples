# Support agent

Email this agent for help. It triages the request, answers what it can from the
knowledge base, escalates bugs and billing issues with a summary, and follows up
until the thread is closed - all from an inbox it owns.

## Run

**Python** (3.10+)

```bash
cd python
pip install -r requirements.txt
export AGENTICEMAIL_API_KEY="am_..."
export ANTHROPIC_API_KEY="sk-ant-..."
python agent.py
```

**TypeScript** (Node 18+)

```bash
cd typescript
npm install
export AGENTICEMAIL_API_KEY="am_..."
export ANTHROPIC_API_KEY="sk-ant-..."
npm start
```

On startup the agent prints its inbox address. Email that address and watch it
reply. It only responds to mail that arrives after it starts.

## Configure

Set these as environment variables (see `.env.example`):

| Variable | Default | What it does |
| --- | --- | --- |
| `ESCALATION_EMAIL` | `support-lead@example.com` | Where bugs and billing issues get escalated. |
| `INBOX_USERNAME` | `support-agent` | Local part of the inbox address. |
| `ANTHROPIC_MODEL` | `claude-sonnet-5` | Claude model to use. |
| `POLL_SECONDS` | `10` | How often to check for new mail. |

The triage rules and tone live in the system prompt inside `agent.py` /
`agent.ts` - edit them to match your product and knowledge base.
