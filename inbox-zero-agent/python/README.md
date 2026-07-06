# Inbox Zero Agent - Python

```bash
pip install -r requirements.txt
export AGENTICEMAIL_API_KEY="am_..."   # app.agenticemail.dev/keys
export ANTHROPIC_API_KEY="sk-ant-..."  # console.anthropic.com
python agent.py
```

The agent prints its inbox address on startup. Forward or send mail to it and it
writes a reply as a **draft** - it never sends anything. Review each draft and
send it yourself. It only handles mail that arrives after it starts.

- `agent.py` - creates the inbox and runs the poll/draft loop.
- `prompt.py` - the voice and triage rules. Edit `build_system_prompt` to match how you write.

Config is via environment variables - see `.env.example`.
