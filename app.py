import os
from flask import Flask, render_template_string, render_template, jsonify
app=Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"]=False
CSS="""
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#10141b;color:#f6f0e6;font:16px/1.6 Inter,Arial,sans-serif}a{color:#d8b987}header{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #403b30;padding:17px max(5%,calc((100% - 1120px)/2));gap:24px}.brand{font-family:Georgia,serif;font-size:24px;letter-spacing:.17em;color:#d8b987;font-weight:bold}nav a{font-size:13px;letter-spacing:.08em;margin-left:16px;text-decoration:none;color:#e4d8c7}.wrap{width:min(1120px,90%);margin:auto}.hero{padding:95px 0 100px;display:grid;grid-template-columns:1.15fr .85fr;align-items:center;gap:50px}.eyebrow{color:#d8b987;font-size:11px;letter-spacing:.27em;text-transform:uppercase;font-weight:700}h1,h2,h3{font-family:Georgia,serif;line-height:1.1;font-weight:400}h1{font-size:clamp(46px,5.5vw,80px);letter-spacing:-.04em;margin:20px 0}h1 em,h2 em{color:#d8b987;font-style:normal}.lead{color:#c4bcb2;font-size:18px;max-width:560px}.tags{display:flex;gap:12px;flex-wrap:wrap;margin:28px 0}.tags span{border:1px solid #494338;color:#d8cbbc;border-radius:99px;padding:7px 13px;font-size:12px}.price{font-family:Georgia,serif;font-size:46px;color:#e6c28d}.price small{font:14px Arial,sans-serif;color:#ada99f}.button{padding:17px 30px;border-radius:40px;background:#d8b987;color:#161616;font-weight:800;letter-spacing:.06em;border:0;display:inline-block}.button.disabled{background:#3f4144;color:#c8c4b9;cursor:not-allowed}.small{font-size:12px;color:#908d87}.cover{position:relative;background:radial-gradient(ellipse,#37342e,#171b23 65%);border-radius:20px;padding:44px}.book{min-height:545px;background:linear-gradient(135deg,#262a30 0%,#070b10 60%,#383026 100%);border:1px solid #98794f;box-shadow:18px 22px 50px #000b;padding:31px 23px;text-align:center;display:flex;flex-direction:column;justify-content:space-between}.book .line{height:1px;background:#9b7953;margin:14px auto;width:90%}.book .title{font:39px/1.08 Georgia,serif}.gold{color:#d8b987}.chat{border:1px solid #88704f;background:#17191b;padding:16px;border-radius:18px;text-align:left;font-size:13px;color:#ddd}.section{padding:76px 0}.section.alt{background:#f1ebdf;color:#202020}.section h2{font-size:clamp(33px,4vw,54px);max-width:770px}.section p{max-width:760px}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}.card{padding:25px;border:1px solid #544e43;border-radius:14px}.card h3{color:#d8b987;font-size:24px}footer{padding:40px 0;border-top:1px solid #4d4336;font-size:13px;color:#b4afa6}.notice{padding:15px 22px;border:1px solid #726042;border-radius:10px;margin-top:26px;color:#e6c28d}details{border-bottom:1px solid #4c483e;padding:15px 0}summary{cursor:pointer} @media(max-width:800px){.hero{grid-template-columns:1fr;padding:45px 0}.grid{grid-template-columns:1fr 1fr}header{flex-direction:column}.cover{max-width:440px;margin:auto;width:100%}}@media(max-width:480px){.grid{grid-template-columns:1fr}.book{min-height:490px}}"""
SHELL="""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="The First Message Formula by HER POV: 50 adaptable openers, a practical C.A.R.E. framework and a free bonus cheat sheet."><title>HER POV | The First Message Formula</title><style>{{css}}</style></head><body><header><div class="brand">HER POV.</div><nav><a href="/">THE GUIDE</a><a href="/terms">TERMS</a><a href="/privacy">PRIVACY</a><a href="/refunds">REFUNDS</a></nav></header>{{body|safe}}<footer><div class="wrap">HER POV · An educational guide for adults. No guaranteed replies or outcomes. · <a href="/terms">Terms</a> · <a href="/privacy">Privacy</a> · <a href="/refunds">Refunds</a></div></footer></body></html>"""
def render(body):
    return render_template_string(SHELL,css=CSS,body=body)
# One-switch launch gate for SendOwl. NEVER turn on until external app has
# delivered both PDFs in an actual end-to-end test and Stripe payouts are enabled.
def checkout_open():
    flags = ("SENDOWL_PRODUCT_LINKED", "SENDOWL_ALL_PRODUCTS_LINKED",
             "SENDOWL_DELIVERY_TESTED", "SENDOWL_BUNDLE_TESTED",
             "STRIPE_PAYOUTS_CONFIRMED", "STRIPE_LINKS_ACTIVE_CONFIRMED",
             "MERCHANT_POLICIES_APPROVED", "MERCHANT_TAX_REVIEWED", "LIVE_READY")
    required_merchant_fields = ("MERCHANT_LEGAL_NAME", "MERCHANT_COUNTRY",
                                "MERCHANT_CONTACT_ADDRESS", "SUPPORT_EMAIL")
    fields_complete = all(os.environ.get(name, "").strip() for name in required_merchant_fields)
    contact_email = os.environ.get("SUPPORT_EMAIL", "").strip()
    return (os.environ.get("STRIPE_MODE") == "live"
            and all(os.environ.get(flag) == "yes" for flag in flags)
            and fields_complete and "@" in contact_email
            and len(contact_email) < 256)

@app.get("/")
def home():
    ready = checkout_open()
    bundle_link = os.environ.get("BUNDLE_PAYMENT_LINK_URL", "")
    valid_bundle_link = bundle_link.startswith("https://buy.stripe.com/") and len(bundle_link) < 300
    return render_template("home.html", checkout_ready=ready,
        checkout_url="https://buy.stripe.com/14A9ANbXgfdicJXb1N3cc00",
        bundle_checkout_ready=ready and valid_bundle_link,
        bundle_checkout_url=bundle_link if valid_bundle_link else "")

# Pre-launch legal drafts: substantive buyer-facing policies with factual
# disclosures, not a substitute for legal review or verified merchant details.
LEGAL = {
    "terms": {
        "title": "Terms of Purchase & Use",
        "lead": "How the HER POV digital guides are sold, licensed, delivered and supported.",
        "sections": [
            {"heading":"The HER POV products",
             "paragraphs":["HER POV offers digital educational material for adults about starting conversations, responding with clarity, building authentic dating profiles, and navigating first-date planning. The product descriptions and prices on the checkout page determine what you buy.",
                           "The collection includes four standalone PDF guides and a Complete Library bundle. The bundle includes all four PDFs and the First Message Cheat Sheet bonus. The future AI Coach is not included in any current digital-guide purchase."],
             "points":[]},
            {"heading":"Who may purchase",
             "paragraphs":["You must be at least 18 years old and legally permitted to transact in your location. If you buy on behalf of someone else, you must have the right to use the payment method."],"points":[]},
            {"heading":"Prices, checkout & confirmation",
             "paragraphs":["Prices shown on the HER POV storefront are in US dollars (USD), generally as one-time purchases, unless a product listing expressly states otherwise. Your payment provider or issuing bank may apply currency conversion or fees. Any applicable taxes, when collected, should be disclosed before you confirm payment.",
                           "Payments are processed by Stripe. A successful charge is not a subscription enrollment. Do not submit multiple payments if a transaction appears delayed: check the purchase confirmation or contact support."],"points":[]},
            {"heading":"Digital delivery and access",
             "paragraphs":["After payment, we intend to provide access through SendOwl, which delivers the purchased digital files using the email provided at checkout. Delivery may depend on correct contact information and third-party processing availability.",
                           "Download files to your own device and store them safely. If a download is missing, corrupt or inaccessible, contact support with your order reference. We will make reasonable efforts to restore access or provide an appropriate remedy in accordance with applicable law."],"points":[]},
            {"heading":"Personal license & intellectual property",
             "paragraphs":["Purchase grants the buyer a limited, nonexclusive, nontransferable license to download and use the purchased materials for personal, noncommercial educational purposes. Copyright and ownership are not transferred."],
             "points":["Do not resell, republish, share publicly, sublicense or upload the full files to public repositories or file-sharing sites.",
                       "You may adapt an example message for your own conversations, but you may not distribute the underlying e-book or bonus as your own product."]},
            {"heading":"Educational scope and respectful use",
             "paragraphs":["These are educational guides, not professional counseling, psychological treatment, legal advice or a method of controlling other people's decisions. You remain responsible for what you say and how you treat others.",
                           "No guide can guarantee replies, matches, dates, a relationship, or improved engagement. Respect privacy, consent, boundaries and a person's decision not to respond."],"points":[]},
            {"heading":"Refunds, disputes and statutory rights",
             "paragraphs":["Read the separate Refunds & Digital Delivery policy before purchase. Nothing in these terms limits non-waivable consumer protections, payment-dispute rights or mandatory remedies available in your jurisdiction."],"points":[]},
            {"heading":"Site availability, updates and contact",
             "paragraphs":["We may correct errors or update product descriptions and these terms prospectively. Material changes affecting an existing order will be handled according to applicable law. The terms applicable to your purchase are those presented at the time of purchase.",
                           "If you need help, contact the seller using the verified details below. Merchant legal identity and contact details must be approved and published before sales open."],"points":[]},
        ]},
    "privacy":{
        "title":"Privacy Notice",
        "lead":"How order details, delivery information and support communications may be used for HER POV digital purchases.",
        "sections":[
            {"heading":"Scope and data controller",
             "paragraphs":["This notice concerns the HER POV storefront, checkout referrals, e-book delivery and support. The merchant identified below is responsible for the personal information it controls. Third-party providers may be independently responsible for certain processing under their own policies."],"points":[]},
            {"heading":"Information involved",
             "paragraphs":["Depending on how you interact with the store, relevant information can include your email address, the name you choose to provide, product selection, order identifier, purchase amount, payment status, delivery history, customer support messages and technical data needed to operate the site and prevent abuse."],
             "points":["Stripe processes payment information. The storefront is not designed to receive or store full card numbers.",
                       "SendOwl may process email, order and download-access details to fulfill digital purchases.",
                       "Render hosts the storefront and may process technical request data and routine server logs. External font services may receive technical request information when their resources load."]},
            {"heading":"Why we process information",
             "paragraphs":["We use necessary information to process and verify transactions, deliver purchased PDFs, respond to requests, protect the store against misuse or fraud, maintain records where legally necessary, and comply with legal requirements."],"points":[]},
            {"heading":"Legal grounds and communications",
             "paragraphs":["Where required by applicable law, we rely on grounds such as fulfilling the customer agreement, complying with legal obligations, legitimate operational and security interests, or valid consent. These grounds vary by jurisdiction.",
                           "Transactional receipts, downloads, access help and fraud notices are distinct from promotional marketing. Marketing communication would require a lawful basis and any consent required by your location."],"points":[]},
            {"heading":"Payments and service providers",
             "paragraphs":["The planned sales stack is Stripe for payment processing, SendOwl for secure digital product delivery and Render for website hosting. Service providers process information according to their roles and contractual terms. Visit their own privacy notices for details about processing they independently control.",
                           "We may also disclose information where legally required, to resolve a payment dispute or to protect customers and the platform from fraud."],"points":[]},
            {"heading":"International transfers, retention and security",
             "paragraphs":["Providers may process information in countries other than your home country. Required safeguards depend on the applicable jurisdiction and provider arrangements.",
                           "Records are retained only as appropriate for delivery, buyer support, accounting, fraud prevention and legal obligations; exact periods differ by data type and applicable law. No website or transmission system can guarantee absolute security."],"points":[]},
            {"heading":"Your choices and privacy rights",
             "paragraphs":["Depending on where you live, you may have rights to request access, correction, deletion, restriction, portability, objection or review of certain uses of your personal information. These rights are subject to applicable law and legal retention requirements.",
                           "To exercise a right, contact the operator using the details below. We may need reasonable verification that you are the relevant buyer, without asking for passwords or complete payment card details."],"points":[]},
            {"heading":"Cookies and website resources",
             "paragraphs":["The marketing page uses static styling and may load external font resources. Stripe and SendOwl may use cookies or similar technologies within their own payment and fulfillment interfaces. We do not represent those third-party cookies as being controlled by this site.",
                           "Any future marketing analytics, advertising tags, or nonessential tracking will require an update to this disclosure and consent controls where legally required."],"points":[]},
            {"heading":"Changes and questions",
             "paragraphs":["If practices change, this notice will be revised. Significant changes will be handled in the manner required by applicable law. Contact the verified merchant support address below with any privacy questions."],"points":[]},
        ]},
    "refunds":{
        "title":"Refunds & Digital Delivery",
        "lead":"What happens if a digital purchase is missing, defective, duplicated, or not what you expected.",
        "sections":[
            {"heading":"Digital items and order contents",
             "paragraphs":["HER POV products are downloadable educational PDFs, not physical goods. The first standalone product includes its stated one-page bonus; other guides are separate unless you buy the Complete Library bundle.",
                           "Review the product name, included files, one-time price and applicable taxes before confirming payment. The bundle contains all four HER POV guides plus the bonus."],"points":[]},
            {"heading":"How delivery works",
             "paragraphs":["After a successful Stripe payment, the SendOwl integration is intended to email a private access link to the buyer's checkout email. Please check the inbox and spam folder. Download and save your purchased files promptly."],"points":[]},
            {"heading":"A missing, broken or incorrect download",
             "paragraphs":["If the paid file does not arrive, cannot be opened, or is not the product purchased, contact customer support with the receipt or order identifier. Do not send full card details. We will investigate and offer delivery correction, restored access, replacement or a refund when required by law or appropriate under the circumstances."],"points":[]},
            {"heading":"Refund requests",
             "paragraphs":["Send your request to the verified support contact below, with your order reference, date of purchase and a brief explanation of the issue. Refunds are reviewed according to the product description, evidence of the order, payment provider rules and applicable consumer law.",
                           "We do not claim that downloading a PDF automatically removes all refund or withdrawal rights. Where your jurisdiction gives mandatory rights, those rights continue to apply. Additional discretionary refund terms will be published before the store accepts payment."],"points":[]},
            {"heading":"Duplicate payments and unauthorized charges",
             "paragraphs":["If you were charged more than once for the same order or notice a payment you did not authorize, contact support promptly. You may also contact Stripe or your card issuer through the normal dispute process. We will not ask for sensitive payment credentials to resolve an order."],"points":[]},
            {"heading":"Timing of any approved refund",
             "paragraphs":["If a refund is approved, it is submitted through the original payment provider where practicable. The time for funds to appear depends on the provider, bank, card network and relevant jurisdiction. We cannot guarantee a particular bank posting date."],"points":[]},
        ]},
    "contact":{
        "title":"Contact & Order Support",
        "lead":"Where to find help with purchases, downloads, billing and privacy requests.",
        "sections":[
            {"heading":"Support for purchases",
             "paragraphs":["Use the merchant support email listed below for missing files, incorrect delivery, questions about the purchased PDFs, billing issues or a refund request. Please keep your Stripe receipt and order reference for verification."],
             "points":["For a missing download, describe the product purchased and the message or error you saw.",
                       "For billing concerns, include the transaction date and order identifier.",
                       "For data/privacy requests, describe what information you are asking about. Do not include passwords or full card details."]},
            {"heading":"Pre-launch availability",
             "paragraphs":["The HER POV storefront is currently in preview mode. Purchases are not yet available. An official seller name and support contact will be published before any real checkout is opened."],"points":[]},
        ]},
}
@app.get("/terms")
@app.get("/privacy")
@app.get("/refunds")
@app.get("/contact")
def policy():
    from flask import request
    name = request.path.lstrip("/")
    info = LEGAL.get(name)
    if info is None:
        return "Not found", 404
    contact = os.environ.get("SUPPORT_EMAIL", "").strip()
    if contact and ("@" not in contact or len(contact)>255):
        contact = ""
    merchant = os.environ.get("MERCHANT_LEGAL_NAME", "").strip()[:200]
    country = os.environ.get("MERCHANT_COUNTRY", "").strip()[:100]
    address = os.environ.get("MERCHANT_CONTACT_ADDRESS", "").strip()[:350]
    return render_template("legal.html", title=info["title"], lead=info["lead"],
                           sections=info["sections"], support_email=contact,
                           legal_name=merchant, merchant_country=country,
                           merchant_address=address, ready=checkout_open())

@app.get("/health")
def health():
    enabled = checkout_open()
    return jsonify(status="ok", live_ready=enabled,
                   checkout_enabled=enabled,
                   delivery_provider="sendowl",
                   mode="live" if enabled else "preview")
from commerce import register as register_delivery
register_delivery(app)
if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT","8000")))
