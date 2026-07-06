# Inbox Zero Agent

> **Productivity** - Drafts replies while you sleep - you review and send.

Give this agent an inbox it owns. For every new email, Claude decides whether it
needs a reply, and if so writes one in your voice and saves it as a **draft**.
Nothing is ever sent automatically. You open your drafts, skim each one, and send
the ones you like. Wake up to a queue of ready-to-send replies instead of a wall
of unread mail.

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

On startup the agent prints its inbox address. Forward or send mail to that
address and watch it queue drafts. It only handles mail that arrives after it
starts.

## It only drafts - it never sends

This agent calls `drafts.create`, which saves a draft for review. It never
sends, replies, or forwards on its own. Every draft waits in your drafts folder
until you read it and hit send yourself. That is the whole point: speed on the
writing, a human on the sending.

## Configure

Set these as environment variables (see `.env.example`):

| Variable | Default | What it does |
| --- | --- | --- |
| `USER_NAME` | `Alex` | Whose voice the drafts are written in. |
| `INBOX_USERNAME` | `inbox-zero-agent` | Local part of the inbox address. |
| `ANTHROPIC_MODEL` | `claude-sonnet-5` | Claude model to use. |
| `POLL_SECONDS` | `10` | How often to check for new mail. |

The voice and triage rules (when to reply, when to flag for you) live in the
system prompt inside `prompt.py` / `prompt.ts` - edit them to match how you
write.
