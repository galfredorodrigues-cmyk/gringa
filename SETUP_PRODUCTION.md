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

The five products were still marked **Produtor Rascunho** on 2026-10-26. Their overview pages showed the required sections complete and the action “Finalizar cadastro” to submit each item for analysis. Do not enable any checkout until Hotmart approves them and their checkout links work.

The product content screens had the following mapping when last inspected: Starter has `01_The_First_Message_Formula.pdf` and `Bonus_First_Message_Cheat_Sheet.pdf`; Volumes 02, 03 and 04 each have their corresponding PDF; Complete Library has all five PDFs. The $21.90 offer is a second offer on the same Complete Library product, so it shares its five digital files.

## Funnel requirements

1. Main page starter selection opens `/last-offer` before payment.
2. Accept Last Chance → the distinct $21.90 offer for the same five files.
3. Decline → Starter at $9.90, with Volume 01 and the bonus.
4. Main page Complete Library button → direct $29.90 offer, bypassing `/last-offer`.

The $21.90 option is a one-time total before checkout, not a post-purchase upsell or an additional $12. Do not advertise live checkout until all relevant Hotmart links, prices, seller requirements and delivery behavior are confirmed.

## Fail-closed environment

Copy `.env.example` into the hosting provider's environment settings. Leave all flags set to `no` and all links blank until there is direct evidence for each value. Do not commit real checkout links, seller contact details, credentials, or buyer files to GitHub.

For Hostinger's Node.js app environment, configure the same keys in hPanel. Required keys include:

- `CHECKOUT_PROVIDER=hotmart`
- `HOTMART_LINK_01`, `_02`, `_03`, `_04`, `_BUNDLE`, and `_LAST_OFFER`
- `HOTMART_ALL_OFFERS_VERIFIED`, `HOTMART_USD_PRICES_VERIFIED`, `HOTMART_DELIVERY_TESTED`, `HOTMART_BUNDLE_CONTENT_VERIFIED`, `HOTMART_PAYOUTS_CONFIRMED`
- `MERCHANT_LEGAL_NAME`, `MERCHANT_COUNTRY`, `MERCHANT_CONTACT_ADDRESS`, `SUPPORT_EMAIL`
- `MERCHANT_POLICIES_APPROVED`, `MERCHANT_TAX_REVIEWED`, `LIVE_READY`
- `LAST_OFFER_USD_PRICE_VERIFIED`, `LAST_OFFER_FIVE_FILES_VERIFIED`, `LAST_OFFER_DELIVERY_TESTED`, `LAST_OFFER_POLICIES_APPROVED`, `LAST_OFFER_LAUNCH_APPROVED`

The server validates Hotmart domains, distinct standard offer URLs, all required standard gates, seller details, and independent Last Chance gates. The special $21.90 URL must be different from the five standard offer URLs. Missing or invalid values keep checkout disabled. `/health` reports the selected provider and whether the Hotmart integration checks are operational; `status=ok` only means the web process answered.

## Hostinger deployment and domain cutover

Hostinger's current official guidance lists Business Web Hosting as supporting Node.js web apps and Express, including deployment from GitHub. Account-specific app slots, resource limits and DNS/SSL settings still need inspection inside the owner's hPanel.

When hPanel access is available:

1. Create a Node.js web app for a temporary Hostinger domain/subdomain. Use Node 20/22/24 supported by hPanel, framework Express, repository `galfredorodrigues-cmyk/gringa`, and branch `codex/her-pov-hostinger-node` (or the reviewed merged branch).
2. Build command: `npm install`; start command: `npm start`; entry file: `server.js`.
3. Keep the Hotmart checkout gates closed. Set no real seller secrets in source files.
4. Test `/`, `/last-offer`, `/upgrade`, `/terms`, `/privacy`, `/refunds`, `/contact`, all four `/sample-page/*.svg` previews, `/product-art/*.png`, and `/health` on the temporary Hostinger URL, desktop and mobile. Verify no 404/500, no sensitive PDFs exposed, and check TLS on that temporary domain.
5. Confirm app logs, resource behavior, Hostinger SSL, and custom-domain binding. Do not change `vitrinyx.com` DNS yet.
6. Only after the Hostinger copy is healthy, approved, and ready should the owner authorize a DNS switch. Keep Render unchanged until DNS, HTTPS, redirects and real device/browser smoke checks pass.
7. Future releases: commit to GitHub, review, merge/deploy the approved branch in hPanel, run the route and health checks, then promote the deployment.

Hostinger access from this automation's cloud browser is blocked by the site. No hPanel account, temporary deployment, SSL or DNS setting was changed. Therefore Hostinger compatibility is confirmed from Hostinger's published plan guidance, but this account's remaining quota/configuration and live deployment are not yet verified.

## Release validation gates

Before opening checkout, verify in Hotmart:

- All five products have been submitted and approved, with no remaining document, tax, identity, policy or product-review restriction.
- USD one-time amounts and offer-specific checkout links match the table above.
- Starter has exactly Volume 01 + Cheat Sheet; Complete $29.90 and Last Chance $21.90 each deliver the same five PDFs.
- Covers on Hotmart correspond to current approved sales-page covers; PDF page counts/content remain intact.
- Hotmart recognizes the approved payout account. The owner reports bank approval, but the financial screen last observed says documents are approved and asks to add an account, with “Por enquanto não há nada para mostrar aqui” under HotPay Brasil. Reconcile this directly in hPanel/Hotmart before setting `HOTMART_PAYOUTS_CONFIRMED=yes`.
- Seller identity, policies, tax position, refund window, customer-support inbox, payment methods and US buyer checkout are confirmed.
- Test accept/decline/direct-bundle routing and automatic file delivery using preview or a no-charge test method. Never claim successful buyer delivery unless verified without ambiguity. Do not conduct a real purchase without the owner's authorization.
- Test Hostinger deployment and temporary-domain HTTPS before any DNS change.

At the current checked state, all product records were drafts and the public Render site reported preview mode with checkout disabled. Do not set `LIVE_READY=yes`, any verification flags to `yes`, or publish an unverified checkout.
