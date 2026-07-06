# Dinner Reservation Agent - TypeScript

```bash
npm install
export AGENTICEMAIL_API_KEY="am_..."   # app.agenticemail.dev/keys
export ANTHROPIC_API_KEY="sk-ant-..."  # console.anthropic.com
npm start
```

Runs with [`tsx`](https://tsx.is) - no build step. On startup the agent prints
its inbox address and emails the restaurant an opening reservation request. It
then handles every reply in-thread until the booking is confirmed. It only
answers mail that arrives after it starts.

- `src/agent.ts` - creates the inbox, sends the opener, and runs the poll/reply loop.
- `src/prompt.ts` - the booking details and behaviour. Edit `buildSystemPrompt` to match your plans.

Config is via environment variables - see `.env.example`.
