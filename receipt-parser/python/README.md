# Receipt & Expense Parser - Python

```bash
pip install -r requirements.txt
export AGENTICEMAIL_API_KEY="am_..."   # app.agenticemail.dev/keys
export ANTHROPIC_API_KEY="sk-ant-..."  # console.anthropic.com
python agent.py
```

The agent prints its inbox address on startup. Forward or photograph a receipt
to that address and it turns it into a clean expense row. It only handles mail
that arrives after it starts.

- `agent.py` - creates the inbox and runs the poll/extract/route loop.
- `prompt.py` - the expense rules and behaviour. Edit `build_system_prompt` to match your process.

Extraction uses Claude's vision on receipt photos (image attachments) and PDF
receipts, so an `ANTHROPIC_MODEL` that supports images and documents is required
(the default `claude-sonnet-5` does).

Config is via environment variables - see `.env.example`.
