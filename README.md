# HER POV storefront

HER POV's English-language storefront and pre-checkout funnel for four digital guides and the Complete Library.

- Main page: <https://vitrinyx.com/>
- Pre-checkout Last Chance Offer: <https://vitrinyx.com/last-offer>
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

As checked on 2026-10-26, all five Hotmart products are approved and marked for active sales. The $9.90 Starter, $21.90 Last Chance Offer, and $29.90 Complete Library checkout pages display the expected USD totals. Hotmart checkout URLs are configured in Hostinger's environment settings. These direct Hotmart URLs can accept payment; the storefront buttons remain fail-closed in preview mode.

Producer-side eBook previews confirmed the Starter has exactly Volume 01 and the Cheat Sheet, and the Complete Library has all four volumes plus the Cheat Sheet. All five files opened in Hotmart's preview. This confirms the attached content is readable in preview, but it does not verify the buyer's post-payment email/access flow; no real order was placed.

The seller confirms the bank account is approved; the Hostinger payout confirmation flag is set. Seller policy approval, tax review, and post-payment delivery tests remain unset. Hotmart's public checkout still labels the author "Magic Wolf" even though the public profile was updated to HER POV. Resolve the public-name and support/legal details before opening storefront checkouts. See [SETUP_PRODUCTION.md](SETUP_PRODUCTION.md) for current evidence and the release checklist.

## Hosting

The site now runs on Hostinger Business as a Node 20 / Express app, using the existing templates and approved design. The registered domain `vitrinyx.com` (with “y”) and its `www` host point to Hostinger; HTTPS and CDN show active in hPanel. Render remains available as an app fallback but no longer serves the public domain.

The public Hostinger `/health` currently reports Hotmart as checkout and delivery provider, with `integration_operational=false`, `checkout_enabled=false`, `live_ready=false`, and `mode=preview`. The home page and `/last-offer` load on the custom domain; the $21.90 accept and $9.90 decline controls and the $29.90 bundle control are intentionally disabled until buyer delivery and merchant checks pass. The Hostinger app was uploaded from a ZIP; automatic GitHub deployment is not connected. Mobile performance testing has not been completed.

## Local run and checks

```sh
npm install
npm test
npm start
```

The Node test suite checks preview fail-closed behavior, funnel routes, Hotmart health reporting, assets, policies and the three checkout destinations under an explicitly synthetic test configuration. It does not perform a payment or verify Hotmart fulfillment.

The Render fallback can run with Python: `pip install -r requirements.txt` followed by `gunicorn --bind 0.0.0.0:$PORT app:app`.

Do not commit buyer PDFs, seller contact details, checkout environment values, or account credentials. Do not set launch gates to `yes` until each required fact has been verified. The custom-domain DNS cutover is complete; keep Render intact as a fallback until Hostinger operation and launch gates have been confirmed.
