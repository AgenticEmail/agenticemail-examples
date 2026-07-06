# Negotiation agent

Multi-party negotiator for used cars, apartments, B2B contracts. Email this
agent a deal and it works the back-and-forth for you: it anchors, concedes
slowly, holds your walk-away line, and confirms the deal in plain terms once the
other side hits your target - all from an inbox it owns.

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
| `USER_NAME` | `Sam` | Who the agent negotiates on behalf of. |
| `TARGET_TERMS` | `$18,000 out the door` | The deal the agent is aiming for. |
| `WALK_AWAY` | `$20,000` | The point past which the agent stops and checks with you. |
| `INBOX_USERNAME` | `negotiation-agent` | Local part of the inbox address. |
| `ANTHROPIC_MODEL` | `claude-sonnet-5` | Claude model to use. |
| `POLL_SECONDS` | `10` | How often to check for new mail. |

The negotiation tactics live in the system prompt inside `agent.py` / `agent.ts`
- edit them to match how hard you want to push.
