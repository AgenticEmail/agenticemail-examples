# Signup & verification agent - TypeScript

```bash
npm install
export AGENTICEMAIL_API_KEY="am_..."   # app.agenticemail.dev/keys
export ANTHROPIC_API_KEY="sk-ant-..."  # console.anthropic.com
npm start
```

Runs with [`tsx`](https://tsx.is) - no build step. The agent prints its inbox
address on startup. Use that address to sign up for a service (or in a
browser-automation flow), and when the confirmation email arrives Claude
extracts the code and magic link as JSON.

- `src/agent.ts` - creates the inbox, watches for mail, extracts `{service, code, link}`.
- `src/prompt.ts` - the extraction rules. Edit `buildSystemPrompt` to tune what counts as a verification email.

Set `FORWARD_TO` to also email the extracted JSON to yourself. Config is via
environment variables - see `.env.example`.
