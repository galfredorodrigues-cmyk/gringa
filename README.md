# HER POV storefront

HER POV's English-language storefront and pre-checkout funnel for four digital guides and the Complete Library.

- Main page: <https://vitrinyx.com/>
- Pre-checkout Last Chance Offer: <https://vitrinyx.com/last-offer>
- Thank-you page: <https://vitrinyx.com/thank-you>
- Repository: `galfredorodrigues-cmyk/gringa`

## Commercial structure

| Product / offer | USD | Files |
|---|---:|---|
| The First Message Formula — Volume 01 | $9.90 | Volume 01 + First Message Cheat Sheet |
| The Reply Decoder — Volume 02 | $4.90 | Volume 02 |
| The Profile Makeover — Volume 03 | $7.90 | Volume 03 |
| From Chat to First Date — Volume 04 | $19.90 | Volume 04 |
| Complete Library | $29.90 | Four volumes + bonus |
| Last Chance Offer | $21.90 | Same five PDFs as Complete Library |

The $21.90 offer is shown before the customer pays. Declining it leads to the $9.90 Starter checkout; accepting it charges a total of $21.90 in one purchase. The main-page Complete Library offer leads directly to $29.90. It is not a post-purchase upsell.

## Current release state

As checked on 2026-10-26, all five Hotmart products are marked for active sales. The $9.90 Starter, $21.90 Last Chance Offer, and $29.90 Complete Library checkout pages display the expected USD totals. Hotmart checkout URLs are configured in Hostinger. The seller has authorized enabling storefront buttons; this release does not represent buyer delivery, tax, or merchant-policy checks as complete.

Producer-side eBook previews confirmed the Starter has exactly Volume 01 and the Cheat Sheet, and the Complete Library has all four volumes plus the Cheat Sheet. All five files opened in Hotmart's preview. This confirms the attached content is readable in preview, but it does not verify the buyer's post-payment email/access flow; no real order was placed.

The seller confirms the bank account is approved; the Hostinger payout confirmation flag is set. Seller policy approval, tax review, and post-payment delivery tests remain unset. Hotmart's public checkout still labels the author "Magic Wolf" even though the public profile was updated to HER POV. This mismatch and seller support/legal details need attention. See [SETUP_PRODUCTION.md](SETUP_PRODUCTION.md) for evidence and remaining validation.

## Hosting

The site now runs on Hostinger Business as a Node 20 / Express app, using the existing templates and approved design. The registered domain `vitrinyx.com` (with “y”) and its `www` host point to Hostinger; HTTPS and CDN show active in hPanel. Render remains available as an app fallback but no longer serves the public domain.

The `/health` route distinguishes seller authorization from technical delivery verification: `checkout_enabled` can be true while `integration_operational` and `live_ready` remain false until approved buyer delivery and seller checks have been completed. `/thank-you?offer=starter`, `?offer=bundle`, and `?offer=last-chance` show offer-specific next steps without claiming to confirm payment. The Hostinger app is manually uploaded from a ZIP; automatic GitHub deployment is not connected. Mobile performance testing has not been completed.

## Local run and checks

```sh
npm install
npm test
npm start
```

The Node test suite checks preview fail-closed behavior, the seller-authorized storefront flow, offer-specific thank-you pages, funnel routes, Hotmart health reporting, assets, policies and checkout destinations under synthetic test configuration. It does not perform a payment or verify Hotmart fulfillment.

The Render fallback can run with Python: `pip install -r requirements.txt` followed by `gunicorn --bind 0.0.0.0:$PORT app:app`.

Do not commit buyer PDFs, seller contact details, checkout environment values, or account credentials. `STOREFRONT_LAUNCH_AUTHORIZED=yes` is a separate seller release instruction; it does not certify delivery, tax, policy, or legal checks. The custom-domain DNS cutover is complete; keep Render intact as a fallback.
