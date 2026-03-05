import time
import schedule
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from slack_sdk import WebClient
import os

SLACK_TOKEN = os.environ["SLACK_BOT_TOKEN"]
CHANNEL_ID = os.environ["SLACK_CHANNEL_ID"]

client = WebClient(token=SLACK_TOKEN)

scope = [
 "https://spreadsheets.google.com/feeds",
 "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
gs = gspread.authorize(creds)

sheet = gs.open("Криты, настройка ботов").worksheet("Криты КЦ")

seen_values = set()

def check_sheet():

    global seen_values

    values = sheet.col_values(1)

    new_values = [v for v in values if v not in seen_values and v.strip() != ""]

    for value in new_values:

        client.chat_postMessage(
            channel=CHANNEL_ID,
            text=f"Новое значение: {value}"
        )

    seen_values.update(new_values)


schedule.every(5).minutes.do(check_sheet)

print("Bot started")

while True:
    schedule.run_pending()
    time.sleep(5)
