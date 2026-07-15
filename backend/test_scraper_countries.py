from google_play_scraper import reviews, Sort
import requests

apps = {
    "zepto": "com.zeptoconsumerapp",
    "blinkit": "com.grofers.customerapp",
    "swiggy": "in.swiggy.android"
}

for name, package in apps.items():
    print(f"\n--- Testing {name} ({package}) ---")
    for country in ["us", "in"]:
        try:
            result, token = reviews(
                package,
                lang="en",
                country=country,
                sort=Sort.NEWEST,
                count=10
            )
            print(f"[{country}] Play Store count: {len(result)}")
        except Exception as e:
            print(f"[{country}] Play Store failed: {e}")

    for country in ["us", "in"]:
        app_store_ids = {
            "zepto": "1583093233",
            "blinkit": "1440073587",
            "swiggy": "989540920"
        }
        app_id = app_store_ids[name]
        try:
            url = f"https://itunes.apple.com/{country}/rss/customerreviews/id={app_id}/sortBy=mostRecent/page=1/json"
            response = requests.get(url)
            data = response.json()
            entries = data.get('feed', {}).get('entry', [])
            # Subtract 1 if the app metadata entry is present
            count = len(entries)
            print(f"[{country}] App Store count: {count}")
        except Exception as e:
            print(f"[{country}] App Store failed: {e}")
