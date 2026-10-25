"""Collect the newest public Google Play reviews for five Indian grocery apps.

    pip install google-play-scraper pandas
    python src/collect_reviews.py         -> data/play_reviews_<date>.csv.gz

The shipped dataset (data/play_reviews_2026-10-24.csv.gz, 26,205 reviews) was pulled on
24 Oct 2026 from the same public Play Store review endpoint this library uses, sorted by newest,
language en, country IN. Re-running will give a newer window. No reviewer names or IDs are kept.
"""
import datetime as dt

import pandas as pd
from google_play_scraper import Sort, reviews

APPS = {
    "FirstClub": ("com.firstclub.app", 12000),          # all written reviews (~2,200)
    "Blinkit": ("com.grofers.customerapp", 6000),
    "Zepto": ("com.zeptoconsumerapp", 6000),
    "Instamart": ("in.swiggy.android.instamart", 6000),
    "BigBasket": ("com.bigbasket.mobileapp", 6000),
}


def collect(package: str, max_n: int) -> list:
    out, token = [], None
    while len(out) < max_n:
        batch, token = reviews(package, lang="en", country="in", sort=Sort.NEWEST,
                               count=min(200, max_n - len(out)), continuation_token=token)
        out.extend(batch)
        if not batch or token is None or token.token is None:
            break
    return out


def main():
    rows = []
    for app, (pkg, n) in APPS.items():
        for r in collect(pkg, n):
            rows.append({"app": app, "package": pkg, "review_id": r["reviewId"], "score": r["score"],
                         "date": r["at"], "text": r["content"], "thumbs_up": r["thumbsUpCount"],
                         "app_version": r.get("reviewCreatedVersion"), "has_dev_reply": bool(r.get("replyContent"))})
        print(f"{app:10s} {sum(1 for x in rows if x['app'] == app):>6,}")
    path = f"data/play_reviews_{dt.date.today().isoformat()}.csv.gz"
    pd.DataFrame(rows).to_csv(path, index=False, compression="gzip")
    print("saved", path)


if __name__ == "__main__":
    main()
