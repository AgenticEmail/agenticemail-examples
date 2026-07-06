# GTM agent - Python

```bash
pip install -r requirements.txt
export AGENTICEMAIL_API_KEY="am_..."   # app.agenticemail.dev/keys
export ANTHROPIC_API_KEY="sk-ant-..."  # console.anthropic.com
python agent.py
```

The agent prints its inbox address on startup, then sends a first-touch email to
your prospect. Reply to it and the agent classifies and responds. It only handles
mail that arrives after it starts.

- `agent.py` - creates the inbox, sends the opener, and runs the poll/reply loop.
- `prompt.py` - the outreach voice and reply-handling rules. Edit `build_system_prompt` to match your motion.

Config is via environment variables - see `.env.example`.
