
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
