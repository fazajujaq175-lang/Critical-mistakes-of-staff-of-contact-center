import time
import schedule
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from slack_sdk import WebClient
import json
import os

# ===== НАСТРОЙКИ =====

SLACK_TOKEN = xoxb-10404683860950-10640251679332-J6SF9GX8YsVxHOyHXqUpewVD
CHANNEL = "#криты-кц-бот"


SPREADSHEET_NAME = "Криты, настройка ботов"
WORKSHEET_NAME = "Криты КЦ"

CHECK_INTERVAL = 3  # минуты

STATE_FILE = "sent_values.json"

# ===== SLACK =====

client = WebClient(token=SLACK_TOKEN)

# ===== GOOGLE SHEETS =====

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
gc = gspread.authorize(creds)

sheet = gc.open(SPREADSHEET_NAME).worksheet(WORKSHEET_NAME)

# ===== ХРАНЕНИЕ УЖЕ ОТПРАВЛЕННЫХ =====

if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        sent_values = json.load(f)
else:
    sent_values = []

# ===== ПРОВЕРКА ТАБЛИЦЫ =====

def check_sheet():
    global sent_values

    try:
        values = sheet.col_values(1)

        new_values = []

        for value in values:
            value = value.strip()

            if value and value not in sent_values:
                new_values.append(value)

        for value in new_values:
            client.chat_postMessage(
                channel=CHANNEL,
                text=f"🚨 *Критическая ошибка:*\n{value}"
            )

            print("Отправлено:", value)

            sent_values.append(value)

        with open(STATE_FILE, "w") as f:
            json.dump(sent_values, f)

    except Exception as e:
        print("Ошибка:", e)

# ===== ПЛАНИРОВЩИК =====

schedule.every(CHECK_INTERVAL).minutes.do(check_sheet)

print("Бот запущен. Проверка каждые", CHECK_INTERVAL, "минут")

check_sheet()

while True:
    schedule.run_pending()
    time.sleep(10)

