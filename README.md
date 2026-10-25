# HER POV — Complete Digital Guide Library

A responsive English-language sales funnel hosted on Render.

## Storefront

https://her-pov-preview.onrender.com

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
