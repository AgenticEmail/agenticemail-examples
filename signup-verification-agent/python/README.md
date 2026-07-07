# Signup & verification agent - Python

```bash
pip install -r requirements.txt
export AGENTICEMAIL_API_KEY="am_..."   # app.agenticemail.dev/keys
export ANTHROPIC_API_KEY="sk-ant-..."  # console.anthropic.com
python agent.py
```

The agent prints its inbox address on startup. Use that address to sign up for
a service (or in a browser-automation flow), and when the confirmation email
arrives Claude extracts the code and magic link as JSON.

- `agent.py` - creates the inbox, watches for mail, extracts `{service, code, link}`.
- `prompt.py` - the extraction rules. Edit `build_system_prompt` to tune what counts as a verification email.

Set `FORWARD_TO` to also email the extracted JSON to yourself. Config is via
environment variables - see `.env.example`.
