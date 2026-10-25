# PRD 2: Quality Receipt + 1-tap freshness guarantee

**Area:** Supply-chain quality & transparency / Customer retention
**Owner:** (intern) | **Status:** Draft for review | **Evidence:** [README, findings 1, 3, 4](README.md)

## Problem
FirstClub promises "quality is pre-verified, not assumed". Today customers can't see that verification on their order, and when quality fails, fixing it is slow.

- **Market:** across 1,200 competitor 1–2★ reviews, quality (25%) and refund/support (40%) dominate. Late delivery is 9%. Customers forgive slow; they don't forgive a bad item with no fix.
- **FirstClub trend:** per 100 reviews, quality complaints rose from 1.6 (before Apr 2026) to 3.8 (Jul–Oct 2026), and refund/support complaints from 2.3 to 4.5.
- **Claims flow:**
  - Several reviewers couldn't raise a quality claim at all: *"Received stale cashews… The app doesn't allow [a request], it keeps redirecting to homepage."*
  - Others were stuck with a bot that couldn't resolve it.
- **Transparency gap:** some reviewers noticed it directly, e.g. *"the [lab] reports are from June 2026 and it's September now."*
- **Our moat:** 61% of 4–5★ reviews praise quality, and 13% praise trust and lab reports. Quality is the moat, so its failures cost us more than they cost competitors.

## Goal
- **Visible quality:** make quality checks visible on every order.
- **Fast fixes:** make a quality failure cost the customer under 30 seconds to fix.
- **Retention:** retain customers who hit a bad item, in the orders 1–5 window where habits form.

## Solution
1. **Quality Receipt (in the order screen and the delivery WhatsApp)**
   - For fresh items: packed-at time, harvest/receipt date where known, and "QC passed by {store} at {time}".
   - For staples with lab tests: test date and a link to the report.
   - Reports older than 60 days are flagged internally, never shown as current.
2. **1-tap freshness claim.**
   - From the receipt: tap the item, take a photo, done.
   - **Instant wallet credit** for fresh items under ₹300 and for accounts with fewer than 3 claims in 30 days. Everything else goes to a human within 15 minutes.
   - Photo upload must work from the camera *and* the gallery. This fixes the redirect bug reviewers describe.
3. **Close the loop to supply chain.**
   - Every claim is tagged SKU × store × batch × supplier.
   - A daily "quality heatmap" for category and ops. Auto-alert when a batch gets 3 or more claims.
   - **Expiry guard at picking:** block packing of items within X days of expiry (X set per category).

## Success metrics
| | Metric | Target |
|---|---|---|
| Primary | 30-day repeat rate of customers who file a quality claim | +5 pts vs control |
| Secondary | Median time from claim to resolution | < 2 min (from hours) |
| Secondary | Quality and refund complaints per 100 Play Store reviews | back below the H1 2026 level |
| Guardrail | Claims per 100 orders, and credit cost as % of GMV | no spike > 20% (abuse check) |
| Guardrail | Repeat claimers (≥ 3 in 30 days) | monitored; routed to human review |

## Experiment
- **Unit:** randomise at the **store** level (dark store / clubhouse), not the customer. The QC loop and expiry guard act on stores, and customers who talk to each other in the same society shouldn't get different policies.
- **Design:** treatment stores get the receipt, 1-tap claims and expiry guard; control stores keep today's flow. Stratify by city and store age.
- **Primary analysis:** repeat rate among customers whose order had a claim, with cluster-robust SEs by store.
- **Test length:** set by claim volume. Few clusters means low power, so plan 6–8 weeks. If store count is too small, run a staggered rollout (stepped-wedge) instead.

## Risks
- **Lab costs:** showing dates exposes stale lab reports. That is a feature; budget for re-testing high-volume staples.
- **Instant credits invite abuse:** caps, photo checks and a repeat-claimer flag; the guardrails above.
- **Ops load:** the batch-level heatmap means acting on bad suppliers, which needs category-team buy-in up front.
