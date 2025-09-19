import gspread
from google.oauth2.service_account import Credentials

def save_lead_to_gsheet(name, email, phone, message):
    try:
        # ✅ Updated scope (latest Google API requirement)
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

        # ✅ Use google-auth instead of oauth2client
        creds = Credentials.from_service_account_file("second.json", scopes=scope)
        client = gspread.authorize(creds)

        # ✅ Open by Google Sheet ID
        sheet = client.open_by_key("1KUz9ACDwJYra59659GdDQucbfHk3hvJciY_NifSwmkc").sheet1

        # ✅ Append new lead
        sheet.append_row([name, email, phone, message])

        msg = f"✅ Lead saved: {name}, {email}, {phone}, {message}"
        print(msg)
        return msg

    except Exception as e:
        error_msg = f"❌ Error saving lead: {e}"
        print(error_msg)
        return error_msg


# Test
# print(save_lead_to_gsheet("Sameer", "sameer@gmail.com", "23321", "test lead"))
