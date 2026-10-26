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

The Hotmart product records and their files/offers were present, but all five products were still marked **Produtor Rascunho** when reviewed on 2026-10-26. The site remains in preview mode; payment controls are fail-closed. The product records show “Finalizar cadastro” to submit them for Hotmart review, which also accepts Hotmart's data-processing terms.

The seller confirms their bank account is approved. The last Hotmart financial screen viewed showed approved documents but no payout account listed under HotPay Brasil, so Hotmart's actual payout-account state still needs to be reconciled before the launch gate can be marked verified. See [SETUP_PRODUCTION.md](SETUP_PRODUCTION.md) for the evidence and release checklist.

## Hosting

The existing production app is Flask on Render. A Node.js/Express adapter for Hostinger is in `server.js`, using the existing Nunjucks-compatible templates and preserving the approved visual design. Hostinger publishes support for Node.js/Express on Business web hosting, but the owner-specific hPanel deployment, quota, temporary-domain tests, SSL and DNS cutover have not been completed. Render remains the fallback until Hostinger has passed validation.

## Local run and checks

```sh
npm install
npm test
npm start
```

The Node test suite checks preview fail-closed behavior, funnel routes, Hotmart health reporting, assets, policies and the three checkout destinations under an explicitly synthetic test configuration. It does not perform a payment or verify Hotmart fulfillment.

The Render fallback can run with Python: `pip install -r requirements.txt` followed by `gunicorn --bind 0.0.0.0:$PORT app:app`.

Do not commit buyer PDFs, seller contact details, checkout environment values, or account credentials. Do not set launch gates to `yes` until each required fact has been verified. Never migrate DNS before the temporary Hostinger deployment, HTTPS and route checks pass.
