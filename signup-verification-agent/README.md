# Signup & verification agent

Give a browser-automation agent an inbox of its own. When it signs up for a
service, the confirmation email lands here and Claude extracts the verification
code and magic link as structured JSON your automation can act on - no shared
personal inbox, no manual copy-paste of codes.

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

On startup the agent prints its inbox address. Use it to sign up somewhere,
then watch it print `service`, `code`, and `link` as the emails arrive.

## Configure

| Variable | Default | What it does |
| --- | --- | --- |
| `INBOX_USERNAME` | `verification-agent` | Local part of the inbox address. |
| `FORWARD_TO` | (unset) | If set, also emails the extracted JSON to this address. |
| `ANTHROPIC_MODEL` | `claude-sonnet-5` | Claude model to use. |
| `POLL_SECONDS` | `5` | How often to check for new mail. |

The extraction rules (what counts as a verification email, what to pull out)
live in the system prompt inside `prompt.py` / `src/prompt.ts`.
