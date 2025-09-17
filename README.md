
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


# MarketFlow AI - Marketing Agency Website with Chatbot

This is a complete marketing agency website with an integrated AI chatbot that automatically captures leads and integrates with Google Sheets and Slack.

## Features

### Website Features
- ✅ Modern, responsive marketing agency website
- ✅ 6 comprehensive marketing services with CTAs
- ✅ Professional design with animations and gradients  
- ✅ Mobile-responsive layout
- ✅ Smooth scrolling navigation
- ✅ Contact sections with clear CTAs

### Chatbot Features
- ✅ AI-powered chatbot (OpenAI GPT-4o-mini)
- ✅ Contextual responses based on website content
- ✅ Automatic contact information extraction (email, phone, name)
- ✅ Conditional lead capture - only triggers when contact details are detected
- ✅ Google Sheets integration for lead storage
- ✅ Slack notifications for new leads
- ✅ Conversation memory (last 10 messages)
- ✅ Professional sales-focused persona

## Requirements

Create a `requirements.txt` file with the following:

```
flask==2.3.3
openai==1.3.5
python-dotenv==1.0.0
requests==2.31.0
```

## Setup Instructions

### 1. Environment Variables
Create a `.env` file in your project root:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Google Sheets API (if using service account)
GOOGLE_SHEETS_CREDENTIALS_PATH=path/to/your/credentials.json
GOOGLE_SHEET_ID=your_google_sheet_id

# Slack Configuration  
SLACK_WEBHOOK_URL=your_slack_webhook_url_here
SLACK_CHANNEL=#leads

# Optional: Custom configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

### 2. File Structure
```
project_folder/
├── app.py                 # Main Flask application (enhanced chatbot code)
├── marketing_website.html # Website HTML (save the HTML artifact)
├── gcc.py                 # Google Sheets integration
├── slack_send.py          # Slack integration  
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
└── static/               # Static files (if needed)
```

### 3. Save the Website
Save the HTML artifact as `marketing_website.html` in your project folder.

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the Application
```bash
python app.py
```

The website will be available at: `http://localhost:5000`

## How It Works

### Contact Detection & Lead Capture

The chatbot automatically detects contact information using regex patterns:

**Email Detection:**
- `user@example.com`
- `contact.person@company.co.uk`

**Phone Detection:**
- `123-456-7890`
- `(123) 456-7890`
- `123.456.7890`
- `1234567890`
- `+1 234 567 8900`

**Name Detection:**
- "I'm John Smith"
- "My name is Sarah Johnson"  
- "This is Mike Wilson"

### Automatic Lead Processing

When contact details are detected, the system:

1. ✅ Extracts email, phone, and name
2. ✅ Generates conversation summary
3. ✅ Calls `save_lead_to_gsheet()` function
4. ✅ Calls `send_lead_to_slack()` function
5. ✅ Continues conversation naturally

### System Prompt Optimization

The chatbot is configured with:
- **Company Context:** MarketFlow AI marketing agency
- **Services Knowledge:** All 6 marketing services from website
- **Sales Focus:** Qualifying leads and scheduling consultations
- **Professional Tone:** Expert marketing consultant persona
- **Lead Qualification:** Asks relevant business questions before capturing contact details

## Testing the Chatbot

### Test Messages for Lead Capture:

**Email Test:**
```
"Hi, I'm interested in your chatbot services. You can reach me at john@company.com"
```

**Phone Test:**
```  
"I'd like to schedule a demo. My number is (555) 123-4567"
```

**Combined Test:**
```
"Hi, I'm Sarah Johnson from ABC Marketing. We need help with lead generation. 
Email: sarah@abcmarketing.com, Phone: 555-987-6543"
```

### Expected Behavior:
- ✅ Chatbot responds professionally about services
- ✅ Lead data automatically saved to Google Sheets
- ✅ Slack notification sent to your team
- ✅ Console shows "✅ Lead captured: [Name] ([Email], [Phone])"

## Customization

### Update Company Information:
Edit the `website_context` dictionary in `app.py`:

```python
website_context = {
    'company_name': 'Your Company Name',
    'services': ['Your services here'],
    'about': 'Your company description'
}
```

### Modify Contact Detection:
Add custom patterns to `extract_contact_info()` function for:
- LinkedIn profiles  
- Company names
- Specific form fields
- Custom contact formats

### Enhance Lead Qualification:
Update `ASSISTANT_PERSONA` to ask specific qualifying questions:
- Budget range
- Timeline
- Company size  
- Specific pain points
- Decision-making process

## Deployment

### Production Considerations:
- Use a production WSGI server (Gunicorn)
- Set up proper logging
- Configure rate limiting  
- Add input validation and sanitization
- Use session management for multiple users
- Set up monitoring and error tracking

### Example Production Start:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

This setup gives you a complete marketing agency website with intelligent lead capture that automatically integrates with your existing Google Sheets and Slack workflows!

----
# End of files
