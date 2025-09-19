import os
import re
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
from dotenv import load_dotenv

from gcc import save_lead_to_gsheet
from slack_send import send_lead_to_slack

# Load API key from .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI()

app = Flask(__name__)

# Website context - Updated to match the marketing website
website_context = {
    'company_name': 'MarketFlow AI',
    'services': [
        'AI Chatbots & Conversational Automation - Deploy intelligent chatbots that engage visitors, qualify leads, and provide instant customer support around the clock',
        'Lead Capture & Qualification - Automatically capture and qualify leads with smart forms and conversational interfaces that increase conversion rates',
        'CRM Integrations (HubSpot, Salesforce, Google Sheets) - Seamlessly integrate with popular platforms to streamline your sales process',
        'Custom Campaign Chatbots for Ads & Landing Pages - Create targeted chatbots for your ad campaigns to maximize ROI and campaign performance',
        'Marketing Analytics & Insights - Track performance, analyze customer interactions, and optimize your marketing strategies with detailed analytics',
        'Marketing Automation - Automate your entire marketing funnel from lead generation to customer retention with intelligent workflows' ,
        
    ],
    'about': "MarketFlow AI specializes in building high-converting AI chatbots tailored for marketing agencies and their clients. Our solutions don't just automate conversations—they create meaningful connections that drive real business results.",
    'value_proposition': "Transform your marketing with AI-powered solutions that convert visitors into customers 24/7",
    'target_audience': "Marketing agencies and businesses looking to automate their marketing processes and increase conversions",
    'pricing_info': "We offer custom pricing based on your specific needs. Packages typically start from $500/month for basic chatbot implementation, with enterprise solutions ranging from $2000-$5000/month.",
    'contact_info': "Ready to get started? I can connect you with our sales team for a free consultation and custom quote."
}

# Enhanced Assistant persona based on website content
ASSISTANT_PERSONA = f"""You are SamAssist — a professional, friendly, and persuasive AI marketing consultant representing {website_context['company_name']}. 

Your role:
- Act as a knowledgeable company representative who understands marketing challenges
- Be concise, helpful, and focused on converting interested website visitors
- Demonstrate expertise in AI chatbots, marketing automation, and lead generation
- Build trust by understanding the visitor's specific business needs
- Propose solution according to user's need and totally relateable to user's need. 
- try to improve user's exisiting process.

Your expertise covers:
{chr(10).join([f"• {service}" for service in website_context['services']])}

Key talking points:
- We specialize in high-converting AI chatbots for marketing agencies
- Our solutions create meaningful connections that drive real business results
- We integrate with popular CRMs and marketing tools
- Custom pricing based on specific business needs
- Free consultations available
- hit psycological truth hooks when you propose a solution.


When visitors show buying intent or ask for demos/quotes/pricing:
1. Ask relevant qualifying questions about their business
2. Politely request contact details (name, email, phone) 
3. Confirm you'll forward them to our sales team immediately
4. Offer specific next steps (demo scheduling, proposal, free consultation)

Always be helpful, never pushy, and focus on solving their marketing challenges."""

# Memory for conversation history
conversation_sessions = {}
MAX_HISTORY = 10

def extract_contact_info(text):
    """Extract contact information from text using regex patterns."""
    contact_info = {}
    
    # Email pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    if emails:
        contact_info['email'] = emails[0]
    
    # Phone pattern (various formats)
    phone_patterns = [
        r'\b\d{3}-\d{3}-\d{4}\b',  # 123-456-7890
        r'\b\(\d{3}\)\s*\d{3}-\d{4}\b',  # (123) 456-7890
        r'\b\d{3}\.\d{3}\.\d{4}\b',  # 123.456.7890
        r'\b\d{10,}\b',  # 1234567890 (10+ digits)
        r'\+\d{1,3}\s*\d{3,4}\s*\d{3,4}\s*\d{3,4}',  # +1 234 567 8900
    ]
    
    for pattern in phone_patterns:
        phones = re.findall(pattern, text)
        if phones:
            contact_info['phone'] = phones[0]
            break
    
    # Name extraction (simple heuristic)
    # Look for "I'm [Name]" or "My name is [Name]" patterns
    name_patterns = [
        r"I'm\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        r"My name is\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        r"This is\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        r"I am\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)"
    ]
    
    for pattern in name_patterns:
        names = re.findall(pattern, text, re.IGNORECASE)
        if names:
            contact_info['name'] = names[0]
            break
    
    return contact_info

def has_contact_details(contact_info):
    """Check if contact info contains email or phone."""
    return 'email' in contact_info or 'phone' in contact_info

def generate_lead_summary(conversation_history, contact_info):
    """Generate a summary of the conversation for lead tracking."""
    # Get the last few messages to understand context
    recent_messages = conversation_history[-6:] if len(conversation_history) > 6 else conversation_history
    
    user_messages = [msg['content'] for msg in recent_messages if msg['role'] == 'user']
    
    # Create a summary
    if user_messages:
        interests = ", ".join(user_messages[:3])  # Take first 3 user messages
        summary = f"Interested in: {interests[:200]}..."  # Limit length
    else:
        summary = "Website visitor inquiry via chatbot"
    
    return summary

def chat_assistant(user_input: str, session_id: str = 'default') -> str:
    """Chat assistant with memory and lead capture functionality."""
    
    global conversation_sessions
    
    # Initialize session if not exists
    if session_id not in conversation_sessions:
        conversation_sessions[session_id] = []
    
    chat_history = conversation_sessions[session_id]
    
    # Store user input in history
    chat_history.append({"role": "user", "content": user_input})
    chat_history = chat_history[-MAX_HISTORY:]  # Keep last 10 messages
    
    # Extract contact information from current message
    contact_info = extract_contact_info(user_input)
    
    # Check if this message contains contact details
    if has_contact_details(contact_info):
        try:
            # Generate lead summary
            lead_summary = generate_lead_summary(chat_history, contact_info)
            
            # Prepare lead data
            lead_email = contact_info.get('email', 'Not provided')
            lead_phone = contact_info.get('phone', 'Not provided')
            lead_name = contact_info.get('name', 'Website Visitor')
            
            # Run both functions to save lead
            save_lead_to_gsheet(
                name="MarketFlow AI Lead",
                email=lead_email,
                phone=lead_phone,
                message=f"{lead_name}: {lead_summary}"
            )
            
            send_lead_to_slack(
                name="MarketFlow AI Lead",
                email=lead_email,
                phone=lead_phone,
                message=f"{lead_name}: {lead_summary}"
            )
            
            print(f"✅ Lead captured: {lead_name} ({lead_email}, {lead_phone})")
            
        except Exception as e:
            print(f"❌ Error saving lead: {e}")
    
    # Build messages for OpenAI
    messages = [
        {"role": "system", "content": ASSISTANT_PERSONA},
        {"role": "system", "content": f"Website context: {website_context}"}
    ] + chat_history

    # Call OpenAI
    try:
        resp = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=messages,
            max_tokens=512,
            temperature=0.2,
        )

        assistant_text = resp.choices[0].message.content.strip()
        
        # Store assistant reply in history
        chat_history.append({"role": "assistant", "content": assistant_text})
        chat_history = chat_history[-MAX_HISTORY:]
        
        # Update session
        conversation_sessions[session_id] = chat_history
        
        return assistant_text
        
    except Exception as e:
        print(f"❌ Error with OpenAI API: {e}")
        return "I apologize, but I'm experiencing technical difficulties. Please try again in a moment or contact our support team directly."

# Flask routes
@app.route('/')
def index():
    """Serve the marketing website."""
    # Read the HTML file content (you would save the HTML artifact as a separate file)
    # For now, returning a simple response
    with open(r'templates\marketing_website.html', 'r') as f:
        return f.read()

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    """Handle chatbot conversations."""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')  # Could use session IDs for multiple users
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get response from chatbot
        response = chat_assistant(user_message, session_id)
        
        return jsonify({
            'response': response,
            'status': 'success'
        })
        
    except Exception as e:
        print(f"❌ Error in chat endpoint: {e}")
        return jsonify({
            'error': 'Internal server error',
            'response': 'I apologize, but I\'m experiencing technical difficulties. Please try again in a moment.'
        }), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'MarketFlow AI Chatbot'})

# === Development server ===
if __name__ == "__main__":
    print("🤖 MarketFlow AI Chatbot Server Starting...")
    print("🌐 Website will be available at: http://localhost:5000")
    print("💬 Chatbot API endpoint: http://localhost:5000/chat")
    print("📊 Health check: http://localhost:5000/health")
    print("\n--- Configuration ---")
    print(f"OpenAI Model: {os.getenv('OPENAI_MODEL', 'gpt-4o-mini')}")
    print(f"Max History: {MAX_HISTORY} messages")
    print("Contact Detection: Email, Phone, Name patterns")
    print("Lead Integration: Google Sheets + Slack")
    print("-" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)