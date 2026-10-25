"""All tables and charts for the Quick-Commerce Trust Gap study.

    python src/keyword_baseline.py
    python src/analyze.py        -> outputs/*.csv, outputs/results.json, charts/*.png
"""
import json
import os
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.stats.proportion import proportion_confint

import vizstyle as vz

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
os.makedirs("outputs", exist_ok=True)
os.makedirs("charts", exist_ok=True)

NEG = {"Q": "Quality / freshness / expiry", "R": "Refund & support", "A": "App / tech / payments",
       "P": "Price & fees", "U": "Not serviceable in my area", "X": "Cancelled / not delivered",
       "W": "Wrong / missing items", "L": "Late delivery", "B": "Delivery partner behaviour",
       "M": "Offers / wallet / membership", "S": "Stock / selection", "O": "Other / unclear"}
POS = {"q": "Quality / freshness / taste", "k": "Packaging", "s": "Selection / curation",
       "a": "App experience", "t": "Trust: lab reports, clean label", "f": "Fast / on-time delivery",
       "p": "Price / value", "c": "Customer service", "u": "Asks to expand to their city",
       "g": "Gifts / freebies", "o": "General praise"}
COMPETITORS = ["Blinkit", "Zepto", "Instamart", "BigBasket"]

raw = pd.read_csv("data/play_reviews_2026-10-24.csv.gz", parse_dates=["date"])
lab = pd.read_csv("data/labelled_reviews.csv", parse_dates=["date"])
neg = lab[lab["set"] == "negative"].copy()
pos = lab[lab["set"] == "firstclub_positive"].copy()
res = {}


def share_ci(k, n):
    lo, hi = proportion_confint(k, n, method="wilson")
    return k / n, lo, hi


# ------------------------------------------------------------- 1. rating mix, all 26,205 reviews
mix = raw.groupby("app").agg(reviews=("score", "size"), avg_rating=("score", "mean"),
                             share_1_2_star=("score", lambda s: (s <= 2).mean()),
                             first=("date", "min"), last=("date", "max")).round(3)
mix.to_csv("outputs/rating_mix_by_app.csv")
res["rating_mix"] = mix.reset_index().assign(first=lambda d: d["first"].astype(str),
                                             last=lambda d: d["last"].astype(str)).to_dict(orient="records")

# ------------------------------------------------------------- 2. themes in negative reviews, by app
rows = []
for app, g in neg.groupby("app"):
    for c, name in NEG.items():
        k = int(g.codes.str.contains(c).sum())
        s, lo, hi = share_ci(k, len(g))
        rows.append({"app": app, "code": c, "theme": name, "n": len(g), "mentions": k,
                     "share": s, "ci_low": lo, "ci_high": hi,
                     "primary_share": float((g.primary_code == c).mean())})
comp = neg[neg.app.isin(COMPETITORS)]
for c, name in NEG.items():
    k = int(comp.codes.str.contains(c).sum())
    s, lo, hi = share_ci(k, len(comp))
    rows.append({"app": "Competitors (pooled)", "code": c, "theme": name, "n": len(comp), "mentions": k,
                 "share": s, "ci_low": lo, "ci_high": hi, "primary_share": float((comp.primary_code == c).mean())})
themes = pd.DataFrame(rows)
themes.round(4).to_csv("outputs/negative_themes_by_app.csv", index=False)
piv = themes.pivot(index="code", columns="app", values="share")
res["themes"] = piv.round(4).to_dict()

qc = themes[(themes.app == "Competitors (pooled)")].set_index("code")
res["quality_vs_late_competitors"] = {
    "quality_share": float(qc.loc["Q", "share"]), "quality_ci": [float(qc.loc["Q", "ci_low"]), float(qc.loc["Q", "ci_high"])],
    "late_share": float(qc.loc["L", "share"]), "late_ci": [float(qc.loc["L", "ci_low"]), float(qc.loc["L", "ci_high"])],
    "refund_support_share": float(qc.loc["R", "share"]),
    "ratio_quality_to_late": float(qc.loc["Q", "share"] / qc.loc["L", "share"]),
}
# "post-purchase trust failure" = quality, wrong/missing, not delivered, or refund/support
trust = lambda g: g.codes.str.contains("[QWXR]").mean()
speed = lambda g: g.codes.str.contains("L").mean()
res["trust_failure_vs_speed"] = {app: {"trust_failure": float(trust(g)), "late": float(speed(g))}
                                for app, g in neg.groupby("app")}

# ------------------------------------------------------------- 3. FirstClub: never got to a first order
fc = neg[neg.app == "FirstClub"].copy()
pre_purchase = fc.codes.map(lambda c: set(c) <= set("UAPSMO") and bool(set(c) & set("UA")))
signup_before = re.compile(r"regist|sign ?up|log ?in|number|details|question|survey|quiz|\bcart\b|otp|personal info|onboard|setup|profile", re.I)
ads = re.compile(r"\bads?\b|advert|instagram|youtube|reels?|promot|marketing|campaign", re.I)
u = fc[fc.codes.str.contains("U")]
login = fc[fc.codes.str.contains("A") & fc.text.str.contains(r"otp|log ?in|sign ?up|regist|blank screen|not (?:even )?open|doesn.?t (?:even )?open|not load|stuck", case=False, regex=True)]
res["firstclub_onboarding"] = {
    "negatives": int(len(fc)),
    "unserviceable_mentions": int(len(u)), "unserviceable_share": float(len(u) / len(fc)),
    "unserviceable_after_signup_or_cart": int(u.text.str.contains(signup_before).sum()),
    "unserviceable_mention_ads": int(u.text.str.contains(ads).sum()),
    "login_or_app_wont_open": int(len(login)), "login_or_app_wont_open_share": float(len(login) / len(fc)),
    "pre_purchase_only_share": float(pre_purchase.mean()),
    "pre_purchase_only_n": int(pre_purchase.sum()),
}
comp_pre = comp.codes.map(lambda c: set(c) <= set("UAPSMO") and bool(set(c) & set("UA"))).mean()
res["competitors_pre_purchase_only_share"] = float(comp_pre)

# ------------------------------------------------------------- 4. FirstClub trend
fca = raw[raw.app == "FirstClub"].copy()
fca["quarter"] = fca.date.dt.to_period("Q").astype(str)
trend = fca.groupby("quarter").agg(reviews=("score", "size"), avg_rating=("score", "mean"),
                                   share_1_2_star=("score", lambda s: (s <= 2).mean())).round(3)
trend.to_csv("outputs/firstclub_quarterly_rating.csv")
res["firstclub_trend"] = trend.reset_index().to_dict(orient="records")


def period(d):
    return "Jun 2025-Mar 2026" if d < pd.Timestamp("2026-04-01") else ("Apr-Jun 2026" if d < pd.Timestamp("2026-07-01") else "Jul-Oct 2026")


fca["period"] = fca.date.map(period)
fc["period"] = fc.date.map(period)
per100 = []
for p_, g in fc.groupby("period"):
    n_all = int((fca.period == p_).sum())
    for c in ["Q", "L", "R", "A", "U", "P", "X", "W"]:
        per100.append({"period": p_, "code": c, "theme": NEG[c], "all_reviews": n_all, "negatives_labelled": len(g),
                       "share_of_negatives": float(g.codes.str.contains(c).mean()),
                       "per_100_reviews": float(g.codes.str.contains(c).sum() / n_all * 100)})
per100 = pd.DataFrame(per100)
per100.round(3).to_csv("outputs/firstclub_themes_by_period.csv", index=False)
res["firstclub_per100"] = per100.pivot(index="code", columns="period", values="per_100_reviews").round(2).to_dict()

# ------------------------------------------------------------- 5. what FirstClub fans praise
praise = pd.DataFrame([{"code": c, "theme": n, "share": float(pos.codes.str.contains(c).mean())} for c, n in POS.items()])
praise.sort_values("share", ascending=False).round(4).to_csv("outputs/firstclub_praise_themes.csv", index=False)
res["praise"] = praise.set_index("code").share.round(4).to_dict()
res["praise_n"] = int(len(pos))

# ------------------------------------------------------------- 6. keyword-vs-LLM agreement (from keyword_baseline.py)
if os.path.exists("outputs/keyword_vs_llm_kappa.csv"):
    kap = pd.read_csv("outputs/keyword_vs_llm_kappa.csv")
    res["keyword_kappa"] = kap.set_index("code").cohen_kappa.to_dict()

with open("outputs/results.json", "w") as fh:
    json.dump(res, fh, indent=2, default=float)
print(json.dumps({k: res[k] for k in ["quality_vs_late_competitors", "trust_failure_vs_speed",
                                     "firstclub_onboarding", "competitors_pre_purchase_only_share",
                                     "firstclub_per100", "praise"]}, indent=2, default=float))

# ============================================================= charts
vz.setup()
SRC = "Data: Google Play reviews collected 24 Oct 2026, labelled with a 12-code codebook (prompts/codebook.md)"

# Chart 1 - quality vs refund/support vs late, competitors
fig, ax = plt.subplots(figsize=(9.6, 4.8))
series = [("Q", "Quality / freshness / expiry", vz.BLUE), ("R", "Refund & support", vz.AQUA), ("L", "Late delivery", vz.ORANGE)]
y = np.arange(len(COMPETITORS))
h = 0.24
for j, (c, name, col) in enumerate(series):
    vals = [float(piv.loc[c, a]) * 100 for a in COMPETITORS]
    ax.barh(y + (j - 1) * (h + 0.03), vals, height=h, color=col, label=name)
    for yy, v in zip(y + (j - 1) * (h + 0.03), vals):
        ax.text(v + 0.8, yy, f"{v:.0f}%", va="center", fontsize=8.8, color=vz.INK)
ax.set_yticks(y); ax.set_yticklabels(COMPETITORS); ax.invert_yaxis()
ax.set_xlim(0, 58); ax.set_xlabel("% of 1-2 star reviews mentioning the theme (300 random reviews per app)")
ax.grid(axis="y", visible=False)
ax.legend(loc="lower right", ncol=1)
r = res["quality_vs_late_competitors"]
vz.title(ax, "Shoppers complain about what arrived, not how fast it came",
         f"Pooled: quality {r['quality_share']*100:.0f}% vs late delivery {r['late_share']*100:.0f}% of negative reviews "
         f"({r['ratio_quality_to_late']:.1f}x); refund & support {r['refund_support_share']*100:.0f}%")
vz.source(fig, SRC)
fig.savefig("charts/01_quality_vs_speed.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# Chart 2 - FirstClub vs competitors theme profile
order = ["A", "R", "Q", "P", "U", "L", "X", "M", "W", "B", "S"]
fig, ax = plt.subplots(figsize=(9.6, 5.6))
y = np.arange(len(order))
h = 0.36
fcv = [float(piv.loc[c, "FirstClub"]) * 100 for c in order]
cpv = [float(piv.loc[c, "Competitors (pooled)"]) * 100 for c in order]
ax.barh(y - h / 2 - 0.02, fcv, height=h, color=vz.ORANGE, label=f"FirstClub (all {len(fc)} negative reviews)")
ax.barh(y + h / 2 + 0.02, cpv, height=h, color=vz.BLUE, label=f"Blinkit, Zepto, Instamart, BigBasket (n={len(comp)})")
for yy, v in zip(y - h / 2 - 0.02, fcv):
    ax.text(v + 0.6, yy, f"{v:.0f}%", va="center", fontsize=8.6, color=vz.INK)
for yy, v in zip(y + h / 2 + 0.02, cpv):
    ax.text(v + 0.6, yy, f"{v:.0f}%", va="center", fontsize=8.6, color=vz.INK2)
ax.set_yticks(y); ax.set_yticklabels([NEG[c] for c in order]); ax.invert_yaxis()
ax.set_xlim(0, 46); ax.set_xlabel("% of 1-2 star reviews mentioning the theme")
ax.grid(axis="y", visible=False); ax.legend(loc="lower right")
o = res["firstclub_onboarding"]
vz.title(ax, "FirstClub's complaints start before the first order",
         f"{o['pre_purchase_only_share']*100:.0f}% of FirstClub's 1-2 star reviews raise no problem with an actual order (only access, app or price), "
         f"vs {res['competitors_pre_purchase_only_share']*100:.0f}% for competitors")
vz.source(fig, SRC)
fig.savefig("charts/02_firstclub_vs_market.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# Chart 3 - FirstClub quarterly share of 1-2 star reviews
t = trend.reset_index()
t = t[t.reviews >= 50]
fig, ax = plt.subplots(figsize=(9.2, 4.2))
xs = np.arange(len(t))
ax.bar(xs, t.share_1_2_star * 100, width=0.6, color=vz.ORANGE)
for x, (_, rr) in zip(xs, t.iterrows()):
    ax.text(x, rr.share_1_2_star * 100 + 0.8, f"{rr.share_1_2_star*100:.0f}%", ha="center", fontsize=9.5, color=vz.INK)
    ax.text(x, 1.2, f"n={int(rr.reviews)}\navg {rr.avg_rating:.1f}★", ha="center", fontsize=7.8, color="#ffffff")
labels = {"2025Q3": "Jul-Sep 25", "2025Q4": "Oct-Dec 25", "2026Q1": "Jan-Mar 26", "2026Q2": "Apr-Jun 26",
          "2026Q3": "Jul-Sep 26", "2026Q4": "Oct 26 (to 24th)"}
ax.set_xticks(xs); ax.set_xticklabels([labels.get(q, q) for q in t.quarter])
ax.set_ylim(0, 33); ax.set_ylabel("% of written reviews that are 1-2 stars"); ax.grid(axis="x", visible=False)
vz.title(ax, "FirstClub's share of 1-2 star reviews has more than doubled this year",
         "All written Play Store reviews of the FirstClub app, by quarter")
vz.source(fig, "Data: Google Play reviews of com.firstclub.app, collected 24 Oct 2026 (2,205 written reviews)")
fig.savefig("charts/03_firstclub_rating_trend.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# Chart 4 - praise themes
pr = praise[praise.code != "o"].sort_values("share", ascending=True)
fig, ax = plt.subplots(figsize=(8.8, 4.6))
ax.barh(pr.theme, pr.share * 100, height=0.6, color=vz.BLUE)
for yy, v in enumerate(pr.share * 100):
    ax.text(v + 0.8, yy, f"{v:.0f}%", va="center", fontsize=9, color=vz.INK)
ax.set_xlim(0, 70); ax.set_xlabel("% of 4-5 star reviews mentioning the theme")
ax.grid(axis="y", visible=False)
vz.title(ax, "What FirstClub's fans praise: quality first, speed a distant sixth",
         f"Random sample of {len(pos)} written 4-5 star FirstClub reviews")
vz.source(fig, SRC)
fig.savefig("charts/04_firstclub_praise.png", dpi=200, bbox_inches="tight")
plt.close(fig)
print("charts written")
