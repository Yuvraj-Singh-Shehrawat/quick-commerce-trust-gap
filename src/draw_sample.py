"""Draw the labelling sample (seeded, so it is reproducible).

- every FirstClub 1-2 star review with >= 25 characters of text (385)
- 300 random 1-2 star reviews (>= 25 chars) for each of Blinkit, Zepto, Instamart, BigBasket
- 300 random FirstClub 4-5 star reviews (>= 25 chars), to learn what fans praise

    python src/draw_sample.py   -> data/sample_to_label.csv
"""
import numpy as np
import pandas as pd

df = pd.read_csv("data/play_reviews_2026-10-24.csv.gz")
df["text"] = df.text.fillna("").str.replace(r"\s+", " ", regex=True).str.strip()
df = df[df.text.str.len() >= 25]

neg = df[df.score <= 2]
parts = [neg[neg.app == "FirstClub"]]
for app in ["Blinkit", "Zepto", "Instamart", "BigBasket"]:
    parts.append(neg[neg.app == app].sample(n=300, random_state=42))
negs = pd.concat(parts).assign(set="negative")
pos = df[(df.app == "FirstClub") & (df.score >= 4)].sample(n=300, random_state=42).assign(set="firstclub_positive")

s = pd.concat([negs, pos]).reset_index(drop=True)
s["sid"] = np.arange(1, len(s) + 1)
s[["sid", "set", "app", "review_id", "score", "date", "text"]].to_csv("data/sample_to_label.csv", index=False)
print(s.groupby(["set", "app"]).size())
