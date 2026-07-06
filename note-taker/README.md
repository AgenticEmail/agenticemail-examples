# Note Taker

Forward emails - they become Markdown notes you can search. This agent owns an
inbox: forward it a message, article, or thread and it replies with one clean,
titled, tagged Markdown note ready to drop into your notes app.

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

On startup the agent prints its inbox address. Forward that address an email and
watch it reply. It only responds to mail that arrives after it starts.

## Configure

Set these as environment variables (see `.env.example`):

| Variable | Default | What it does |
| --- | --- | --- |
| `INBOX_USERNAME` | `note-taker` | Local part of the inbox address. |
| `ANTHROPIC_MODEL` | `claude-sonnet-5` | Claude model to use. |
| `POLL_SECONDS` | `10` | How often to check for new mail. |

The note format (title, summary, bullets, tags) lives in the system prompt inside
`prompt.py` / `prompt.ts` - edit it to match how you like to take notes.
