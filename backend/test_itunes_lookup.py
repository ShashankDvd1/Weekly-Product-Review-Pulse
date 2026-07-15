import requests

ids = {
    "zepto": "1575323645",
    "blinkit": "960335206",
    "swiggy": "989540920"
}

for name, app_id in ids.items():
    print(f"\n--- Lookup {name} (ID: {app_id}) ---")
    for country in ["us", "in"]:
        url = f"https://itunes.apple.com/lookup?id={app_id}&country={country}"
        try:
            r = requests.get(url)
            data = r.json()
            results = data.get("results", [])
            if results:
                track = results[0]
                print(f"[{country}] Found: {track.get('trackName')} | Primary Category: {track.get('primaryGenreName')}")
            else:
                print(f"[{country}] Not found")
        except Exception as e:
            print(f"[{country}] Failed: {e}")
            
    # Also fetch RSS directly and print top level keys or entry preview
    for country in ["us", "in"]:
        url = f"https://itunes.apple.com/{country}/rss/customerreviews/id={app_id}/sortBy=mostRecent/page=1/json"
        try:
            r = requests.get(url)
            data = r.json()
            feed = data.get("feed", {})
            entries = feed.get("entry", [])
            print(f"[{country}] RSS entries: {len(entries)}")
            if entries and isinstance(entries, list):
                print(f"  First entry title: {entries[0].get('title', {}).get('label')}")
            elif entries:
                print(f"  Single entry: {entries.get('title', {}).get('label') if isinstance(entries, dict) else type(entries)}")
        except Exception as e:
            print(f"[{country}] RSS Failed: {e}")
