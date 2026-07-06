# Invoice processor

Extract, match, and route invoices from PDF attachments. Vendors email PDF
invoices to an inbox the agent owns. Claude reads each PDF with its vision,
pulls out the vendor, invoice number, amount, currency, and due date, decides
approved vs needs-review against your limit, routes a summary to your AP team,
and confirms receipt with the vendor - all from an inbox it owns.

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

On startup the agent prints its inbox address. Have a vendor email a PDF invoice
to that address and watch it get routed. It only handles mail that arrives after
it starts.

Extraction uses Claude's PDF vision, so the configured `ANTHROPIC_MODEL` must
support documents (the default `claude-sonnet-5` does).

## Configure

Set these as environment variables (see `.env.example`):

| Variable | Default | What it does |
| --- | --- | --- |
| `AP_EMAIL` | `ap@example.com` | Where routed invoices are sent. |
| `AUTO_APPROVE_LIMIT` | `1000` | Invoices under this amount are marked approved; the rest are needs-review. |
| `INBOX_USERNAME` | `invoice-processor` | Local part of the inbox address vendors email. |
| `ANTHROPIC_MODEL` | `claude-sonnet-5` | Claude model to use (must support PDF vision). |
| `POLL_SECONDS` | `10` | How often to check for new mail. |

The accounts-payable rules (matching, approval logic, vendor reply) live in the
system prompt inside `agent.py` / `agent.ts` - edit them to match your process.
