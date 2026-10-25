"""HER POV: Stripe verified purchases, private PDF delivery, secure email.
Payment link remains disabled in Stripe until an actual end-to-end test.
"""
import os
import re
import hmac
import time
import html
import json
import hashlib
import logging
from urllib.parse import urlencode
from flask import Blueprint, request, jsonify, abort, send_file, render_template_string
import requests
import stripe
import private_storage as storage

bp = Blueprint("delivery", __name__)
AMOUNT = 990
CURRENCY = "usd"
LINK_ID = "plink_1UUIU78n16yukLPqLqyBhpjt"
PRICE_ID = "price_1UUI8S8n16yukLPqFcJ9YTIk"
MAX_DAYS = 30 * 24 * 60 * 60
log = logging.getLogger("herpov.delivery")
FILENAMES = {"ebook": "HER_POV_The_First_Message_Formula.pdf",
             "bonus": "HER_POV_First_Message_Cheat_Sheet.pdf"}

def env(name):
    return os.getenv(name, "").strip()

def readiness():
    """Truthful production readiness, no secret exposure."""
    required = ["STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET", "DOWNLOAD_SIGNING_SECRET",
                "RESEND_API_KEY", "RESEND_FROM_EMAIL", "SUPPORT_EMAIL",
                "MERCHANT_LEGAL_NAME", "MERCHANT_CONTACT_ADDRESS"]
    missing = [x for x in required if not env(x)]
    if env("STRIPE_MODE") != "live":
        missing.append("STRIPE_MODE=live")
    if not env("STRIPE_SECRET_KEY").startswith(("rk_live_", "sk_live_")):
        missing.append("Stripe live restricted key")
    if not env("STRIPE_WEBHOOK_SECRET").startswith("whsec_"):
        missing.append("Verified webhook signing secret")
    if len(env("DOWNLOAD_SIGNING_SECRET")) < 32:
        missing.append("Strong signing key (32+ characters)")
    if not env("RESEND_API_KEY").startswith("re_"):
        missing.append("Email provider API key")
    if "@" not in env("RESEND_FROM_EMAIL"):
        missing.append("Verified sender domain")
    if not env("PUBLIC_BASE_URL").startswith("https://"):
        missing.append("HTTPS public base URL")
    if not storage.configured():
        missing.append("Private S3/R2 bucket credentials")
    else:
        for kind in FILENAMES:
            if not storage.exists(kind):
                missing.append("Private PDF object missing: " + kind)
    for flag in ["MERCHANT_POLICIES_APPROVED", "MERCHANT_TAX_REVIEWED",
                 "FULFILLMENT_TESTED", "LIVE_READY"]:
        if env(flag) != "yes":
            missing.append(flag + "=yes")
    return list(dict.fromkeys(missing))

def stripe_client():
    key = env("STRIPE_SECRET_KEY")
    mode = env("STRIPE_MODE")
    if not key or (mode == "live" and not key.startswith(("rk_live_", "sk_live_"))) or (
        mode == "test" and not key.startswith(("rk_test_", "sk_test_"))):
        raise RuntimeError("Stripe server credentials missing or wrong mode")
    return stripe.StripeClient(key)

def verify_session(sid):
    if not re.fullmatch(r"cs_(test_)?[A-Za-z0-9]{8,128}", sid or ""):
        return None
    session = stripe_client().v1.checkout.sessions.retrieve(sid)
    if session.get("status") != "complete" or session.get("payment_status") != "paid":
        return None
    expected_link = env("TEST_PAYMENT_LINK_ID") if env("STRIPE_MODE") == "test" else LINK_ID
    if not expected_link or session.get("payment_link") != expected_link:
        return None
    if session.get("currency") != CURRENCY or session.get("amount_total") != AMOUNT:
        return None
    if bool(session.get("livemode")) != (env("STRIPE_MODE") == "live"):
        return None
    return session

def signature(session_id, kind, expiry):
    secret = env("DOWNLOAD_SIGNING_SECRET")
    if len(secret) < 32:
        raise RuntimeError("Signing not configured")
    payload = f"{session_id}|{kind}|{expiry}".encode()
    return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

def download_link(session, kind):
    created = int(session["created"])
    expiry = created + MAX_DAYS
    params = urlencode({"sid": session["id"], "kind": kind,
                        "exp": expiry, "sig": signature(session["id"], kind, expiry)})
    return f'{env("PUBLIC_BASE_URL").rstrip("/")}/download?{params}'

def delivery_html(session):
    """Responsive transaction-only email. Contains private, signed, per-order links."""
    main = html.escape(download_link(session, "ebook"), quote=True)
    bonus = html.escape(download_link(session, "bonus"), quote=True)
    support = html.escape(env("SUPPORT_EMAIL") or env("RESEND_FROM_EMAIL"), quote=True)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>HER POV: Your Digital Edition</title>
</head><body style="background:#eae4dc;margin:0;padding:35px 10px;font-family:Arial,sans-serif;color:#19202a">
<table role="presentation" cellspacing="0" cellpadding="0" border="0" style="max-width:600px;margin:auto;background:#f9f6f0;width:100%;border-collapse:collapse">
<tr><td style="background:#10151d;color:#e3c18a;padding:28px 35px;border-bottom:2px solid #b28d55">
<span style="font:30px Georgia,serif;letter-spacing:-1px">HER POV.</span>
<span style="display:block;margin-top:8px;color:#b7aba0;font:bold 10px Arial,sans-serif;letter-spacing:2px">VOL. 01 / YOUR DIGITAL EDITION</span>
</td></tr>
<tr><td style="padding:38px 35px 26px">
<p style="margin:0;color:#a27c43;font:bold 10px Arial,sans-serif;letter-spacing:2px">PAYMENT CONFIRMED / READY TO DOWNLOAD</p>
<h1 style="font:39px/1.1 Georgia,serif;letter-spacing:-1px;margin:15px 0;color:#1d232c">Your next conversation starts here.</h1>
<p style="font:16px/1.7 Arial,sans-serif;color:#595853">
Thank you for getting <strong>The First Message Formula</strong>.
Your complete guide and complimentary one-page reference are ready.</p>
</td></tr>
<tr><td style="padding:0 35px 24px">
<table role="presentation" width="100%" style="border:1px solid #e2d7c6;border-collapse:collapse">
<tr><td style="padding:19px;background:#fff">
<p style="font:bold 10px Arial,sans-serif;letter-spacing:1.5px;color:#a57f48;margin:0 0 8px">01 / THE MAIN GUIDE</p>
<strong style="font:23px Georgia,serif;color:#20252d">The First Message Formula</strong>
<p style="font:13px Arial,sans-serif;color:#696760;margin:7px 0 17px">56-page PDF · 8 chapters · 50 adaptable openers</p>
<a href="{main}" style="background:#10151d;color:#f2d6a1;padding:13px 19px;display:inline-block;text-decoration:none;font:bold 12px Arial,sans-serif">DOWNLOAD YOUR E-BOOK ↗</a></td></tr></table>
</td></tr>
<tr><td style="padding:0 35px 28px">
<table role="presentation" width="100%" style="border:1px solid #e2d7c6;border-collapse:collapse">
<tr><td style="padding:19px;background:#fff">
<p style="font:bold 10px Arial,sans-serif;letter-spacing:1.5px;color:#a57f48;margin:0 0 8px">02 / THE COMPLIMENTARY BONUS</p>
<strong style="font:23px Georgia,serif;color:#20252d">First Message Cheat Sheet</strong>
<p style="font:13px Arial,sans-serif;color:#696760;margin:7px 0 17px">One-page quick reference PDF · included at no extra charge</p>
<a href="{bonus}" style="background:#d8b987;color:#162029;padding:13px 19px;display:inline-block;text-decoration:none;font:bold 12px Arial,sans-serif">DOWNLOAD YOUR BONUS ↗</a></td></tr></table>
</td></tr>
<tr><td style="padding:4px 35px 30px">
<p style="font:13px/1.7 Arial,sans-serif;color:#6a6661">These private links expire <strong>30 days after purchase</strong>.
Save both PDFs to your device. Do not forward these personal links.</p>
<div style="background:#eae1d3;padding:17px 19px;margin:25px 0">
<p style="font:bold 10px Arial,sans-serif;letter-spacing:1px;color:#8b704c;margin:0 0 6px">WHAT COMES NEXT</p>
<strong style="font:22px Georgia,serif;color:#20252d">The Reply Decoder</strong>
<p style="font:13px/1.6 Arial,sans-serif;color:#6b675f;margin:9px 0 0">A future HER POV guide for navigating replies with more clarity.
Coming later — not included in this purchase.</p></div>
<p style="font:13px Arial,sans-serif;color:#6a6661">Need help with your purchase?
<a href="mailto:{support}" style="color:#8b704c">Contact HER POV support</a>.</p>
</td></tr>
<tr><td style="background:#10151d;color:#aaa9a4;padding:23px 35px;font:11px/1.7 Arial,sans-serif">
HER POV · Educational content for adults. One-time purchase, no subscription.
No guarantee of responses, attraction or dating outcomes.
</td></tr></table>
</body></html>"""

def send_order_email(session):
    email = (session.get("customer_details") or {}).get("email") or session.get("customer_email")
    if not email or "@" not in email:
        raise RuntimeError("No payer email")
    if not env("RESEND_API_KEY") or not env("RESEND_FROM_EMAIL"):
        raise RuntimeError("Email sender not configured")
    payload = {"from": env("RESEND_FROM_EMAIL"), "to": [email],
               "subject": "Your HER POV e-book + free bonus",
               "reply_to": env("SUPPORT_EMAIL") or env("RESEND_FROM_EMAIL"),
               "html": delivery_html(session)}
    r = requests.post("https://api.resend.com/emails", json=payload,
                      headers={"Authorization": "Bearer " + env("RESEND_API_KEY"),
                               "Idempotency-Key": "her-pov-order-"+session["id"]},
                      timeout=15)
    r.raise_for_status()
    return r.json().get("id", "")

@bp.post("/webhook/stripe")
def webhook():
    secret = env("STRIPE_WEBHOOK_SECRET")
    if not secret:
        return jsonify(error="Webhook not configured"), 503
    try:
        event = stripe.Webhook.construct_event(request.get_data(cache=False),
                 request.headers.get("Stripe-Signature", ""), secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        return jsonify(error="Invalid signature"), 400
    if event["type"] not in ("checkout.session.completed", "checkout.session.async_payment_succeeded"):
        return jsonify(ignored=True), 200
    sid = event["data"]["object"]["id"]
    try:
        session = verify_session(sid)
        if session is None:
            return jsonify(ignored="Session not paid, wrong product, or wrong account"), 200
        if not storage.configured() or not all(storage.exists(k) for k in FILENAMES):
            raise RuntimeError("PDF assets unavailable")
        if env("STRIPE_MODE") == "test" and env("ALLOW_SANDBOX_EMAILS") != "yes":
            return jsonify(verified=True, email="sandbox_disabled"), 200
        mail_id = send_order_email(session)
        return jsonify(delivered=True, message_id=mail_id), 200
    except Exception as e:
        log.error("Fulfillment failure: %s", type(e).__name__)
        return jsonify(error="Fulfillment unavailable; event should retry"), 503

@bp.get("/success")
def success():
    sid = request.args.get("session_id", "")
    try:
        session = verify_session(sid)
    except Exception:
        session = None
    if not session:
        return "Payment not verified. If you paid, please check your email receipt.", 403
    if int(session["created"]) + MAX_DAYS <= time.time():
        return "Download period expired. Please contact support.", 410
    main = download_link(session, "ebook")
    bonus = download_link(session, "bonus")
    return render_template_string("""<!doctype html><html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><meta name="referrer" content="no-referrer">
<title>HER POV — Your Purchase Is Ready</title>
<style>:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#10151d;color:#f4ede3;font:16px/1.65 Arial,sans-serif}
main{max-width:790px;padding:40px 22px 90px;margin:auto}.logo{font:30px Georgia,serif;color:#d8b987}
.header{display:flex;justify-content:space-between;align-items:center;margin:0 0 65px;border-bottom:1px solid #3d4144;padding-bottom:20px}
.hint{font-size:11px;letter-spacing:.14em;color:#d8b987;font-weight:700}
h1,h2{font-family:Georgia,serif;font-weight:400}h1{font-size:clamp(43px,8vw,67px);line-height:1.08;margin:18px 0}
h2{font-size:32px}h1 em{font-style:italic;color:#d8b987}.lead{color:#bfc0bc;font-size:18px}
.files{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:42px 0}.file{border:1px solid #6b5840;padding:26px 22px;background:#1d242e;min-width:0}
.file strong{font:25px/1.15 Georgia,serif;display:block;margin:12px 0;color:#f5e2c0}.file small{display:block;font-size:12px;color:#aaa8a3}.file a{display:inline-block;background:#d8b987;color:#131922;font-weight:800;text-decoration:none;font-size:12px;
padding:14px 17px;margin-top:24px}.note{padding:20px 24px;border:1px solid #49463e;color:#b8b8b2;font-size:13px;line-height:1.6}
.next{margin-top:45px;padding:24px 27px;background:#f2ebe0;color:#252522}.next h2{margin:12px 0}.next p{color:#59554c}.next small{letter-spacing:.1em;color:#88734d}
footer{font-size:11px;color:#929390;margin-top:45px}@media(max-width:520px){.files{grid-template-columns:1fr}.header{margin-bottom:35px}}
</style></head><body><main><div class="header"><span class="logo">HER POV.</span><span class="hint">VOL. 01 / YOUR LIBRARY</span></div>
<p class="hint">PAYMENT CONFIRMED</p><h1>Your next message starts <em>here.</em></h1>
<p class="lead">Thank you for your purchase. Your e-book and complimentary quick-reference sheet are ready to save.</p>
<div class="files"><div class="file"><small>01 / YOUR MAIN GUIDE</small>
<strong>The First Message Formula</strong><small>56-page digital PDF</small>
<a href="{{ main }}">DOWNLOAD YOUR GUIDE ↗</a></div>
<div class="file"><small>02 / YOUR FREE BONUS</small>
<strong>First Message Cheat Sheet</strong><small>One-page quick reference PDF</small>
<a href="{{ bonus }}">DOWNLOAD YOUR BONUS ↗</a></div></div>
<div class="note">These personal links are valid for 30 days after your purchase. Save the PDFs to your device for future reference.
For help with your order, contact the support address shown on your payment receipt. Please do not share your personal links.</div>
<div class="next"><small>WHAT COMES NEXT / THE HER POV SERIES</small>
<h2>The Reply Decoder</h2><p>Our next planned guide explores how to think more clearly about replies and avoid overanalyzing the conversation.
It's currently in development and is not included in your purchase.</p></div>
<footer>HER POV · Digital edition · No guaranteed replies, dates, or romantic outcomes.</footer>
</main></body></html>""",main=main,bonus=bonus)


@bp.get("/download")
def download():
    sid = request.args.get("sid", "")
    kind = request.args.get("kind", "")
    try:
        expiry = int(request.args.get("exp", "0"))
    except ValueError:
        abort(403)
    if kind not in FILENAMES or expiry <= time.time() or expiry > time.time()+MAX_DAYS+120:
        abort(403)
    if len(env("DOWNLOAD_SIGNING_SECRET")) < 32:
        abort(503)
    if not hmac.compare_digest(request.args.get("sig",""), signature(sid,kind,expiry)):
        abort(403)
    try:
        session = verify_session(sid)
    except Exception:
        abort(503)
    if not session or expiry != int(session["created"])+MAX_DAYS:
        abort(403)
    try:
        buffer = storage.read(kind)
    except Exception:
        abort(503)
    return send_file(buffer, mimetype="application/pdf", as_attachment=True,
                     download_name=FILENAMES[kind], max_age=0, conditional=False)

def admin_auth():
    from base64 import b64decode
    user=env("ADMIN_USERNAME")
    pwd=env("ADMIN_PASSWORD")
    auth=request.headers.get("Authorization","")
    if not user or len(pwd)<20 or not auth.startswith("Basic "):
        return False
    try:
        u,p=b64decode(auth[6:],validate=True).decode().split(":",1)
    except (ValueError, UnicodeError):
        return False
    return hmac.compare_digest(user,u) and hmac.compare_digest(pwd,p)

@bp.route("/admin/assets", methods=["GET","POST"])
def admin_assets():
    if not admin_auth():
        return ("Owner credentials required",401,{"WWW-Authenticate":'Basic realm="HER POV private files"'})
    if request.method=="POST":
        # Cross-origin uploads cannot provide this custom header without CORS.
        if request.headers.get("X-HERPOV-Upload") != "authorized":
            abort(403)
        kind=request.form.get("kind")
        f=request.files.get("file")
        if kind not in FILENAMES or not f:
            abort(400)
        data=f.read(15*1024*1024+1)
        try:
            storage.upload(kind,data)
        except ValueError:
            abort(400)
        except Exception:
            abort(503)
        return jsonify(uploaded=kind, verified=storage.exists(kind))
    checks={name:storage.exists(name) for name in FILENAMES}
    return render_template_string("""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>HER POV · Owner Files</title>
<style>body{background:#11151c;color:#f3ebdf;font:16px Arial;margin:0}
main{max-width:680px;margin:7vh auto;padding:26px}h1{font:40px Georgia;color:#d8b987}
small{color:#c3b5a1}label{display:block;margin:20px 0 8px}
select,input,button{padding:14px;background:#232932;color:white;border:1px solid #7d6e59;border-radius:6px;max-width:100%;width:100%}
button{background:#d8b987;color:#11151c;cursor:pointer;font-weight:bold}
fieldset{border:1px solid #5d5344;border-radius:9px;margin:20px 0;padding:18px}li{margin:12px 0}
em{color:#d8b987;font-style:normal}</style></head>
<body><main><h1>HER POV · Private delivery</h1><p>Owner-only protected PDF upload. Files are stored in your private S3/R2 bucket, never in the public site.</p>
<fieldset><legend>Storage status</legend><p>Bucket: <em>{{ "Connected" if connected else "Not configured" }}</em></p>
<ul><li>E-book: <em>{{ "Available" if checks.ebook else "Missing" }}</em></li>
<li>Bonus: <em>{{ "Available" if checks.bonus else "Missing" }}</em></li></ul></fieldset>
<form id="upload"><label for="kind">Document</label>
<select id="kind" name="kind"><option value="ebook">56-page e-book</option>
<option value="bonus">Bonus cheat sheet</option></select>
<label for="file">PDF file (15 MB maximum)</label><input id="file" name="file" type="file" accept=".pdf,application/pdf" required>
<p><button type="submit" {{ "disabled" if not connected }}>Securely upload PDF</button></p>
<p id="feedback" role="status" aria-live="polite"></p></form>
<small>Upload each PDF once. Never publish these documents in GitHub or public storage.</small>
<script>document.getElementById('upload').addEventListener('submit', async function(ev){
ev.preventDefault(); const feedback=document.getElementById('feedback');feedback.textContent='Uploading…';
try{const result=await fetch('/admin/assets',{method:'POST',body:new FormData(ev.target),
headers:{'X-HERPOV-Upload':'authorized'},cache:'no-store',credentials:'same-origin'});
if(!result.ok)throw Error('Upload rejected ('+result.status+')');
const info=await result.json();feedback.textContent=info.verified?'Document uploaded and verified.':'Upload incomplete.';}
catch(e){feedback.textContent=e.message;}
});</script>
</main></body></html>""",connected=storage.configured(),checks=checks)

@bp.get("/admin/setup")
def admin_setup():
    if not admin_auth():
        return ("Owner credentials required", 401,
                {"WWW-Authenticate": 'Basic realm="HER POV private setup"'})
    flags = (
        ("SENDOWL_PRODUCT_LINKED", "Both PDFs are linked to the existing Stripe product"),
        ("SENDOWL_DELIVERY_TESTED", "Full payment-to-email-to-download delivery was verified"),
        ("STRIPE_PAYOUTS_CONFIRMED", "Stripe payouts are enabled (account reviewed)"),
        ("MERCHANT_POLICIES_APPROVED", "Merchant information and buyer policies approved"),
        ("MERCHANT_TAX_REVIEWED", "Required taxes and registrations reviewed"),
        ("STRIPE_MODE", "Stripe integration set to live for launch"),
        ("LIVE_READY", "Final owner launch approval"),
    )
    passed = {key for key, label in flags if
              (env(key) == "live" if key == "STRIPE_MODE" else env(key) == "yes")}
    checkout_ready = len(passed) == len(flags)
    from flask import render_template
    return render_template("admin_delivery.html", flags=flags,
                           passed=passed, checkout_ready=checkout_ready)

@bp.post("/admin/test-email")
def test_delivery_email():
    """Owner-only transactional email readiness test; never sends paid links."""
    if not admin_auth():
        return ("Owner credentials required",401,{"WWW-Authenticate":'Basic realm="HER POV owner"'})
    if request.headers.get("X-HERPOV-Upload") != "authorized":
        abort(403)
    api_key=env("RESEND_API_KEY")
    sender=env("RESEND_FROM_EMAIL")
    recipient=env("SUPPORT_EMAIL")
    if not api_key.startswith("re_") or "@" not in sender or "@" not in recipient:
        return jsonify(sent=False,error="Resend API key, verified sender and support inbox are required"),503
    from datetime import datetime, timezone
    date=datetime.now(timezone.utc).strftime("%Y-%m-%d")
    payload={"from":sender,"to":[recipient],
             "subject":"HER POV — Transactional Email Test",
             "reply_to":recipient,
             "html":("<p><strong>HER POV test successful.</strong></p>"
                     "<p>Your transactional email integration accepted a delivery request.</p>"
                     "<p>This is a configuration test only, not an order or a paid download.</p>")}
    try:
        response=requests.post("https://api.resend.com/emails",
            json=payload,timeout=15,
            headers={"Authorization":"Bearer "+api_key,
                     "Idempotency-Key":"her-pov-owner-verification-"+date})
        response.raise_for_status()
    except requests.RequestException as e:
        log.error("Resend test failed: %s",type(e).__name__)
        return jsonify(sent=False,error="Email provider rejected test; verify domain and API key"),502
    return jsonify(accepted_by_provider=True,
                   check_inbox=recipient,
                   message_id=response.json().get("id"),
                   note="Provider acceptance does not confirm mailbox delivery.")

@bp.get("/_status")
def owner_status():
    if not admin_auth():
        abort(401)
    return jsonify({"ready":not readiness(),"missing":readiness()})

def register(app):
    app.register_blueprint(bp)
    @app.after_request
    def protect_delivery(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Frame-Options"] = "DENY"
        return response
