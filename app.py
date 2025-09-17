# Project: AI Chatbot (Flask backend + Bottom-right web widget)
# Files included below. Save each file with the shown filename and run as instructed.

--- app.py ---
from flask import Flask, render_template, request, jsonify
import os
import openai

app = Flask(__name__)

# Load API key from environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise RuntimeError('Set the OPENAI_API_KEY environment variable before running.')
openai.api_key = OPENAI_API_KEY

# === Persona / System prompt ===
ASSISTANT_PERSONA = (
    "You are SamAssist — a professional, friendly, and persuasive sales assistant representing the company. "
    "Speak like a knowledgeable company representative: concise, helpful, and focused on converting interested website visitors. "
    "Use the website context (provided) to answer questions about services, pricing, timelines, and process. "
    "If a visitor shows buying intent or asks for a demo/quote, politely request contact details (name, email, phone) and say you'll forward them to the sales team immediately. "
    "Always confirm understanding and offer next steps (demo, call scheduling, proposal).")

# Minimal chat history store (for demo only). In production, use a persistent store keyed by session.
CHAT_HISTORY = {}
MAX_HISTORY = 10

@app.route('/')
def index():
    website_context = {
        'company_name': 'Your Company Name',
        'services': [
            'AI Chatbots & Conversational Automation',
            'Lead Capture & Qualification',
            'CRM Integrations (HubSpot, Salesforce, Google Sheets)',
            'Custom Campaign Chatbots for Ads & Landing Pages'
        ],
        'about': "We build high-converting AI chatbots tailored for marketing agencies and their clients."
    }
    return render_template('index.html', website_context=website_context)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json or {}
    user_message = data.get('message', '').strip()
    session_id = data.get('session_id', 'demo_session')

    if not user_message:
        return jsonify({'error': 'Empty message'}), 400

    if session_id not in CHAT_HISTORY:
        CHAT_HISTORY[session_id] = []

    # Append the new user message
    CHAT_HISTORY[session_id].append({"role": "user", "content": user_message})
    
    # Keep only the last MAX_HISTORY messages
    CHAT_HISTORY[session_id] = CHAT_HISTORY[session_id][-MAX_HISTORY:]

    # Build messages for the Chat Completions API
    messages = [
        {"role": "system", "content": ASSISTANT_PERSONA},
        {"role": "system", "content": f"Website context: {request.json.get('website_context', '')}"},
    ] + CHAT_HISTORY[session_id]

    try:
        resp = openai.ChatCompletion.create(
            model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
            messages=messages,
            max_tokens=512,
            temperature=0.2,
        )
        assistant_text = resp['choices'][0]['message']['content']

        # Append assistant reply to history
        CHAT_HISTORY[session_id].append({"role": "assistant", "content": assistant_text})
        CHAT_HISTORY[session_id] = CHAT_HISTORY[session_id][-MAX_HISTORY:]

        capture_contact = False
        contact_fields = {}
        if any(word in user_message.lower() for word in ['email', 'contact', 'phone', 'demo', 'quote']):
            capture_contact = True

        return jsonify({'reply': assistant_text, 'capture_contact': capture_contact, 'contact_fields': contact_fields})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

--- templates/index.html ---
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Website with AI Chatbot Demo</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
  <header>
    <h1>{{ website_context.company_name }}</h1>
    <p>{{ website_context.about }}</p>
  </header>

  <main>
    <section>
      <h2>Services</h2>
      <ul>
        {% for s in website_context.services %}
          <li>{{ s }}</li>
        {% endfor %}
      </ul>
    </section>
  </main>

  <!-- Chat widget placeholder (bottom-right) -->
  <div id="chat-widget-root"></div>

  <script>
    window.WEBSITE_CONTEXT = `Company: {{ website_context.company_name }}\nServices: {{ website_context.services | join(', ') }}\nAbout: {{ website_context.about }}`;
  </script>
  <script src="/static/chat.js"></script>
</body>
</html>

--- static/style.css ---
:root{
  --primary: #0b72ff;
  --bg: #0f1724;
  --card: #0b1220;
}

body{font-family: Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; margin:0; padding:0;}

#chat-widget-root{position:fixed; right:20px; bottom:20px; z-index:9999;}

.chat-widget {
  width:360px; max-width:90vw; height:520px; background:var(--card); border-radius:12px; box-shadow:0 10px 30px rgba(2,6,23,0.6); display:flex; flex-direction:column; overflow:hidden;
}
.chat-header{padding:12px 14px; display:flex; align-items:center; gap:10px; background:linear-gradient(90deg,var(--primary),#4ea8ff); color:white}
.chat-header .title{font-weight:700}
.chat-messages{flex:1; padding:12px; overflow:auto; background:linear-gradient(180deg, rgba(255,255,255,0.02), transparent);}
.msg{margin-bottom:10px; max-width:85%; padding:8px 10px; border-radius:10px}
.msg.user{align-self:flex-end; background:#0b84ff22; color:white}
.msg.assistant{align-self:flex-start; background:#0b122033; color:#e6eef8}
.chat-input{padding:10px; display:flex; gap:8px; border-top:1px solid rgba(255,255,255,0.03)}
.chat-input input{flex:1; padding:10px 12px; border-radius:8px; border:1px solid rgba(255,255,255,0.06); background:transparent; color:#e6eef8}
.chat-input button{padding:10px 14px; border-radius:8px; border:none; background:var(--primary); color:white; cursor:pointer}

.chat-minimized{width:60px; height:60px; border-radius:30px; background:var(--primary); display:flex; align-items:center; justify-content:center; color:white; cursor:pointer}

--- static/chat.js ---
(() => {
  const root = document.getElementById('chat-widget-root');

  let minimized = true;

  function createMinimized() {
    root.innerHTML = '';
    const btn = document.createElement('div');
    btn.className = 'chat-minimized';
    btn.innerText = 'Chat';
    btn.onclick = () => { minimized = false; renderWidget(); };
    root.appendChild(btn);
  }

  function renderWidget() {
    root.innerHTML = '';
    const widget = document.createElement('div');
    widget.className = 'chat-widget';

    const header = document.createElement('div'); header.className='chat-header';
    const title = document.createElement('div'); title.className='title'; title.innerText='Sales Assistant';
    const close = document.createElement('button'); close.innerText='✕'; close.style.marginLeft='auto'; close.onclick = () => { minimized=true; createMinimized(); };
    header.appendChild(title); header.appendChild(close);

    const messages = document.createElement('div'); messages.className='chat-messages';

    const inputWrap = document.createElement('div'); inputWrap.className='chat-input';
    const input = document.createElement('input'); input.placeholder='Type your question...';
    const btn = document.createElement('button'); btn.innerText='Send';

    inputWrap.appendChild(input); inputWrap.appendChild(btn);

    widget.appendChild(header); widget.appendChild(messages); widget.appendChild(inputWrap);
    root.appendChild(widget);

    addAssistantMessage(messages, 'Hi! I\'m here to help. How can I assist you with our services today?');

    btn.onclick = () => { sendMessage(input, messages); };
    input.addEventListener('keydown', (e) => { if (e.key === 'Enter') sendMessage(input, messages); });
  }

  function addUserMessage(container, text) {
    const el = document.createElement('div'); el.className='msg user'; el.innerText = text; container.appendChild(el); container.scrollTop = container.scrollHeight;
  }
  function addAssistantMessage(container, text) {
    const el = document.createElement('div'); el.className='msg assistant'; el.innerText = text; container.appendChild(el); container.scrollTop = container.scrollHeight;
  }

  async function sendMessage(input, messages) {
    const val = input.value.trim();
    if (!val) return;
    addUserMessage(messages, val);
    input.value = '';
    addAssistantMessage(messages, 'Typing...');

    try {
      const resp = await fetch('/chat', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ message: val, session_id: 'demo_session', website_context: window.WEBSITE_CONTEXT })
      });
      const data = await resp.json();
      const typing = Array.from(messages.querySelectorAll('.msg.assistant')).pop();
      if (typing) typing.remove();

      if (data.error) {
        addAssistantMessage(messages, 'Error: ' + data.error);
        return;
      }
      addAssistantMessage(messages, data.reply || 'Sorry, I had trouble answering that.');

      if (data.capture_contact) {
        const contactPrompt = document.createElement('div'); contactPrompt.className='msg assistant';
        contactPrompt.innerHTML = 'It seems you\'re interested — may I get your name, email, and phone so our sales rep can reach out?';
        messages.appendChild(contactPrompt);
      }

    } catch (err) {
      addAssistantMessage(messages, 'Network error: ' + err.message);
    }
  }

  createMinimized();
})();

