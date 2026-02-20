import gspread
from google.oauth2.credentials import Credentials as UserCredentials
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
import json
import pickle
from googleapiclient.discovery import build

def get_file_path(filename):
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, filename)

json_path = get_file_path('token.json')

def get_cleaned_creds():
    """Fixes formatting issues in credentials.json automatically."""
    with open("credentials.json", "r") as f:
        info = json.load(f)
    
    # Fix potential newline/formatting issues in the private key
    info["private_key"] = info["private_key"].replace("\\n", "\n")
    
    SHEET_SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    return Credentials.from_service_account_info(info, scopes=SHEET_SCOPE)

# --- SETUP ---
# 1. Modern Sheets Credentials
SHEET_SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds_sheet = Credentials.from_service_account_file(get_file_path("credentials.json"), scopes=SHEET_SCOPE)
client = gspread.authorize(creds_sheet)
sheet = client.open("CampusEats_Roadmap").sheet1

# 2. Tasks Credentials (Using your existing token.pickle)
def get_tasks_service():
    base_path = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_path, 'token.json') 
    
    if os.path.exists(json_path):
        # Load the user credentials from token.json
        creds_tasks = UserCredentials.from_authorized_user_file(json_path)
        
        # If the token is expired, you might need to refresh it (handled by the library)
        return build('tasks', 'v1', credentials=creds_tasks)
    
    print(f"Debug: Looking for token.json at {json_path}")
    return None

def push_to_iphone(content):
    service = get_tasks_service()
    if not service:
        print("Error: token.pickle not found.")
        return

    task_body = {
        'title': f"📍 GOALS: {datetime.now().strftime('%d %b')}",
        'notes': content
    }
    service.tasks().insert(tasklist='@default', body=task_body).execute()

def process_daily_schedule():
    # Use today's date: 2026-01-27
    today = datetime.now().strftime("%Y-%m-%d")
    records = sheet.get_all_records()
    
    for i, row in enumerate(records):
        # We look for today's date and check if it's already been pushed
        if str(row['Date']) == today and row['Status'] != "Pushed":
            dev = row['Dev_Task']
            dsa = row['DSA_Task']
            goal = row['Goal/Objective']
            
            full_task = f"🛠 DEV: {dev}\n\n📚 DSA: {dsa} : 🎯 GOAL: {goal}"
            
            print(f"Syncing today's tasks for {today}...")
            push_to_iphone(full_task)
            
            # Update Status in column 4 (D)
            sheet.update_cell(i + 2, 4, "Pushed")
            print("✅ Successfully pushed to iPhone and updated Sheet.")
            return

    print(f"No new tasks found for {today}.")

if __name__ == "__main__":
    process_daily_schedule()