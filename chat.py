import os
from openai import OpenAI
from dotenv import load_dotenv

from gcc import save_lead_to_gsheet
from slack_send import send_lead_to_slack

# 
# Load API key from .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI()

# Website context
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

# Assistant persona
ASSISTANT_PERSONA = (
    "You are SamAssist — a professional, friendly, and persuasive sales assistant representing the company. "
    "Speak like a knowledgeable company representative: concise, helpful, and focused on converting interested website visitors. "
    "Use the website context (provided) to answer questions about services, pricing, timelines, and process. "
    "If a visitor shows buying intent or asks for a demo/quote, politely request contact details (name, email, phone) "
    "and say you'll forward them to the sales team immediately. "
    "Always confirm understanding and offer next steps (demo, call scheduling, proposal)."
)

# Memory for last 10 messages
CHAT_HISTORY = []
MAX_HISTORY = 10

def chat_assistant(user_input: str) -> str:
    """Chat assistant with memory of last 10 messages."""

    global CHAT_HISTORY

    # Store user input in history
    CHAT_HISTORY.append({"role": "user", "content": user_input})
    CHAT_HISTORY = CHAT_HISTORY[-MAX_HISTORY:]

    # Build messages
    messages = [
        {"role": "system", "content": ASSISTANT_PERSONA},
        {"role": "system", "content": f"Website context: {website_context}"}
    ] + CHAT_HISTORY

    # Call OpenAI
    resp = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=messages,
        max_tokens=512,
        temperature=0.2,
    )

    assistant_text = resp.choices[0].message.content.strip()

    # Store assistant reply
    CHAT_HISTORY.append({"role": "assistant", "content": assistant_text})
    CHAT_HISTORY = CHAT_HISTORY[-MAX_HISTORY:]
    # if user have contact details ( phone , email or any other) then run below 2 functions, otherwise ignore
        save_lead_to_gsheet("Website bot", "<lead email here>", "<phone number here>", ":summary or description here")
        send_lead_to_slack("Website bot", "<lead email here>", "<phone number here>", ":summary or description here")

    return assistant_text


# === Run in terminal ===
if __name__ == "__main__":
    print("🤖 SamAssist is live! Type 'quit' to exit.\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit"]:
            print("👋 Goodbye!")
            break
        reply = chat_assistant(user_input)
        print(f"SamAssist: {reply}\n")


