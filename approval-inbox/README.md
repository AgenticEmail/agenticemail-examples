# Approval Inbox

Your inbox is your approval queue - approve everything from email. Systems email
this agent their approval requests, it summarises each one, and you approve or
reject by replying in the thread - all from an inbox it owns.

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

On startup the agent prints its inbox address. Point your systems at that
address and reply "approve" or "reject" to each request. It only responds to
mail that arrives after it starts.

## Configure

Set these as environment variables (see `.env.example`):

| Variable | Default | What it does |
| --- | --- | --- |
| `APPROVER_NAME` | `Alex` | Who approves or rejects the requests. |
| `INBOX_USERNAME` | `approval-inbox` | Local part of the inbox address. |
| `ANTHROPIC_MODEL` | `claude-sonnet-5` | Claude model to use. |
| `POLL_SECONDS` | `10` | How often to check for new mail. |

The approval behaviour lives in the system prompt inside `agent.py` /
`agent.ts` - edit it to match how you want requests handled.
