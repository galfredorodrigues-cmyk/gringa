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

- **Stripe** processes payments using the existing live account.
- **SendOwl Stripe App** stores files and sends private downloads after payment. Installation was reported by the owner but product links and fulfillment have not been verified by the available tools.
- **Render** hosts this public web storefront. No buyer PDFs or account secrets belong in this GitHub repo.

The code retains dormant legacy Stripe-webhook / R2 / Resend routes but these are NOT part of the planned SendOwl commerce stack. Keep their legacy webhook disabled.

## Security and release rules

Checkout must stay disabled until all criteria are verified, not merely assumed:
- Each of the five Stripe products is linked to exactly the expected files in SendOwl.
- A controlled paid purchase has been tested for an individual guide and the complete bundle, and emails, PDFs and access restrictions actually work.
- Stripe `payouts_enabled=true` (currently false, `disabled_reason=other`; only Stripe can remove the restriction).
- All Payment Links have been created, inspected and activated after successful delivery validation.
- A verified merchant legal name, operating country, mailing address and functioning support inbox exist in Render environment.
- Terms of Purchase, Privacy Notice and Refunds & Digital Delivery policy are reviewed and accepted by the merchant, and tax obligations have been reviewed.

Local implementation uses Flask and Jinja2 templates. Install dependencies with `pip install -r requirements.txt`; run `gunicorn --bind 0.0.0.0:$PORT app:app`. Tests are in `tests/test_delivery.py`.

See [SETUP_PRODUCTION.md](SETUP_PRODUCTION.md) for Stripe Product IDs, SendOwl file mapping and all launch flags.
