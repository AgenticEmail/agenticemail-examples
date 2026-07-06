# Scheduling agent

Email this agent to book time. It classifies the request, offers three slots
that fit your rules, and handles the back-and-forth until a time is confirmed -
all from an inbox it owns.

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
| `USER_NAME` | `Alex` | Who people are booking time with. |
| `TIMEZONE` | `America/Los_Angeles` | Timezone the agent books in. |
| `INBOX_USERNAME` | `scheduling-agent` | Local part of the inbox address. |
| `ANTHROPIC_MODEL` | `claude-sonnet-5` | Claude model to use. |
| `POLL_SECONDS` | `10` | How often to check for new mail. |

The scheduling rules (working hours, buffers, max calls per day) live in the
system prompt inside `agent.py` / `agent.ts` - edit them to match your calendar.
