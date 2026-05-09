import datetime
import json
import os
import requests

DATASET_ID = 358 # Electricity consumption in Finland, hourly data
DAYS_AGO = 7
API_KEY = os.environ["FINGRID_API_KEY"]

today = datetime.datetime.now(datetime.timezone.utc).date()
day = today - datetime.timedelta(days=DAYS_AGO)
next_day = day + datetime.timedelta(days=1)

url = f"https://data.fingrid.fi/api/datasets/{DATASET_ID}/data"
params = {
    "startTime": f"{day}T00:00:00Z",
    "endTime":   f"{next_day}T00:00:00Z",
    "pageSize": 20000
}

response = requests.get(url, headers={"x-api-key": API_KEY}, params=params)
data = response.json()

filename = f"data/fingrid_{day}.json"

os.makedirs("data", exist_ok=True)
with open(filename, "w") as f:
    json.dump(data, f, indent=2)

print(f"Saved {filename}")
