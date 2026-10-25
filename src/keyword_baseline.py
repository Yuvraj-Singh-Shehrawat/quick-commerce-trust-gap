"""Transparent keyword baseline for the negative-review codebook, and its agreement with the LLM labels.

Why: LLM labels need a sanity check. This rule-based classifier is crude on purpose. Where it
agrees with the LLM, the theme is lexically obvious. Where it disagrees, the LLM is doing
something the keywords can't (negation, Hinglish, context), or one of the two is wrong.
Human hand-labels (validation/) are the real test; this is the free first check.

    python src/keyword_baseline.py   -> outputs/keyword_vs_llm_kappa.csv
"""
import os
import re

import pandas as pd
from sklearn.metrics import cohen_kappa_score

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RULES = {
    "Q": r"expir|rotten|stale|spoil|fung|mou?ld|not fresh|quality|damag|broken|leak|smell|worm|insect|curdl|melt|defect|fake|sada|kharab|ghatiya",
    "W": r"missing|wrong (item|product|order)|incomplete|less quantity|short|instead of|different (item|product)|only \d+|nikal liye",
    "L": r"\blate\b|delay|slow deliver|\bhours?\b|\bhrs?\b|waiting|wait(ed)? for|\beta\b|took .{0,12}min|time (shown|promised)|min(ute)?s? (but|and|still)",
    "X": r"cancel|not deliver|never deliver|didn.?t deliver|marked (as )?delivered|not receiv|never receiv|didn.?t receiv|did not receiv",
    "P": r"price|expensive|costly|overpric|\bfees?\b|charge|surge|minimum (order|cart|amount)|free delivery|\bmrp\b|\brates?\b|mehnga|mahanga",
    "R": r"refund|support|customer care|customer service|\bchat\b|\bbot\b|helpline|\breturn|replace|exchange|complain|resolution|resolve",
    "A": r"\bapp (is|does|not|keeps|crash)|login|log in|\botp\b|crash|bug|glitch|payment|\bupi\b|\bcard\b|loading|not load|\bui\b|\bux\b|update|cash on delivery|\bcod\b|sign ?up|onboarding|address",
    "B": r"delivery (boy|guy|partner|person|agent|executive|man)|\brider\b|rude|behaviou?r|doorstep|come down|misbehav",
    "S": r"out of stock|not in stock|\bstock\b|limited (option|item|product)|variety|very few (option|product|item)",
    "U": r"unservic|not servic|serviceable|not available in (my|our)|my (area|location|city|locality)|pin ?code|\b5\d{5}\b|start (in|your|service)|coming soon|not (operating|available) in",
    "M": r"offer|coupon|cash ?back|wallet|referr?al|\brefer\b|membership|free (gift|item)|1 ?rs|₹ ?1\b|voucher|\bdeals?\b",
}
CODES = list(RULES)


def keyword_codes(text: str) -> str:
    t = str(text).lower()
    return "".join(c for c in CODES if re.search(RULES[c], t))


def main():
    df = pd.read_csv(os.path.join(ROOT, "data", "labelled_reviews.csv"))
    neg = df[df["set"] == "negative"].copy()
    neg["kw_codes"] = neg.text.map(keyword_codes)
    rows = []
    for c in CODES:
        llm = neg.codes.str.contains(c).astype(int)
        kw = neg.kw_codes.str.contains(c).astype(int)
        rows.append({"code": c, "llm_share": llm.mean(), "keyword_share": kw.mean(),
                     "agreement": (llm == kw).mean(), "cohen_kappa": cohen_kappa_score(llm, kw)})
    out = pd.DataFrame(rows).round(3)
    out.to_csv(os.path.join(ROOT, "outputs", "keyword_vs_llm_kappa.csv"), index=False)
    print(out.to_string(index=False))
    return out


if __name__ == "__main__":
    main()
