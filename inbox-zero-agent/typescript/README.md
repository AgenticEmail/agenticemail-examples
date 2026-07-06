# Inbox Zero Agent - TypeScript

```bash
npm install
export AGENTICEMAIL_API_KEY="am_..."   # app.agenticemail.dev/keys
export ANTHROPIC_API_KEY="sk-ant-..."  # console.anthropic.com
npm start
```

Runs with [`tsx`](https://tsx.is) - no build step. The agent prints its inbox
address on startup. Forward or send mail to it and it writes a reply as a
**draft** - it never sends anything. Review each draft and send it yourself. It
only handles mail that arrives after it starts.

- `src/agent.ts` - creates the inbox and runs the poll/draft loop.
- `src/prompt.ts` - the voice and triage rules. Edit `buildSystemPrompt` to match how you write.

Config is via environment variables - see `.env.example`.
