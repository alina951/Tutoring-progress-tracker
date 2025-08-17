import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# --- Step 1: Connect to Google Sheets ---
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# 🔑 Path to your service account JSON
SERVICE_ACCOUNT_FILE = "C:/Users/alina/Downloads/tutoring-progress-tracker-2e27e2045c7c.json"

creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
client = gspread.authorize(creds)

# --- Step 2: Open your Google Sheet by URL ---
# Replace with your actual Google Sheet URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/1sWBmkxobJp-mdwe2f9SOZPI8QgU_w_QMYpwUNIUvHW8/edit?resourcekey=&gid=637618865#gid=637618865"
sheet = client.open_by_url(SHEET_URL).sheet1  # first sheet

# --- Step 3: Load Data into Pandas ---
data = sheet.get_all_records()
df = pd.DataFrame(data)

# --- Step 4: Clean the "Homework scored (%)" column ---
df["Homework scored (%)"] = df["Homework scored (%)"].astype(str).str.replace("%", "").astype(float)

# --- Step 5: Group by Student and Calculate Average ---
avg_scores = df.groupby("Student Name/Year")["Homework scored (%)"].mean().reset_index()

# Apply flagging rule
avg_scores["Flag"] = avg_scores["Homework scored (%)"].apply(
    lambda x: "Green ✅" if x >= 85 else "Red ❌"
)

# --- Step 6: Write results to a NEW SHEET called "Flags" ---
try:
    flag_sheet = client.open_by_url(SHEET_URL).worksheet("Flags")
except gspread.exceptions.WorksheetNotFound:
    flag_sheet = client.open_by_url(SHEET_URL).add_worksheet(title="Flags", rows="100", cols="20")

# Clear old content
flag_sheet.clear()

# Upload results
flag_sheet.update([avg_scores.columns.values.tolist()] + avg_scores.values.tolist())

print("✅ Flags successfully written to 'Flags' tab in your Google Sheet!")
