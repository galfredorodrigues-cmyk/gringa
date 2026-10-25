# HER POV — production delivery checklist (PT-BR)
**Status:** loja de demonstração online, sem cobranças. NÃO alterar a cobrança para ativo antes dos testes e da regularização de repasses.

## 1. Private object storage (Cloudflare R2 or S3)
Use a *private* bucket. Do NOT enable public object URLs, do NOT add PDFs to GitHub.
Set these Render environment variables from your bucket service credentials:
- S3_ENDPOINT_URL: HTTPS endpoint for the S3-compatible API (not a public download URL)
- S3_ACCESS_KEY_ID
- S3_SECRET_ACCESS_KEY
- S3_BUCKET
- S3_REGION: "auto" for R2 (or your provider region)

Owner-only upload portal after ADMIN_USERNAME and a unique 20+ character ADMIN_PASSWORD are set:
https://her-pov-preview.onrender.com/admin/assets
Upload e-book and bonus separately. Storage keys: "her-pov/volume-01/ebook.pdf" and "her-pov/volume-01/bonus.pdf".

## 2. Transactional delivery email
Verify a sender domain with Resend, then set:
- RESEND_API_KEY (in Render secrets; NEVER in GitHub)
- RESEND_FROM_EMAIL (authorized address at verified sending domain)
- SUPPORT_EMAIL
The backend uses Resend HTTPS API and a per-order Idempotency-Key to avoid duplicate email delivery during webhook retries.

## 3. Stripe configuration
Payment Link: plink_1UUIU78n16yukLPqLqyBhpjt — REAL, currently **inactive**.
Account: Magic Universal (live account acct_1UUFxK8n16yukLPq).
Product: prod_VVIj3wtkTG7eNW, price price_1UUI8S8n16yukLPqFcJ9YTIk, $9.90 USD one-time.
Payment Link is set to redirect to:
https://her-pov-preview.onrender.com/success?session_id={CHECKOUT_SESSION_ID}
A production Stripe webhook exists but is **disabled**:
we_1UUJd38n16yukLPqv3VwN2i0
https://her-pov-preview.onrender.com/webhook/stripe
Its signing secret is securely configured in Render; it was never committed.
Create a restricted live Stripe API key with checkout session READ permissions. Save as STRIPE_SECRET_KEY in Render secrets. Do not paste it in ChatGPT.
For test orders, use a separate Stripe sandbox key and TEST_PAYMENT_LINK_ID; NEVER use the live Payment Link for fake purchases.

## 4. Safety gates before activation
Review and finalize Terms, Privacy, Refund policy, merchant identity, customer support contact and taxes.
Verify Stripe payouts_enabled and charges_enabled, and resolve all payout issues.
Configure DOWNLOAD_SIGNING_SECRET (random 32+ characters, stable across redeploys).
Confirm a complete **sandbox** checkout.session.completed / async_payment_succeeded flow:
a) signed webhook accepted
b) Stripe session independently verified as paid and matching expected Payment Link
c) Resend e-mail actually delivered to a mailbox you control
d) BOTH download links work and the PDFs open
e) tampered links and unpaid sessions blocked
f) repeated webhook does not resend duplicate email.
Only after completing these checks should an authorized owner set flags:
MERCHANT_POLICIES_APPROVED=yes
MERCHANT_TAX_REVIEWED=yes
FULFILLMENT_TESTED=yes
LIVE_READY=yes
STRIPE_MODE=live
Then update storefront code from pre-launch to live state, re-enable production Stripe webhook and **last** reactivate the real Payment Link.

## Security and platform notes
The application currently keeps the buy button disabled in source code, regardless of environment flag values.
The Render free service has an ephemeral filesystem and spins down on inactivity; external private storage is required.
The GitHub repository is PUBLIC. Never commit private PDF files or credentials.
Review webhook logs, delivery logs, and failed deliveries before launch.
