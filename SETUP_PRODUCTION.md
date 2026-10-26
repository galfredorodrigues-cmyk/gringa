# HER POV production setup

## Current architecture

- GitHub repository: `galfredorodrigues-cmyk/gringa` (source of truth).
- Existing fallback: Flask on Render (`her-pov-preview.onrender.com`); keep it available until Hostinger has passed validation and DNS is intentionally migrated.
- Hostinger candidate: the same existing Jinja templates rendered by a new Express/Nunjucks adapter in `server.js`. This retains the approved HTML/CSS design and the `/`, `/last-offer`, `/upgrade`, legal, preview-art, and `/health` routes. Do not serve buyer PDFs from the public site.
- Hotmart is intended to process checkout and deliver the digital files. The storefront does not directly handle card data.

## Commerce map (observed in Hotmart UI)

| Offer | Hotmart product / offer | Price | Delivery |
|---|---|---:|---|
| Starter — The First Message Formula | Product 8805091 | $9.90 USD | Volume 01 + Cheat Sheet |
| Volume 02 — The Reply Decoder | Product 8806705 | $4.90 USD | Volume 02 |
| Volume 03 — The Profile Makeover | Product 8806718 | $7.90 USD | Volume 03 |
| Volume 04 — From Chat to First Date | Product 8806725 | $19.90 USD | Volume 04 |
| Complete Library — base offer `ajaj42kr` | Product 8808376 | $29.90 USD | Four guides + Cheat Sheet |
| Last Chance Offer — `si2c0upa` | Same product 8808376 | $21.90 USD | Same five files as Complete Library |

On 2026-10-26, all five products showed **Vendas ativas** in Hotmart. The three relevant checkout pages were opened without entering buyer data or submitting an order: Starter displayed $9.90, the Complete Library offer displayed $29.90, and the Last Chance offer displayed $21.90 as a total for the same full library. Hotmart's checkout pages are live and chargeable if a buyer uses a link; the HER POV website continues to keep its buttons gated in preview mode.

The Starter eBook management page showed exactly `01_The_First_Message_Formula.pdf` and `Bonus_First_Message_Cheat_Sheet.pdf`. Its buyer-facing producer preview listed both with open/download controls. Complete Library's management page showed exactly the five named PDFs; the buyer-facing producer preview listed all five, and each opened in the preview. The opened PDFs displayed the expected page counts (56, 19, 19, 19, and 1 for the bonus) and updated covers. This verifies Hotmart's attached files and producer-side rendering, but not actual post-payment delivery to a buyer. No transaction was made. Hotmart documentation states approved orders trigger automatic access instructions by email; the actual receipt/access flow still requires a no-charge platform test if available, otherwise an authorized test order.

## Funnel requirements

1. Main page starter selection opens `/last-offer` before payment.
2. Accept Last Chance → the distinct $21.90 offer for the same five files.
3. Decline → Starter at $9.90, with Volume 01 and the bonus.
4. Main page Complete Library button → direct $29.90 offer, bypassing `/last-offer`.

The $21.90 option is a one-time total before checkout, not a post-purchase upsell or an additional $12. Do not advertise live checkout until all relevant Hotmart links, prices, seller requirements and delivery behavior are confirmed.

## Fail-closed environment

Copy `.env.example` into the hosting provider's environment settings. Leave all flags set to `no` and all links blank until there is direct evidence for each value. Do not commit real checkout links, seller contact details, credentials, or buyer files to GitHub.

For Hostinger's Node.js app environment, configure the same keys in hPanel. Required keys include:

- `HOSTINGER_MANAGED_NODE=yes` in Hostinger only. Hostinger imports the selected entry file, so this opt-in starts the Express listener when that runner loads `server.js`; leave it unset for local test imports.

- `CHECKOUT_PROVIDER=hotmart`
- `HOTMART_LINK_01`, `_02`, `_03`, `_04`, `_BUNDLE`, and `_LAST_OFFER`
- `HOTMART_ALL_OFFERS_VERIFIED`, `HOTMART_USD_PRICES_VERIFIED`, `HOTMART_DELIVERY_TESTED`, `HOTMART_BUNDLE_CONTENT_VERIFIED`, `HOTMART_PAYOUTS_CONFIRMED`
- `MERCHANT_LEGAL_NAME`, `MERCHANT_COUNTRY`, `MERCHANT_CONTACT_ADDRESS`, `SUPPORT_EMAIL`
- `MERCHANT_POLICIES_APPROVED`, `MERCHANT_TAX_REVIEWED`, `LIVE_READY`
- `LAST_OFFER_USD_PRICE_VERIFIED`, `LAST_OFFER_FIVE_FILES_VERIFIED`, `LAST_OFFER_DELIVERY_TESTED`, `LAST_OFFER_POLICIES_APPROVED`, `LAST_OFFER_LAUNCH_APPROVED`

The server validates Hotmart domains, distinct standard offer URLs, all required standard gates, seller details, and independent Last Chance gates. The special $21.90 URL must be different from the five standard offer URLs. Missing or invalid values keep checkout disabled. `/health` reports the selected provider and whether the Hotmart integration checks are operational; `status=ok` only means the web process answered.

## Hostinger deployment and domain cutover

Hostinger's current official guidance lists Business Web Hosting as supporting Node.js web apps and Express, including deployment from GitHub. Account-specific app slots, resource limits and DNS/SSL settings still need inspection inside the owner's hPanel.

For this Hostinger app:

1. Create a Node.js web app for a temporary Hostinger domain/subdomain. Use Node 20/22/24 supported by hPanel, framework Express, repository `galfredorodrigues-cmyk/gringa`, and branch `main` (the adapter is merged there).
2. Build command: `npm install`; entry file: `server.js`.
3. Keep the Hotmart checkout gates closed. Set no real seller secrets in source files.
4. Test `/`, `/last-offer`, `/upgrade`, `/terms`, `/privacy`, `/refunds`, `/contact`, all four `/sample-page/*.svg` previews, `/product-art/*.png`, and `/health` on the temporary Hostinger URL, desktop and mobile. Verify no 404/500, no sensitive PDFs exposed, and check TLS on that temporary domain.
5. Confirm app logs, resource behavior, Hostinger SSL, and custom-domain binding. Do not change `vitrinyx.com` DNS yet.
6. Only after the Hostinger copy is healthy, approved, and ready should the owner authorize a DNS switch. Keep Render unchanged until DNS, HTTPS, redirects and real device/browser smoke checks pass.
7. Future releases: commit to GitHub, review, merge/deploy the approved branch in hPanel, run the route and health checks, then promote the deployment.

The temporary app `dodgerblue-seal-706434.hostingersite.com` was created in the owner's Business plan and deployed from `her-pov-hostinger-fixed.zip`. The first version returned 503 because Hostinger imports the entry file and does not support a `require.main === module` guard around `listen()`. The fix now uses `HOSTINGER_MANAGED_NODE=yes`. After redeployment, `/health` returned Hotmart with `integration_operational=false`, `checkout_enabled=false`, `live_ready=false`, and `mode=preview`; Hostinger runtime logs reported zero errors. Desktop routes for the home, offer, redirect, legal pages, sample SVGs, product-art images, health, and the expected 404 were checked. The approved editorial design rendered. The temporary site loaded over HTTPS without a browser certificate warning. Mobile performance was not checked in this pass. Keep the custom domain/DNS untouched until delivery and seller/policy checks pass.

## Release validation gates

Before opening checkout, verify in Hotmart:

- All five products currently show active sales; confirm there is no separate account-level document, tax, identity or policy restriction before launch.
- USD one-time amounts and offer-specific checkout links match the table above.
- Starter has exactly Volume 01 + Cheat Sheet; Complete $29.90 and Last Chance $21.90 each deliver the same five PDFs.
- Covers on Hotmart correspond to current approved sales-page covers; PDF page counts/content remain intact.
- The owner confirms the seller bank account is approved. A previously viewed HotPay Brasil screen did not display a payout account, so reconcile that account-level view in Hotmart before setting `HOTMART_PAYOUTS_CONFIRMED=yes`; do not treat bank approval itself as pending without a current platform block.
- Seller identity, policies, tax position, refund window, customer-support inbox, payment methods and US buyer checkout are confirmed.
- Test accept/decline/direct-bundle routing on the deployed preview and test automatic post-payment file access using a platform no-charge method if available. Producer previews and checkout-page inspection are complete, but they do not prove post-payment buyer email/access. Never conduct a real purchase without the owner's authorization.
- Test Hostinger deployment and temporary-domain HTTPS before any DNS change.

At the current checked state, all five product records show active sales and the three checkout totals match the planned prices. The Hostinger preview and the public Render site both keep checkout disabled; Render remains unchanged as the fallback. Do not set `LIVE_READY=yes`, mark delivery as fully verified, or promote the site until the temporary Hostinger deployment and post-payment delivery path are verified.
