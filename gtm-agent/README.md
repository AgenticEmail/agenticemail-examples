# GTM agent

Give this agent an inbox and it runs outbound for you. It sends a first-touch
cold email, then classifies every reply - interested, not interested, referral,
or objection - and responds. Warm leads get a call and a CC to you for handoff.

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

On startup the agent prints its inbox address and sends a first-touch email to
your prospect. Reply to that email and watch it classify and respond. It only
handles mail that arrives after it starts.

## Configure

Set these as environment variables (see `.env.example`):

| Variable | Default | What it does |
| --- | --- | --- |
| `USER_NAME` | `Sam` | Who the outreach is from, and who warm leads are handed to. |
| `PROSPECT_EMAIL` | `prospect@example.com` | Who the first-touch email is sent to. |
| `INBOX_USERNAME` | `gtm-agent` | Local part of the inbox address. |
| `ANTHROPIC_MODEL` | `claude-sonnet-5` | Claude model to use. |
| `POLL_SECONDS` | `10` | How often to check for new mail. |

The outreach voice and reply-handling rules live in the system prompt inside
`agent.py` / `agent.ts` - edit them to match your motion.
