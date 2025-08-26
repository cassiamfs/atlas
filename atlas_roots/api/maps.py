import requests
import time

API_KEY = "AIzaSyBQRAvd5FhEr31_0lrMju_HA85pRoO6kRw"

def fetch_place_details(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,rating,formatted_address,types,review,website",
        "key": API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()

    if data.get("status") == "OK":
        return data["result"]
    else:
        print(f"Error fetching {place_id}: {data.get('status')}")
        return None

place_ids = [
    "ChIJN1t_tDeuEmsRUsoyG83frY4",  # Examples      
    "ChIJD7fiBh9u5kcRYJSMaMOCCwQ"
]

results = []

for pid in place_ids:
    details = fetch_place_details(pid)
    if details:
        results.append(details)
    time.sleep(0.2)  # avoid hitting rate limits (50 req/sec max)

for place in results:
    print("Name:", place.get("name"))
    print("Address:", place.get("formatted_address"))
    print("Rating:", place.get("rating"))
    print("Types:", place.get("types"))

    if "reviews" in place:
        for r in place["reviews"][:3]:  # show first 3 reviews
            print(" - Review:", r["text"])
    print("="*40)
