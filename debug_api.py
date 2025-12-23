import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('OPENAQ_API_KEY')
HEADERS = {'X-API-Key': API_KEY}

def debug_structure():
    # 1. Get sensors for location 1285339
    loc_id = 1285339
    url_sensors = f"https://api.openaq.org/v3/locations/{loc_id}/sensors"
    print(f"Fetching sensors: {url_sensors}")
    
    resp = requests.get(url_sensors, headers=HEADERS)
    if resp.status_code != 200:
        print(f"Error fetching sensors: {resp.status_code} {resp.text}")
        return

    sensors = resp.json().get('results', [])
    if not sensors:
        print("No sensors found.")
        return

    # 2. Pick first sensor
    sensor_id = sensors[0]['id']
    parameter = sensors[0]['parameter']['name']
    print(f"Testing Sensor ID: {sensor_id} ({parameter})")

    # 3. Get measurements
    url_meas = f"https://api.openaq.org/v3/sensors/{sensor_id}/measurements"
    params = {'limit': 1}
    print(f"Fetching measurements: {url_meas}")
    
    resp_m = requests.get(url_meas, headers=HEADERS, params=params)
    if resp_m.status_code != 200:
        print(f"Error fetching measurements: {resp_m.status_code} {resp_m.text}")
        return

    results = resp_m.json().get('results', [])
    if results:
        print("\n--- RAW MEASUREMENT OBJECT ---")
        print(json.dumps(results[0], indent=2))
        print("------------------------------")
    else:
        print("No measurements found.")

if __name__ == "__main__":
    debug_structure()
