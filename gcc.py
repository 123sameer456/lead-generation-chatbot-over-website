import gspread
from oauth2client.service_account import ServiceAccountCredentials

def save_lead_to_gsheet(name, email, phone, message):
    """
    Save a lead into Google Sheets.
    Just call this function with name, email, phone, and message.
    """
    try:
        # Define scope
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        # Load credentials
        creds = ServiceAccountCredentials.from_json_keyfile_name("gcc.json", scope)
        client = gspread.authorize(creds)

        # Open sheet by ID
        sheet = client.open_by_key("1KUz9ACDwJYra59659GdDQucbfHk3hvJciY_NifSwmkc").sheet1

        # Append row
        sheet.append_row([name, email, phone, message])

        msg = f"✅ Lead saved: {name}, {email}, {phone}, {message}"
        print(msg)
        return msg

    except Exception as e:
        error_msg = f"❌ Error saving lead: {e}"
        print(error_msg)
        return error_msg
