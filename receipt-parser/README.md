# Receipt & Expense Parser

Forward receipts - they become clean expense rows. People forward or photograph
receipts and send them to an inbox the agent owns. Claude reads each one with
its vision - both receipt photos (image attachments) and PDF receipts - pulls
out the merchant, date, total, tax, and payment method, categorises the expense,
flags anything unusual, routes a clean row to your expense system, and confirms
the merchant and total with the sender - all from an inbox it owns.

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

On startup the agent prints its inbox address. Forward or photograph a receipt
to that address and watch it become an expense row. It only handles mail that
arrives after it starts.

Extraction uses Claude's vision on receipt photos and PDFs, so the configured
`ANTHROPIC_MODEL` must support images and documents (the default
`claude-sonnet-5` does).

## Configure

Set these as environment variables (see `.env.example`):

| Variable | Default | What it does |
| --- | --- | --- |
| `EXPENSE_EMAIL` | `expenses@example.com` | Where routed expense rows are sent. |
| `FLAG_LIMIT` | `500` | Receipts with a total over this amount are flagged for review. |
| `INBOX_USERNAME` | `receipt-parser` | Local part of the inbox address receipts are sent to. |
| `ANTHROPIC_MODEL` | `claude-sonnet-5` | Claude model to use (must support image and PDF vision). |
| `POLL_SECONDS` | `10` | How often to check for new mail. |

The expense rules (extraction, categories, flagging, sender reply) live in the
system prompt inside `agent.py` / `agent.ts` - edit them to match your process.
