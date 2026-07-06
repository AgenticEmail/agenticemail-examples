# Note Taker - TypeScript

```bash
npm install
export AGENTICEMAIL_API_KEY="am_..."   # app.agenticemail.dev/keys
export ANTHROPIC_API_KEY="sk-ant-..."  # console.anthropic.com
npm start
```

Runs with [`tsx`](https://tsx.is) - no build step. The agent prints its inbox
address on startup. Forward it an email and it replies with a clean Markdown
note. It only answers mail that arrives after it starts.

- `src/agent.ts` - creates the inbox and runs the poll/reply loop.
- `src/prompt.ts` - the note format and behaviour. Edit `buildSystemPrompt` to match your style.

Config is via environment variables - see `.env.example`.
