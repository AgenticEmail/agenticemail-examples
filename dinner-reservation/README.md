# Dinner Reservation Agent

Emails restaurants, handles replies, confirms the booking.

Give this agent an inbox and it books your table for you. It emails the
restaurant an opening request with your date, time window, party size, and
dietary needs, then handles every reply - accepting any time inside your window,
confirming the booking, and sending you a one-line confirmation. If the
restaurant cannot accommodate, it reports back so you can pick another.

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

On startup the agent prints its inbox address and sends the opening reservation
request to your restaurant. Reply as the restaurant and watch it negotiate and
confirm. It only handles mail that arrives after it starts.

## Configure

Set these as environment variables (see `.env.example`):

| Variable | Default | What it does |
| --- | --- | --- |
| `USER_NAME` | `Sam` | Who the table is booked for. |
| `PARTY_SIZE` | `2` | How many people the reservation is for. |
| `DATE_WINDOW` | `Friday 7-8pm` | The date and time window to book. |
| `AREA` | `downtown` | The area to book near. |
| `PREFERENCES` | `Italian, quiet` | Cuisine and any other preferences or dietary needs. |
| `RESTAURANT_EMAIL` | `restaurant@example.com` | Who the opening request is sent to. |
| `INBOX_USERNAME` | `dinner-reservation` | Local part of the inbox address. |
| `ANTHROPIC_MODEL` | `claude-sonnet-5` | Claude model to use. |
| `POLL_SECONDS` | `10` | How often to check for new mail. |

The booking details and negotiation rules live in the system prompt inside
`agent.py` / `agent.ts` - edit them to match your plans.
