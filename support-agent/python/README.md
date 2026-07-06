# Support agent - Python

```bash
pip install -r requirements.txt
export AGENTICEMAIL_API_KEY="am_..."   # app.agenticemail.dev/keys
export ANTHROPIC_API_KEY="sk-ant-..."  # console.anthropic.com
python agent.py
```

The agent prints its inbox address on startup. Email it and it replies. It only
answers mail that arrives after it starts.

- `agent.py` - creates the inbox and runs the poll/reply loop.
- `prompt.py` - the triage rules and tone. Edit `build_system_prompt` to match your product and knowledge base.

Config is via environment variables - see `.env.example`.
