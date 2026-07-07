# Receipt & Expense Parser - TypeScript

```bash
npm install
export AGENTICEMAIL_API_KEY="am_..."   # app.agenticemail.dev/keys
export ANTHROPIC_API_KEY="sk-ant-..."  # console.anthropic.com
npm start
```

Runs with [`tsx`](https://tsx.is) - no build step. The agent prints its inbox
address on startup. Forward or photograph a receipt to that address and it turns
it into a clean expense row. It only handles mail that arrives after it starts.

- `src/agent.ts` - creates the inbox and runs the poll/extract/route loop.
- `src/prompt.ts` - the expense rules and behaviour. Edit `buildSystemPrompt` to match your process.

Extraction uses Claude's vision on receipt photos (image attachments) and PDF
receipts, so an `ANTHROPIC_MODEL` that supports images and documents is required
(the default `claude-sonnet-5` does).

Config is via environment variables - see `.env.example`.
