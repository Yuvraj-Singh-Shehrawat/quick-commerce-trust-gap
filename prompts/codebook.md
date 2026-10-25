# Codebook: complaint and praise themes

Each review gets **one or more codes**. The **first code is the primary theme**: the complaint that drives the rating. Codes after it are other issues the review mentions.

## Negative reviews (1–2★): 12 codes

| Code | Theme | Includes | Does not include |
|---|---|---|---|
| Q | Quality / freshness / expiry | rotten, stale, expired or near-expiry, damaged, leaking, melted, bad taste or smell, fake or defective product, food-safety worries | wrong item (W) |
| W | Wrong / missing items | missing item, wrong product, short quantity or weight, freebie or offer item not in the bag | a whole order never arriving (X) |
| L | Late delivery | slower than promised, ETA keeps changing, "10 minutes" took an hour | cancelled orders (X) |
| X | Cancelled / not delivered | order cancelled by the platform or rider, "marked delivered" but never arrived, paid but nothing came | — |
| P | Price & fees | prices higher than other apps or the market, handling / platform / surge / small-cart fees, minimum order for free delivery, price changed at checkout | offers and coupons not working (M) |
| R | Refund & support | refund refused or delayed, unhelpful support, bot-only support, no phone number, return or replacement refused | — |
| A | App / tech / payments | crashes, login or OTP failures, slow loading, UI/UX friction, payment failures, address or location bugs, no cash on delivery, onboarding questionnaire | "my area is not served" (U) |
| B | Delivery partner behaviour | rude rider, refusing doorstep delivery, asking for extra cash, mishandling the order | — |
| S | Stock / selection | items out of stock, limited range, wrong brands carried | — |
| U | Not serviceable in my area | app not live in the user's city or pincode, "start in X", area became unserviceable | — |
| M | Offers / wallet / membership | coupons not applied, ₹1 deals, referral rewards, wallet or cashback expiry, membership | — |
| O | Other / unclear | spam, too vague to code, marketing or ads complaints, packaging plastic, unrelated | — |

## FirstClub positive reviews (4–5★): 11 codes (lower case)

| Code | Praise theme |
|---|---|
| q | Quality / freshness / taste |
| f | Fast or on-time delivery |
| p | Price / value / offers |
| s | Selection / curation / variety |
| c | Customer service |
| a | App UX |
| g | Gifts / freebies |
| k | Packaging |
| t | Trust / transparency (lab reports, clean label, no junk, organic) |
| u | Asks FirstClub to expand to their city |
| o | General praise / other |

## Prompt used for LLM classification (`src/classify_llm.py`)

```
You label Indian quick-commerce app reviews. Use ONLY the codebook below.
Return one line per review in the form  <id>:<codes>
- Use upper-case codes for 1-2 star reviews, lower-case codes for 4-5 star reviews.
- List every code that applies. Put the code for the MAIN reason for the rating first.
- Hinglish and Hindi reviews are in scope; label them like English ones.
- If nothing fits or the text is unintelligible, use O (or o).
<codebook tables pasted here>
Reviews:
<id>|<stars>|<text>
...
```
