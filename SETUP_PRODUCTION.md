# HER POV / Final release checklist (Stripe + SendOwl)

The four educational PDF guides and bonus are COMPLETE. The AI Coach is a future concept.
The production storefront runs on https://her-pov-preview.onrender.com with checkout CLOSED until delivery and payouts are verified.
Owner dashboard: https://her-pov-preview.onrender.com/admin/setup

## Verified Stripe catalog / one-time USD prices

| Product | Stripe Product ID | Default Price ID | Total |
| --- | --- | --- | ---: |
| Volume 01: The First Message Formula (plus 1-page bonus) | prod_VVIj3wtkTG7eNW | price_1UUI8S8n16yukLPqFcJ9YTIk | $9.90 |
| Volume 02: The Reply Decoder | prod_VVLhvci2ykMohx | price_1UUKzk8n16yukLPqfDKKPqT3 | $4.90 |
| Volume 03: The Profile Makeover | prod_VVLhYhr67DJ4ch | price_1UUKzm8n16yukLPqwRoRve8p | $7.90 |
| Volume 04: From Chat to First Date | prod_VVTNx4tpx4d1TF | price_1UUSQa8n16yukLPqMpHFmIC8 | $19.90 |
| Complete Library Bundle (four guides plus bonus) | prod_VVTNODSow6TZhL | price_1UUSQp8n16yukLPqNRZflNNK | $29.90 |

Standalone total value: $42.60; bundle savings $12.70. One-time, no subscriptions.

## SendOwl: attach digital files before sales

The app was installed by the owner (reported, but not independently accessible via the connected Stripe API). Sign into Magic Universal in Stripe; launch the SendOwl app at the top of the Dashboard. SendOwl file vault: upload five separate PDFs from the private bundle. DO NOT put private files in GitHub.

Attach files to each Stripe product:
- Volume 01: 56-page main PDF AND 1-page cheat sheet bonus (2 files).
- Volume 02: Reply Decoder PDF (1 file).
- Volume 03: Profile Makeover PDF (1 file).
- Volume 04: From Chat to First Date PDF (1 file).
- Complete Library Bundle: all FIVE PDFs (5 files).

Use Stripe Product catalog / SendOwl / Unlinked products / Select product / add files (+) / Attach files. Do not create duplicate Stripe products or upload ZIP as a replacement if buyers expect separate files. Official reference: https://help.sendowl.com/help/managing-digital-products-stripe-sendowl

## Strict no-charge release blockers

1. Payment link for Volume 01 is INACTIVE: plink_1UUIU78n16yukLPqLqyBhpjt.
2. No payment links have yet been created for Volumes 02–04 or the Complete Library. Creating a Payment Link normally makes it live immediately; do not create or share them until storage/delivery is verified.
3. Stripe API currently reports charges_enabled=true, payouts_enabled=false, requirements.disabled_reason=other, currently_due=[]. Resolve in Stripe Dashboard / Stripe Support and verify payouts_enabled=true BEFORE opening customer charges.
4. MERCHANT_POLICIES_APPROVED and MERCHANT_TAX_REVIEWED must be based on finalized legal seller and contact details, refund and privacy policies, local taxes. Current terms/privacy/refunds pages contain DRAFT language.
5. SendOwl app does not support Stripe Sandbox. Coordinate an owner-controlled live-mode purchase only when delivery configuration is correct and repasses/account eligibility are resolved. Check a paid order delivers correct PDF links to inbox and allows opening every file.
6. After purchase simulations and actual verification, safely set Render env flags:
   STRIPE_MODE=live
   SENDOWL_PRODUCT_LINKED=yes
   SENDOWL_ALL_PRODUCTS_LINKED=yes
   SENDOWL_DELIVERY_TESTED=yes
   SENDOWL_BUNDLE_TESTED=yes
   STRIPE_PAYOUTS_CONFIRMED=yes
   STRIPE_LINKS_ACTIVE_CONFIRMED=yes
   MERCHANT_LEGAL_NAME=<verified actual seller name>
   MERCHANT_COUNTRY=<actual country>
   MERCHANT_CONTACT_ADDRESS=<actual mailing address>
   SUPPORT_EMAIL=<working customer support email>
   MERCHANT_POLICIES_APPROVED=yes
   MERCHANT_TAX_REVIEWED=yes
   LIVE_READY=yes
   BUNDLE_PAYMENT_LINK_URL=https://buy.stripe.com/<real, verified, active bundle link>
   *Never set these flags to yes solely to make the UI live; verified delivery is mandatory.*

## Architecture

- Stripe: prices, payment processing, receipts.
- SendOwl: five private PDF assets and transaction email/download page.
- Render: marketing sales funnel, owner monitoring.
- Future HER POV AI Coach: separate unbuilt product, NOT included in the guide bundle.
- Cloudflare R2/Resend: NOT needed on chosen launch route. Legacy code remains dormant, and its webhook remains disabled.

Security: all buyer files in SendOwl; do not put them in the public GitHub repo or a public URL. Never post credentials in chat.

## Legal policy pages prepared in English (not yet owner-approved)
- https://her-pov-preview.onrender.com/terms
- https://her-pov-preview.onrender.com/privacy
- https://her-pov-preview.onrender.com/refunds
- https://her-pov-preview.onrender.com/contact

Before taking orders, the seller must verify their actual legal operator identity, customer service email, mailing address, refund terms, tax position and country. The current documents visibly mark themselves as prelaunch and the checkout gate requires valid merchant contact environment fields. Do not invent these fields or assume a legal review took place.

## Stripe payout restriction (observed 2026-10-25)
- Account Magic Universal: charges_enabled=true, payouts_enabled=false; requirements.disabled_reason='other', currently_due=[].
- Existing account business profile URL does not describe the HER POV storefront; the owner must decide whether to use this account commercially or separate a different brand.
- Stripe support: https://support.stripe.com/contact
- Brazil verification reference: https://support.stripe.com/questions/brazil-specific-account-verification-troubleshooting?locale=en-GB
- Do not activate any checkout until official Stripe confirms payouts_enabled=true.
