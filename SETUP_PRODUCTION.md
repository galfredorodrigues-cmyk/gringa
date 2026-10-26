# HER POV production setup

## Current architecture

- GitHub repository: `galfredorodrigues-cmyk/gringa` (source of truth).
- Public production: Hostinger Business, Node 20 / Express. The app renders the existing Jinja templates with Nunjucks and retains the approved HTML/CSS design and the `/`, `/last-offer`, `/upgrade`, legal, preview-art, and `/health` routes. Do not serve buyer PDFs from the public site.
- Existing fallback: the Flask app remains on Render, but public DNS now points to Hostinger.
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

On 2026-10-26, all five products showed **Vendas ativas** in Hotmart. The three relevant checkout pages were opened without entering buyer data or submitting an order: Starter displayed $9.90, the Complete Library offer displayed $29.90, and the Last Chance offer displayed $21.90 as a total for the same full library. Hotmart's direct checkout pages are live and chargeable. The website continues to keep its buttons gated in preview mode.

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

Hostinger Business has one app deployed and uses 20% of plan resources. The production app was uploaded as `her-pov-hostinger-fixed.zip` and uses Node 20 / Express. The custom domain `vitrinyx.com` (with “y”; the account-registered domain) is now connected to this app. hPanel shows SSL and CDN active. Automatic GitHub deployment is not connected; GitHub `main` remains the source of truth, and future releases must be uploaded/redeployed through hPanel until a Git deployment is explicitly connected.

For this Hostinger app:

1. The production Node app is already deployed and bound to `vitrinyx.com`.
2. The DNS cutover is complete: apex ALIAS and `www` CNAME point to Hostinger CDN targets; the old Render `www` CNAME was removed. Hostinger hPanel shows SSL and CDN active.
3. Keep the Hotmart checkout gates closed until delivery, policy, tax, seller identity and support details are confirmed.
4. Production `/` and `/last-offer` load with the approved design; `/health` reports Hotmart and the fail-closed preview state. Legal, sample-art and health routes had been checked on the temporary app before cutover. Mobile performance testing did not produce a result and remains unverified.
5. Keep Render running as a fallback, but do not expect the public domain to use it while DNS remains on Hostinger.
6. Future releases: commit to GitHub `main`, update/redeploy the Hostinger app via hPanel, and repeat route, health, HTTPS and device checks. The app is not yet configured for automatic GitHub deploys.

The initial temporary app `dodgerblue-seal-706434.hostingersite.com` returned 503 because Hostinger imports the entry file. The server fix uses `HOSTINGER_MANAGED_NODE=yes`. After redeployment, Hostinger logs reported zero errors. The account-registered custom domain was then connected and the public DNS was moved to Hostinger. On 2026-10-26, `https://www.vitrinyx.com/health` returned `checkout_provider=hotmart`, `delivery_provider=hotmart`, `integration_operational=false`, `checkout_enabled=false`, `live_ready=false`, and `mode=preview`. The home and Last Chance pages rendered on the custom domain with the approved design and disabled payment buttons. hPanel shows SSL and CDN active. The temporary hostname no longer serves the app after custom-domain binding.

## Release validation gates

Before opening checkout, verify in Hotmart:

- All five products currently show active sales; confirm there is no separate account-level document, tax, identity or policy restriction before launch.
- USD one-time amounts and offer-specific checkout links match the table above.
- Starter has exactly Volume 01 + Cheat Sheet; Complete $29.90 and Last Chance $21.90 each deliver the same five PDFs.
- Covers on Hotmart correspond to current approved sales-page covers; PDF page counts/content remain intact.
- The seller confirms the bank account is approved; `HOTMART_PAYOUTS_CONFIRMED=yes` is set in hPanel.
- `HOTMART_DELIVERY_TESTED=no` and `LAST_OFFER_DELIVERY_TESTED=no`: Hotmart producer previews and checkout inspection do not prove the post-payment email/access path. Hotmart's buyer help says access instructions are emailed after an order is approved, but no HER POV buyer order was tested. No purchase was made.
- `MERCHANT_POLICIES_APPROVED=no` and `LAST_OFFER_POLICIES_APPROVED=no`; `MERCHANT_TAX_REVIEWED=no`; `LIVE_READY=no`; `LAST_OFFER_LAUNCH_APPROVED=no`.
- Hotmart's tax rules currently classify the Complete Library as ESS (ebook) and as a product with no educational content. The PDFs are educational guides, so have a tax professional review the second classification and the applicable sales regions before changing it. The Hotmart wizard was opened for inspection and closed without saving changes.
- Public Hotmart checkout still shows author `Magic Wolf`, while the account public profile is set to HER POV. Seller/legal name, mailing address and a verified support inbox have not been supplied for publication.
- The Hostinger public domain uses valid HTTPS according to hPanel. Mobile speed checks did not return a result. No real purchase or payment test was made.

At the current checked state, all five product records show active sales, and the configured checkout URLs and USD totals match the plan. Direct Hotmart checkouts are live/chargeable, while the website buttons remain disabled by `LIVE_READY=no`. Do not open the website checkouts, claim delivery was tested, or remove the preview notice until post-payment delivery, seller contact/legal details, policy approval, tax review and the public-name mismatch are resolved.
