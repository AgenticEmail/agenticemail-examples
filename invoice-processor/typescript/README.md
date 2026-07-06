# Invoice processor - TypeScript

```bash
npm install
export AGENTICEMAIL_API_KEY="am_..."   # app.agenticemail.dev/keys
export ANTHROPIC_API_KEY="sk-ant-..."  # console.anthropic.com
npm start
```

Runs with [`tsx`](https://tsx.is) - no build step. The agent prints its inbox
address on startup. Vendors email PDF invoices to that address and it processes
them. It only handles mail that arrives after it starts.

- `src/agent.ts` - creates the inbox and runs the poll/extract/route loop.
- `src/prompt.ts` - the accounts-payable rules and behaviour. Edit `buildSystemPrompt` to match your process.

Extraction uses Claude's PDF vision, so an `ANTHROPIC_MODEL` that supports
documents is required (the default `claude-sonnet-5` does).

Config is via environment variables - see `.env.example`.
