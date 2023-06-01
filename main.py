import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from mailer import Mailer


SERVICE_ACCOUNT_FILE = 'service-account.json'
SPREADSHEET_ID = os.getenv('AJK_SPREADSHEET_PELATIHAN_DOCKER_ID')
MAIN_EMAIL = os.getenv('MAIN_EMAIL')
MAIN_EMAIL_PASSWORD = os.getenv('MAIN_EMAIL_PASSWORD')
SHARED_EMAIL = os.getenv('SHARED_EMAIL')

if __name__ == "__main__":
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
    
    service = build('sheets', 'v4', credentials=creds)
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range='sheet1!A:C'
        ).execute()

    header = result['values'][0]
    column_nrp = header.index('NRP')
    column_fullname = header.index('Fullname')
    column_email = header.index('Email')
    recipients = []

    values = result.get('values', [])
    for row in values[1:] :
        recipient_nrp = row[column_nrp]
        recipient_fullname = row[column_fullname]
        recipient_email = row[column_email]

        if not recipient_nrp or not recipient_fullname or not recipient_email :
            continue

        recipient = {"nrp": recipient_nrp, "fullname" : recipient_fullname, "email": recipient_email}
        recipients.append(recipient)
    
    mailer = Mailer(MAIN_EMAIL, MAIN_EMAIL_PASSWORD, SHARED_EMAIL)
    mailer.send_email_concurrently(recipients)