# Newsletter digest

A daily digest of everything that hit your inbox. Point an AgenticEmail inbox
at your newsletters and updates. Once a day this agent reads everything that
arrived, groups it by theme, flags anything time-sensitive, and emails you a
single scannable digest - from an inbox it owns.

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

On startup the agent prints its inbox address. Subscribe that address to a few
newsletters, then run the agent. Each run reads every inbound message and sends
you one grouped digest. If nothing has arrived yet, it says so and exits.

## Schedule it

This runs once and exits - it is meant to run on a schedule, once a day. A cron
entry that digests every morning at 8am:

```cron
0 8 * * *  cd /path/to/newsletter-digest/python && python agent.py
```

## Configure

Set these as environment variables (see `.env.example`):

| Variable | Default | What it does |
| --- | --- | --- |
| `USER_EMAIL` | `you@example.com` | Where the daily digest is sent. |
| `INBOX_USERNAME` | `newsletter-digest` | Local part of the inbox address. |
| `ANTHROPIC_MODEL` | `claude-sonnet-5` | Claude model to use. |

What goes in the digest and how it is grouped lives in the system prompt inside
`prompt.py` / `prompt.ts` - edit it to match what you subscribe to.
