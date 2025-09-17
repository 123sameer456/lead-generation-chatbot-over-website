
--- README.md ---
# AI Chatbot Demo (Flask + Frontend Widget)

## Setup
1. Create a Python virtual environment and install requirements:

```bash
python -m venv venv
source venv/bin/activate   # on Windows use venv\Scripts\activate
pip install flask openai
```

2. Export your OpenAI API key in an environment variable:

```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_MODEL="gpt-4o-mini"
```

3. Run the app:

```bash
python app.py
```

4. Open http://127.0.0.1:5000 in your browser. The chat widget appears bottom-right.

## Notes
- Stores only the last 10 messages per session in memory for context.
- For production: add session management, persistent storage, rate-limiting, authentication, and secure contact forwarding to CRM/Slack/HubSpot.
- Contact intent detection is basic; enhance with regex or an intent model.

---

# End of files
