import requests

keywords = ["Zepto", "Blinkit", "Swiggy"]

for keyword in keywords:
    print(f"\n--- Searching for: {keyword} ---")
    url = f"https://itunes.apple.com/search?term={keyword}&country=in&entity=software&limit=5"
    try:
        r = requests.get(url)
        data = r.json()
        results = data.get("results", [])
        print(f"Results found: {len(results)}")
        for idx, track in enumerate(results):
            print(f"  [{idx + 1}] Name: {track.get('trackName')} | ID: {track.get('trackId')} | Artist: {track.get('artistName')} | Bundle ID: {track.get('bundleId')}")
    except Exception as e:
        print(f"Failed to search: {e}")
