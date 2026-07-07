# AI recruiter

Email this agent as an applicant. It screens the application against the role's
must-haves, offers three interview slots, and keeps candidates warm - all from an
inbox it owns.

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
| `USER_NAME` | `Dana` | Who candidates are interviewing with. |
| `ROLE` | `Senior Backend Engineer` | The role being hired for. |
| `REQUIREMENTS` | `5+ years Python, distributed systems, startup experience` | Must-haves the agent screens against. |
| `INTERVIEW_HOURS` | `10:00-16:00` | Window the agent offers interview slots in. |
| `TIMEZONE` | `America/Los_Angeles` | Timezone the agent books in. |
| `INBOX_USERNAME` | `ai-recruiter` | Local part of the inbox address. |
| `ANTHROPIC_MODEL` | `claude-sonnet-5` | Claude model to use. |
| `POLL_SECONDS` | `10` | How often to check for new mail. |

The screening and interview behaviour lives in the system prompt inside
`prompt.py` / `prompt.ts` - edit it to match your hiring process.
