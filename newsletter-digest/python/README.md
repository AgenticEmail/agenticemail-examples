# Newsletter digest - Python

```bash
pip install -r requirements.txt
export AGENTICEMAIL_API_KEY="am_..."   # app.agenticemail.dev/keys
export ANTHROPIC_API_KEY="sk-ant-..."  # console.anthropic.com
python agent.py
```

The agent prints its inbox address on startup. Subscribe that address to a few
newsletters, then run it once a day (see the cron note in the top-level README).
Each run reads every inbound message and emails you one grouped digest. If
nothing has arrived yet, it says so and exits.

- `agent.py` - creates the inbox, reads inbound mail, and sends one digest.
- `prompt.py` - what to include and how to group it. Edit `build_system_prompt` to taste.

Config is via environment variables - see `.env.example`.
