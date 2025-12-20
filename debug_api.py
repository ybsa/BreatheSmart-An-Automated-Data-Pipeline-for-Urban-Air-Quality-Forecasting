"""
Debug script to test OpenAQ API v3 connection with API key
"""
import requests
import json
import os
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
API_KEY = os.getenv('OPENAQ_API_KEY')

print("=" * 80)
print("Testing OpenAQ API v3 Connection")
print("=" * 80)
print(f"\n🔑 API Key loaded: {'✅ Yes' if API_KEY else '❌ No'}")
if API_KEY:
    print(f"    Key preview: {API_KEY[:20]}...")

# v3 endpoint
url = "https://api.openaq.org/v3/measurements"
params = {
    "locations_name": "Abu Dhabi",
    "parameters_id": 2,  # 2 = PM2.5
    "limit": 5
}

# Add API key to headers
headers = {}
if API_KEY:
    headers['X-API-Key'] = API_KEY

print(f"\n🔗 Request URL: {url}")
print(f"📋 Parameters: {json.dumps(params, indent=2)}")
print(f"🔐 Headers: {'X-API-Key present' if headers else 'No headers'}")

try:
    print("\n⏳ Sending request...")
    response = requests.get(url, params=params, headers=headers, timeout=30)
    
    print(f"\n📊 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ SUCCESS! Received data:")
        print(f"   - Results count: {len(data.get('results', []))}")
        
        if data.get('results'):
            print(f"\n📝 First result sample:")
            result = data['results'][0]
            print(f"   - Location: {result.get('location', {}).get('name', 'N/A')}")
            print(f"   - Value: {result.get('value')} {result.get('parameter', {}).get('units', 'µg/m³')}")
            print(f"   - DateTime: {result.get('datetime')}")
            print(f"\n✅ API Connection Working!")
        else:
            print("\n⚠️  No results in response")
            print(f"Full response: {json.dumps(data, indent=2)[:500]}")
    else:
        print(f"\n❌ Request failed with status {response.status_code}")
        print(f"Response body: {response.text[:500]}")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

