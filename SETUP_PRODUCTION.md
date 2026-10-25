# HER POV / Final release checklist (Hotmart preferred; Stripe legacy)

The four educational PDF guides and bonus are COMPLETE. The AI Coach is a future concept.
The production storefront runs on https://her-pov-preview.onrender.com with checkout CLOSED until delivery and payouts are verified.
Owner dashboard: https://her-pov-preview.onrender.com/admin/setup

## Hotmart launch path (prepared, NOT active)

HER POV will use the **five Hotmart offers** managed by the owner in ChatGPT Work.
The website now contains a provider-neutral button layout and *strictly gated*
Hotmart checkout links for all four individual guides and the Complete Library.
The live Render configuration has not been changed to Hotmart and orders remain closed.

**Information needed when Work finishes:**
1. Five **direct creator checkout/offer links** for each of the four guides
   and the Complete Library; they must be from `pay.hotmart.com` or
   `go.hotmart.com` and must be distinct. Do not share API tokens or passwords.
2. Confirm the actual buyer-facing checkout **USD prices** of $9.90,
   $4.90, $7.90, $19.90 and $29.90. Verify the final charged price,
   currency and any country-specific fees before announcing savings.
3. Verify the bundle includes the four full PDFs plus the 1-page bonus.
   Confirm the starter guide includes **both** the main PDF and its bonus.
4. Verify products are approved and sellable under current Hotmart policies,
   billing/payout eligibility, refund policy and customer support.
5. After all setup is approved, run at least one end-to-end controlled test
   including purchase confirmation, email access and all expected PDFs.
   If a test requires actual payment, the owner must authorize it explicitly.

**Render environment variables for the eventual Hotmart launch** (do not set
until each value is real and checked):

```text
CHECKOUT_PROVIDER=hotmart
HOTMART_LINK_01=https://pay.hotmart.com/<real-creator-offer>
HOTMART_LINK_02=https://pay.hotmart.com/<real-creator-offer>
HOTMART_LINK_03=https://pay.hotmart.com/<real-creator-offer>
HOTMART_LINK_04=https://pay.hotmart.com/<real-creator-offer>
HOTMART_LINK_BUNDLE=https://pay.hotmart.com/<real-creator-offer>
HOTMART_ALL_OFFERS_VERIFIED=yes
HOTMART_USD_PRICES_VERIFIED=yes
HOTMART_DELIVERY_TESTED=yes
HOTMART_BUNDLE_CONTENT_VERIFIED=yes
HOTMART_PAYOUTS_CONFIRMED=yes
MERCHANT_LEGAL_NAME=<verified merchant operator>
MERCHANT_COUNTRY=<verified country>
MERCHANT_CONTACT_ADDRESS=<verified real mailing address>
SUPPORT_EMAIL=<verified working support email>
MERCHANT_POLICIES_APPROVED=yes
MERCHANT_TAX_REVIEWED=yes
LIVE_READY=yes
```

Any missing or malformed value, missing seller data, duplicate links, missing
verification flag, or `LIVE_READY` not `yes` means that **every payment
button remains disabled**. No raw checkout URL is exposed in preview HTML.
The page remains `noindex,follow` while checkout is closed to avoid
promoting an unfinished store to search engines.

Hotmart's own official checkout integration reference:
https://developers.hotmart.com/docs/pt-BR/tutorials/checkout-elements/

**Do not turn on Stripe and Hotmart checkouts simultaneously.** The old Stripe
flow remains documented below only as a fallback and for audit history.

## Last Chance Offer BEFORE checkout (prepared only, NOT live)

The principal HER POV page preserves the original copy and shows two purchase choices: Volume 01 + bonus at USD $9.90 or the standard four-guide bundle + bonus at USD $29.90.

The **starter** choice routes first to `/last-offer` (old `/upgrade` redirects to the new address). **No payment has happened yet.** The visitor sees a pre-checkout final offer with two clear exits:
- **Accept**: buy all four guides plus the bonus for **USD $21.90 in one transaction**. This is a separate special-priced full-bundle offer containing five PDFs, saving USD $8.00 versus the publicly displayed USD $29.90 bundle before applicable tax/fees.
- **Decline / lose the offer**: continue to the existing Volume 01 + bonus checkout at USD $9.90.
The main page's direct bundle choice still goes to the USD $29.90 checkout and bypasses the final-offer page.

This is **not** a post-purchase upsell and must not be configured as an extra USD $12 charge. The old $12 post-purchase concept is superseded; never claim the customer already paid USD $9.90 at the last-offer page.

The last-offer page remains in preview mode with both payment controls disabled until validated. To enable the special option when the primary Hotmart checkout is already verified and open, provide a distinct, verified `HOTMART_LINK_LAST_OFFER` and independently confirm all flags:
```text
LAST_OFFER_USD_PRICE_VERIFIED=yes
LAST_OFFER_FIVE_FILES_VERIFIED=yes
LAST_OFFER_DELIVERY_TESTED=yes
LAST_OFFER_POLICIES_APPROVED=yes
LAST_OFFER_LAUNCH_APPROVED=yes
```
The software rejects the private link if it duplicates any of the five standard checkout URLs. It will not show the special button unless the original Hotmart release gate AND every new flag are validated.

Before opening any payment routes, confirm the USD buyer-facing amount, taxes and currency, all five actual private PDF file deliveries, supported direct Hotmart checkout URL, customer support, refund rights, payment eligibility and tests of accept, decline, interruption, duplicate payment prevention, and standard USD $29.90 bundle. Do not invent urgency timers or create a publicly indexed discount page. Seller must approve any change to live charging.

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
