"""Agreement between YOUR hand labels and the LLM labels.

1. Open validation/hand_label_150.csv (150 negative reviews, 30 per app).
2. Read prompts/codebook.md, then fill `your_codes` for every row WITHOUT looking at the LLM labels
   (e.g. "QR" = quality + refund/support, main reason first). Takes ~40 minutes.
3. python src/agreement.py   -> per-theme agreement and Cohen's kappa, plus primary-theme agreement.
"""
import os

import pandas as pd
from sklearn.metrics import cohen_kappa_score

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
hand = pd.read_csv(os.path.join(ROOT, "validation", "hand_label_150.csv"))
llm = pd.read_csv(os.path.join(ROOT, "data", "labelled_reviews.csv"))[["sid", "codes"]]
df = hand.merge(llm, on="sid")
df = df[df.your_codes.fillna("").str.strip() != ""]
if df.empty:
    raise SystemExit("Fill the your_codes column first.")
df["your_codes"] = df.your_codes.str.upper().str.replace(r"[^QWLXPRABSUMO]", "", regex=True)
rows = []
for c in "QWLXPRABSUMO":
    a = df.your_codes.str.contains(c).astype(int)
    b = df.codes.str.contains(c).astype(int)
    if a.sum() + b.sum() == 0:
        continue
    rows.append({"code": c, "you": a.mean(), "llm": b.mean(), "agreement": (a == b).mean(),
                 "kappa": cohen_kappa_score(a, b) if a.nunique() > 1 or b.nunique() > 1 else float("nan")})
out = pd.DataFrame(rows).round(3)
print(out.to_string(index=False))
print(f"\nPrimary-theme agreement: {(df.your_codes.str[0] == df.codes.str[0]).mean():.1%}  (n={len(df)})")
print(f"Any-overlap agreement:   {df.apply(lambda r: bool(set(r.your_codes) & set(r.codes)), axis=1).mean():.1%}")
