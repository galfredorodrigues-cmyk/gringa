# HER POV — fastest verified launch route

**Delivery provider: SendOwl for Stripe.** Do **not** set up Cloudflare R2, S3 or Resend for this route. Old R2/Resend code remains dormant, not needed for SendOwl.

## Already configured
- English sales funnel: https://her-pov-preview.onrender.com
- Product in existing live Stripe account Magic Universal: prod_VVIj3wtkTG7eNW
- USD $9.90 one-time price: price_1UUI8S8n16yukLPqFcJ9YTIk
- Existing live Stripe Payment Link plink_1UUIU78n16yukLPqLqyBhpjt, currently INACTIVE
- Stripe hosted confirmation mentions email delivery.
- Safe buy-button release gate in app.py (closed until every check passes).
- Owner dashboard: https://her-pov-preview.onrender.com/admin/setup
- Both original PDFs verified (56 pages and one page), included in private upload pack provided to owner.
- Legacy first-party Stripe webhook is disabled: we_1UUJd38n16yukLPqv3VwN2i0; leave disabled for SendOwl.

## One required owner authorization
Open https://marketplace.stripe.com/apps/sendowl while signed into Magic Universal Stripe.
Select Install app and review the permissions and actual offered price. Account creation and third-party installation require the owner's action, not possible using the connected Stripe API.
IMPORTANT: the SendOwl Stripe app page says a free starting plan is offered, but SendOwl's general pricing page lists paid plans from $39/month. Verify the specific plan offered and do NOT enroll in a paid plan without explicit approval.

## Product delivery inside SendOwl
1. Add a new SendOwl digital item with BOTH original PDFs attached.
2. Upload HER_POV_01_The_First_Message_Formula.pdf (56 pages).
3. Upload HER_POV_02_First_Message_Cheat_Sheet_Bonus.pdf (1 page).
4. Link the SendOwl files to existing Stripe product prod_VVIj3wtkTG7eNW. Do not duplicate this Stripe product.
5. Confirm the buyer email contains access to BOTH PDF files, secure links and sensible download limits.
6. SendOwl's Stripe App currently runs in Live mode only, not Stripe Sandboxes. Validate available testing method in account; do not accept live customer funds until full fulfillment is proven.

## Mandatory launch blockers
- Stripe payouts_enabled is currently false. Resolve directly in Stripe and verify it becomes true.
- Approve merchant identity, support contact, refund/privacy/terms policies and taxes. Current website pages are explicitly marked DRAFT.
- Verify payment-to-delivery: checkout paid, SendOwl order created, delivery email received, BOTH PDFs downloaded/opened, fraudulent/unpaid attempts denied.
- Only after verification may the owner approve these Render Environment flags:
  STRIPE_MODE=live
  SENDOWL_PRODUCT_LINKED=yes
  SENDOWL_DELIVERY_TESTED=yes
  STRIPE_PAYOUTS_CONFIRMED=yes
  MERCHANT_POLICIES_APPROVED=yes
  MERCHANT_TAX_REVIEWED=yes
  LIVE_READY=yes
- Activate the existing Stripe Payment Link only AFTER files and email are verified. The public buy button is only enabled when all flags are yes.
- No PDF files or passwords may be committed into the PUBLIC GitHub repository.

## Architecture
Stripe: payment and hosted receipt.
SendOwl: private digital file storage and buyer email/delivery.
Render: English marketing funnel, no private files.
Legacy Flask webhook / private storage functionality is unused for this SendOwl workflow. Do not configure those legacy provider secrets unless deliberately returning to that alternate approach.
