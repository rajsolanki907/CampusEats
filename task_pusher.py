import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/tasks']

def get_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('tasks', 'v1', credentials=creds)

def add_task(title, notes):
    service = get_service()
    
    # Set the reminder for 9:00 AM tomorrow
    tomorrow = datetime.now() + timedelta(days=1)
    due_time = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0).isoformat() + "Z"

    task = {
        'title': title,
        'notes': notes,
        'due': due_time  # This tells Google WHEN to remind you
    }
    
    result = service.tasks().insert(tasklist='@default', body=task).execute()
    print(f"Success! Task created for tomorrow at 9 AM: {result['title']}")
   
if __name__ == '__main__':
    add_task(
        "Campus Eats - Day 8: Order System & Relationships", 
        "Task: 1. Create an Order model in models.py. 2. Build a POST /orders/ route to handle transactions. 3. Update schemas to include Order information."
    )