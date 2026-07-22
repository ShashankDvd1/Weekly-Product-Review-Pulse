import sys

with open('backend/agents/orchestrator.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_collect_all = '''    def collect_all(
        self,
        apps: list[str] = None,
        play_store_package: str = None,
        app_store_id: str = None,
        from_date: str = None,
        to_date: str = None,
        include_reddit: bool = True,
        reddit_subreddits: list[str] = None,
        reddit_search_terms: list[str] = None,
    ) -> list[UnifiedSignal]:
        """
        Collect data, deduplicate, and run the Intelligent Review Quality Filter.
        If valid genuine reviews < target, dynamically expand the date range and retry.
        """
        if apps is None:
            apps = ["zepto", "blinkit", "swiggy_instamart"]

        if (play_store_package or app_store_id) and apps == ["zepto", "blinkit", "swiggy_instamart"]:
            apps = []

        if not from_date or not to_date:
            from datetime import datetime
            from_date = "2024-01-01"
            to_date = datetime.now().strftime("%Y-%m-%d")

        TARGET_GENUINE_REVIEWS = 150
        MAX_RETRIES = 2
        
        current_from_date = from_date
        current_to_date = to_date
        
        self.collection_results = []
        self._progress = []
        all_signals = []
        
        from core.schemas import QualityCategory
        
        for attempt in range(MAX_RETRIES + 1):
            self._log_progress(f"\\n🚀 Collection Attempt {attempt + 1}/{MAX_RETRIES + 1} (From: {current_from_date} To: {current_to_date})")
            batch_signals = []
            
            # 1. Custom app targets
            if play_store_package or app_store_id:
                app_name = "Custom Target"
                if play_store_package:
                    try:
                        self._log_progress(f"📱 Collecting Play Store reviews for custom package: {play_store_package}...")
                        df_play = fetch_play_store_reviews(play_store_package, current_from_date, current_to_date, max_reviews=300)
                        if not df_play.empty:
                            df_play["content"] = df_play["content"].apply(scrub_pii_from_text)
                            normalized = normalize_play_store_reviews(df_play, app_name, play_store_package)
                            batch_signals.extend(normalized)
                            self._log_progress(f"  ✅ {len(normalized)} custom Play Store reviews")
                    except Exception as e:
                        self._log_progress(f"  ❌ Play Store error for {play_store_package}: {str(e)[:100]}")

                if app_store_id:
                    try:
                        self._log_progress(f"🍎 Collecting App Store reviews for custom ID: {app_store_id}...")
                        df_app = fetch_app_store_reviews(app_store_id, current_from_date, current_to_date, max_pages=4)
                        if not df_app.empty:
                            df_app["content"] = df_app["content"].apply(scrub_pii_from_text)
                            normalized = normalize_app_store_reviews(df_app, app_name, app_store_id)
                            batch_signals.extend(normalized)
                            self._log_progress(f"  ✅ {len(normalized)} custom App Store reviews")
                        else:
                            self._log_progress(f"  ⚠️ 0 App Store reviews found in selected date range for custom ID: {app_store_id}")
                    except Exception as e:
                        self._log_progress(f"  ❌ App Store error for {app_store_id}: {str(e)[:100]}")

            # 2. Registered catalog apps
            if apps:
                for app_key in apps:
                    app_config = QUICK_COMMERCE_APPS.get(app_key)
                    if not app_config:
                        continue
                    app_name = app_config["name"]
                    package = app_config["play_store_package"]
                    app_store_id_reg = app_config["app_store_id"]

                    try:
                        self._log_progress(f"📱 Collecting Play Store reviews for {app_name}...")
                        df_play = fetch_play_store_reviews(package, current_from_date, current_to_date, max_reviews=300)
                        if not df_play.empty:
                            df_play["content"] = df_play["content"].apply(scrub_pii_from_text)
                            normalized = normalize_play_store_reviews(df_play, app_name, package)
                            batch_signals.extend(normalized)
                            self._log_progress(f"  ✅ {len(normalized)} Play Store reviews for {app_name}")
                    except Exception as e:
                        self._log_progress(f"  ❌ Play Store error for {app_name}: {str(e)[:100]}")

                    try:
                        self._log_progress(f"🍎 Collecting App Store reviews for {app_name}...")
                        df_app = fetch_app_store_reviews(app_store_id_reg, current_from_date, current_to_date, max_pages=4)
                        if not df_app.empty:
                            df_app["content"] = df_app["content"].apply(scrub_pii_from_text)
                            normalized = normalize_app_store_reviews(df_app, app_name, app_store_id_reg)
                            batch_signals.extend(normalized)
                            self._log_progress(f"  ✅ {len(normalized)} App Store reviews for {app_name}")
                        else:
                            self._log_progress(f"  ⚠️ 0 App Store reviews found in selected date range for {app_name}")
                    except Exception as e:
                        self._log_progress(f"  ❌ App Store error for {app_name}: {str(e)[:100]}")

            # 3. Reddit Ingestion
            if include_reddit:
                try:
                    self._log_progress(f"🔴 Collecting Reddit discussions...")
                    reddit_signals = collect_reddit_data(
                        subreddits=reddit_subreddits,
                        search_terms=reddit_search_terms,
                    )
                    if reddit_signals:
                        for sig in reddit_signals:
                            sig["content"] = scrub_pii_from_text(sig["content"])
                        normalized = normalize_reddit_data(reddit_signals)
                        batch_signals.extend(normalized)
                        self._log_progress(f"  ✅ {len(normalized)} Reddit signals collected")
                except Exception as e:
                    self._log_progress(f"  ❌ Reddit error: {str(e)[:100]}")
            
            all_signals.extend(batch_signals)
            
            self._log_progress(f"🔄 Deduplicating {len(all_signals)} cumulative signals...")
            from processing.deduplication import semantic_deduplicate
            unique_signals = semantic_deduplicate(all_signals)
            self._log_progress(f"✅ Current unique dataset: {len(unique_signals)} signals")
            
            self._log_progress(f"🧠 Running Intelligent Quality Filter on {len(unique_signals)} reviews...")
            from reasoning.quality_filter import assess_review_quality_batch
            assessed_signals = assess_review_quality_batch(unique_signals)
            
            accepted_signals = [
                s for s in assessed_signals 
                if getattr(s, 'quality_category', QualityCategory.DISCARD) in [
                    QualityCategory.MEDIUM_SIGNAL, 
                    QualityCategory.HIGH_SIGNAL, 
                    QualityCategory.GOLD_INSIGHT
                ]
            ]
            
            self._log_progress(f"🏆 Accepted high-signal genuine reviews: {len(accepted_signals)}")
            
            if len(accepted_signals) >= TARGET_GENUINE_REVIEWS:
                self.signals = accepted_signals
                self._log_progress(f"✅ Reached target of {TARGET_GENUINE_REVIEWS} genuine reviews. Proceeding to analysis.")
                break
            elif attempt < MAX_RETRIES:
                self._log_progress(f"⚠️ Only {len(accepted_signals)} valid reviews found (Target: {TARGET_GENUINE_REVIEWS}). Expanding date range backward...")
                try:
                    from datetime import datetime
                    import datetime as dt
                    from_dt = datetime.strptime(current_from_date, "%Y-%m-%d")
                    new_to_dt = from_dt
                    new_from_dt = from_dt - dt.timedelta(days=90)
                    current_to_date = new_to_dt.strftime("%Y-%m-%d")
                    current_from_date = new_from_dt.strftime("%Y-%m-%d")
                except Exception as e:
                    self._log_progress("❌ Could not expand dates. Aborting retries.")
                    self.signals = accepted_signals
                    break
            else:
                self._log_progress(f"⚠️ Reached max retries. Proceeding with {len(accepted_signals)} valid reviews.")
                self.signals = accepted_signals
                
        return self.signals'''

start_idx = content.find('    def collect_all(')
end_idx = content.find('    # ── Analysis Phase ─────────────────────────')

if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + new_collect_all + '\n\n' + content[end_idx:]
    with open('backend/agents/orchestrator.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Updated successfully')
else:
    print('Could not find start or end index')
