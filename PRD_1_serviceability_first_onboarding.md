# PRD 1: Serviceability-first onboarding

**Area:** New customer acquisition / App experience
**Owner:** (intern) | **Status:** Draft for review | **Evidence:** [README, finding 2](README.md)

## Problem
People who install FirstClub outside its delivery zones find that out only after signing up, answering onboarding questions or building a cart. They leave angry, and many leave a 1★ review.

- **Serviceability:** 16% of FirstClub's 1–2★ Play Store reviews (63 of 385) are "not serviceable in my area", vs 4% across Blinkit, Zepto, Instamart and BigBasket.
- **Late discovery:** 18 of those 63 say they had already registered, answered questions or filled a cart before learning this. 8 complain about seeing FirstClub ads anyway.
- **Login and launch:** 9% (36 reviews) are about login/OTP failures or an app that won't open.
- **Overall:** 38% of FirstClub's negative reviews raise no problem with an actual order, vs 13% for competitors. These reviewers never got to experience the product, yet they pull the store rating down for everyone who might.

> *"The app makes you enter all personal details and complete the entire setup, only to state at the very end that service is not available"* (1★, Sep 2026)

## Goal
- **No dead ends:** no one should invest effort before learning whether FirstClub delivers to them.
- **Keep the demand:** unserviceable visitors become a demand signal (a waitlist by pincode) instead of a 1★ review.

## Non-goals
- Expanding delivery zones. This PRD only stops promising what we can't deliver.
- Changing onboarding for serviceable users beyond moving the location step earlier.

## Solution
1. **Location first, before login.**
   - First screen: "Where should we deliver?" with GPS or pincode/society search.
   - Serviceable users go straight to browsing as a guest. Login happens at checkout.
2. **Honest "not yet" screen for unserviceable locations.**
   - Shows: "We're not in {area} yet. {n} neighbours are waiting."
   - One-tap waitlist using phone number or WhatsApp. No account and no questionnaire.
   - Shows the nearest serviceable area and our city list.
3. **Waitlist → expansion signal.**
   - A weekly table of waitlist sign-ups by pincode for the expansion and ops teams.
   - Auto-notify everyone in a pincode the day it goes live. These are warm first orders for the launch.
4. **Stop paying to frustrate people.**
   - Geo-fence performance-marketing audiences to serviceable pincodes, plus waitlist-heavy pincodes when they launch.
5. **Login reliability.**
   - Add a fallback OTP channel (WhatsApp) after one failed SMS.
   - Log OTP failures by carrier and handset.

## Success metrics
| | Metric | Target |
|---|---|---|
| Primary | Install → first order within 7 days, **serviceable installs only** | +2 pts vs control (baseline from Mixpanel funnel) |
| Secondary | Unserviceable installs that reach the waitlist (vs uninstall) | > 40% |
| Secondary | 1–2★ reviews mentioning serviceability or login, per 100 reviews | −50% within 6 weeks |
| Guardrail | Account creation rate among serviceable users (guest browsing could delay sign-up) | no drop > 1 pt |
| Guardrail | Checkout conversion (login moved to checkout) | no drop |

## Experiment
- **Assignment:** randomise new installs 50/50 at first app open (control = current flow).
- **Primary analysis:** install-to-first-order among serviceable installs. This is the only group where the change can move orders, so analysing everyone would dilute the effect.
- **Sample size:** at a 25% baseline, detecting +2 pts (α = 0.05, power 0.8) needs **~7,500 serviceable installs per arm**.
  - The baseline is a placeholder; replace it with the real funnel in week 1.
  - At current install volumes, run time = 7,500 ÷ (weekly serviceable installs ÷ 2).
- **Review metric:** read as a before/after trend, because reviews can't be randomised. Treat it as directional.

## Risks
- **Guest browsing → fewer leads:** we lose phone numbers from browsers who never buy. Mitigation: the waitlist and checkout login still capture intent.
- **Small waitlist pincodes:** waitlists in pincodes we won't serve for months create expectations. Mitigation: show honest timelines only where expansion is planned.

## Rollout
- Week 1: design + location API.
- Week 2: build behind a flag.
- Weeks 3–6: A/B test.
- Then ship the winner and hand the pincode demand table to the expansion team.
