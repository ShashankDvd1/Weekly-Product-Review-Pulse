from google_play_scraper import reviews, Sort
import requests

try:
    print("Testing Play Store scraper...")
    result, token = reviews(
        "com.kiranacheckout.customer",
        lang="en",
        country="in",
        sort=Sort.NEWEST,
        count=10
    )
    print(f"Play Store result count: {len(result)}")
    if result:
        print(f"Play Store sample date: {result[0].get('at')}")
except Exception as e:
    print(f"Play Store failed: {e}")

try:
    print("\nTesting App Store RSS...")
    url = "https://itunes.apple.com/in/rss/customerreviews/id=1575323757/sortBy=mostRecent/page=1/json"
    response = requests.get(url)
    print(f"App Store status: {response.status_code}")
    data = response.json()
    entries = data.get('feed', {}).get('entry', [])
    print(f"App Store entries: {len(entries)}")
    if entries:
        print(f"App Store sample: {entries[0].get('updated', {}).get('label')}")
except Exception as e:
    print(f"App Store failed: {e}")
