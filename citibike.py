import datetime
import json
import os
import requests

URL = "https://gbfs.citibikenyc.com/gbfs/en/station_status.json"

response = requests.get(URL)
data = response.json()

timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M")
filename = f"data/citibike_{timestamp}.json"

os.makedirs("data", exist_ok=True)
with open(filename, "w") as f:
    json.dump(data, f, indent=2)

print(f"Saved {filename}")
