# HER POV — Complete Digital Guide Library

A responsive English-language sales funnel hosted on Render.

## Storefront

https://vitrinyx.com/ (Render fallback: https://her-pov-preview.onrender.com)

## Products

| Product | Price (USD) | Files |
|---|---:|---:|
| The First Message Formula, Volume 01 | $9.90 | Main 56-page PDF + 1-page cheat sheet |
| The Reply Decoder, Volume 02 | $4.90 | 19-page PDF |
| The Profile Makeover, Volume 03 | $7.90 | 19-page PDF |
| From Chat to First Date, Volume 04 | $19.90 | 19-page PDF |
| Complete HER POV Library | $29.90 | All five PDFs (bundle) |

The HER POV AI Coach is a future idea, not sold in this launch.

## Commerce stack

- **Hotmart** is the preferred next checkout and digital-delivery provider. Product registration and owner approval are still underway in Work; it is **not connected or enabled** on the storefront.
- **GitHub + Render** host the public English-language HER POV marketing site, real PDF excerpt previews and the product artwork. The website can display all five direct Hotmart checkout links *only after every release gate is confirmed*.
- **Stripe + SendOwl** are the legacy fallback, with payment links still gated/inactive; there is no public buyer checkout today.
- Never put buyer PDF files, merchant credentials or API tokens in GitHub.

## Pre-checkout Last Chance Offer (no payments active)

- Main storefront: `https://vitrinyx.com/` retains all original editorial copy and sections, with two options: **Volume 01 + bonus for USD $9.90**, or **four volumes + bonus for USD $29.90**.
- Clicking either "start with one" button opens `https://vitrinyx.com/last-offer` **before any payment**. The old `/upgrade` path redirects to `/last-offer`.
- The optional offer is **USD $21.90 for all four e-books + bonus in a single checkout**, saving USD $8.00 vs the direct USD $29.90 full library (before any applicable taxes/fees). The buyer has paid **$0** at this stage: do not call the $21.90 checkout a $12 upgrade or charge $9.90 first.
- The intended two actions are (a) **accept** → separately verified Hotmart offer containing all five PDFs for USD $21.90; (b) **pass / lose the offer** → existing starter Hotmart offer containing Volume 01 and bonus for USD $9.90. Direct bundle choice on homepage keeps its own USD $29.90 checkout.
- This is a **pre-checkout special offer**, not a Hotmart post-purchase one-click upsell. Do not claim that a transaction occurred until the external payment provider verifies it. No invented timers or statements of false scarcity.
- In preview, the Last Chance Offer shows strong but disabled payment choices, with `noindex, nofollow, noarchive`. The homepage's "start with one" links work for previewing the offer. No payment can be made until corresponding separate release gates are verified.
- The private offer requires `HOTMART_LINK_LAST_OFFER` on an approved `pay.hotmart.com` or `go.hotmart.com` domain, **distinct from all five original links**, plus `LAST_OFFER_USD_PRICE_VERIFIED=yes`, `LAST_OFFER_FIVE_FILES_VERIFIED=yes`, `LAST_OFFER_DELIVERY_TESTED=yes`, `LAST_OFFER_POLICIES_APPROVED=yes`, `LAST_OFFER_LAUNCH_APPROVED=yes` and all standard Hotmart checkout gates.
- Confirm the precise USD charge and eligible market, seller rules, product contents, order confirmation, test delivery, refund handling, and customer support before setting any new release flags. Tests must verify accept, pass, direct $29.90 purchase, failure/no-charge states, wrong links, and duplicate payment attempts.
- Hotmart is not yet enabled, payment and release keys are not to be set to arbitrary demo values. Do not place private PDF files or credentials in GitHub.

## Security and release rules

Checkout must stay disabled until all criteria are verified, not merely assumed. For Hotmart, see the dedicated release flags and five-link mapping in [SETUP_PRODUCTION.md](SETUP_PRODUCTION.md). The legacy Stripe checks below apply only if the owner returns to Stripe:
- Each of the five Stripe products is linked to exactly the expected files in SendOwl.
- A controlled paid purchase has been tested for an individual guide and the complete bundle, and emails, PDFs and access restrictions actually work.
- Stripe `payouts_enabled=true` (currently false, `disabled_reason=other`; only Stripe can remove the restriction).
- All Payment Links have been created, inspected and activated after successful delivery validation.
- A verified merchant legal name, operating country, mailing address and functioning support inbox exist in Render environment.
- Terms of Purchase, Privacy Notice and Refunds & Digital Delivery policy are reviewed and accepted by the merchant, and tax obligations have been reviewed.

Local implementation uses Flask and Jinja2 templates. Install dependencies with `pip install -r requirements.txt`; run `gunicorn --bind 0.0.0.0:$PORT app:app`. Tests are in `tests/test_delivery.py`.

See [SETUP_PRODUCTION.md](SETUP_PRODUCTION.md) for Stripe Product IDs, SendOwl file mapping and all launch flags.
