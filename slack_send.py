import requests
import os


# slack : 
# Better: load from .env
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/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")

def send_lead_to_slack(name, email, phone, message):
    """
    Send lead details to Slack channel via webhook.
    """
    payload = {
        "text": (
            f"📢 *New Lead Captured!*\n"
            f"*Name:* {name}\n"
            f"*Email:* {email}\n"
            f"*Phone:* {phone}\n"
            f"*Message:* {message}"
        )
    }

    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)
        if response.status_code == 200:
            print("✅ Lead sent to Slack!")
            return True
        else:
            print(f"❌ Failed to send to Slack: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


# print(send_lead_to_slack("ali abdullah", "ali@example.com", "+324323432", "Interested in demo"))