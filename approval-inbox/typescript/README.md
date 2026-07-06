# Approval Inbox - TypeScript

```bash
npm install
export AGENTICEMAIL_API_KEY="am_..."   # app.agenticemail.dev/keys
export ANTHROPIC_API_KEY="sk-ant-..."  # console.anthropic.com
npm start
```

Runs with [`tsx`](https://tsx.is) - no build step. The agent prints its inbox
address on startup. Point your systems at it and reply "approve" or "reject" to
each request. It only answers mail that arrives after it starts.

- `src/agent.ts` - creates the inbox and runs the poll/reply loop.
- `src/prompt.ts` - the approval behaviour. Edit `buildSystemPrompt` to match how you want requests handled.

Config is via environment variables - see `.env.example`.
