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
    main = html.escape(download_link(session, "ebook"), quote=True)
    bonus = html.escape(download_link(session, "bonus"), quote=True)
    return f"""<div style="font-family:Arial,sans-serif;max-width:580px;margin:auto">
<p style="color:#b28d55;letter-spacing:3px">HER POV</p>
<h2>Your First Message Formula is ready</h2>
<p>Thank you for your purchase. Both PDFs are ready for secure download.</p>
<p><a href="{main}">Download your e-book</a></p>
<p><a href="{bonus}">Download the bonus cheat sheet</a></p>
<p>These personal links expire 30 days after purchase. Save your copies to your device.</p>
<p>Need help? Reply to this email. HER POV — Digital download — No subscription.</p>
</div>"""

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
    return render_template_string("""<!doctype html><title>HER POV | Your Downloads</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<body style="font:16px Arial;background:#11151c;color:#eee;padding:6vw">
<main style="max-width:680px;margin:auto"><h1 style="color:#d8b987">Payment confirmed.</h1>
<p>Thank you. Your digital guide and complimentary bonus are ready.</p>
<p><a style="color:#d8b987" href="{{ main }}">Download your e-book (PDF)</a></p>
<p><a style="color:#d8b987" href="{{ bonus }}">Download your bonus cheat sheet (PDF)</a></p>
<small>Links expire 30 days after purchase. Do not share them.</small></main></body>""",
         main=main, bonus=bonus)

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
    flags = {
       "S3_BUCKET": storage.configured(),
       "EBOOK": storage.exists("ebook"),
       "BONUS": storage.exists("bonus"),
       "RESEND_API_KEY": bool(env("RESEND_API_KEY")),
       "RESEND_FROM_EMAIL": bool(env("RESEND_FROM_EMAIL")),
       "SUPPORT_EMAIL": bool(env("SUPPORT_EMAIL")),
       "STRIPE_SECRET_KEY": bool(env("STRIPE_SECRET_KEY")),
       "STRIPE_WEBHOOK_SECRET": bool(env("STRIPE_WEBHOOK_SECRET")),
       "DOWNLOAD_SIGNING_SECRET": len(env("DOWNLOAD_SIGNING_SECRET")) >= 32,
    }
    return render_template_string("""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>HER POV | Owner Setup</title><style>
body{background:#11151c;color:#f5ebdb;font:16px/1.6 Arial;margin:0}
main{max-width:780px;margin:30px auto;padding:25px}
h1,h2{font-family:Georgia,serif;color:#d8b987}h1{font-size:42px}
section{border:1px solid #544b3e;border-radius:14px;margin:18px 0;padding:20px}
a{color:#ddc296}small{color:#bbb2a7}
li{margin:10px 0}strong.ok{color:#8ad6a2}strong.missing{color:#f6b77a}
code{padding:4px 7px;color:#eed0a4;background:#26282b}
</style></head><body><main>
<p>HER POV · PRIVATE OWNER DASHBOARD</p><h1>Delivery readiness</h1>
<p>The live checkout is disabled. This page only reports connection and file status, without showing your keys.</p>
<section><h2>Private storage · Cloudflare R2</h2>
<p>Bucket: <strong class="{{'ok' if flags.S3_BUCKET else 'missing'}}">{{'Configured' if flags.S3_BUCKET else 'Not connected'}}</strong></p>
<p>E-book: <strong class="{{'ok' if flags.EBOOK else 'missing'}}">{{'Uploaded' if flags.EBOOK else 'Not uploaded'}}</strong></p>
<p>Bonus: <strong class="{{'ok' if flags.BONUS else 'missing'}}">{{'Uploaded' if flags.BONUS else 'Not uploaded'}}</strong></p>
<p>Create a private R2 bucket named <code>her-pov-private-files</code> and a bucket-limited read/write S3 token.
Add these keys in your Render environment: <code>S3_ENDPOINT_URL</code>, <code>S3_ACCESS_KEY_ID</code>,
<code>S3_SECRET_ACCESS_KEY</code>, <code>S3_BUCKET</code>, <code>S3_REGION</code> (auto).</p>
<p><a href="https://dash.cloudflare.com/?to=/:account/r2/overview">Open Cloudflare R2</a> ·
<a href="/admin/assets">Upload private PDFs</a></p></section>
<section><h2>Buyer email · Resend</h2>
<p>API key: <strong class="{{'ok' if flags.RESEND_API_KEY else 'missing'}}">{{'Configured' if flags.RESEND_API_KEY else 'Not connected'}}</strong></p>
<p>Sending address: <strong class="{{'ok' if flags.RESEND_FROM_EMAIL else 'missing'}}">{{'Configured (not verified here)' if flags.RESEND_FROM_EMAIL else 'Not configured'}}</strong></p>
<p>Support address: <strong class="{{'ok' if flags.SUPPORT_EMAIL else 'missing'}}">{{'Configured' if flags.SUPPORT_EMAIL else 'Not configured'}}</strong></p>
<p>Verify the domain in your Resend account and add your sending-only API key in the Render environment as
<code>RESEND_API_KEY</code>, <code>RESEND_FROM_EMAIL</code> and <code>SUPPORT_EMAIL</code>.</p>
<p><a href="https://resend.com/domains">Resend domains</a> · <a href="https://resend.com/api-keys">Resend API keys</a></p>
<button type="button" id="test-email" style="padding:10px;background:#d8b987;color:#11151c;border:0;border-radius:6px;cursor:pointer">
Send a real test email to the support inbox</button>
<p id="email-result" role="status" aria-live="polite"></p>
<script>document.getElementById('test-email').addEventListener('click',async()=>{
const area=document.getElementById('email-result');area.textContent='Sending test...';
try{
const response=await fetch('/admin/test-email',{method:'POST',headers:{'X-HERPOV-Upload':'authorized'},
cache:'no-store',credentials:'same-origin'});
const body=await response.json();
area.textContent=body.accepted_by_provider?'Accepted by email provider. Check the support inbox: '+body.check_inbox:
(body.error || 'Sender not ready');
}catch(error){area.textContent='Request failed: '+error.message;}
});</script></section>
<section><h2>Payment protection</h2>
<ul><li>Stripe API key: {{'Present' if flags.STRIPE_SECRET_KEY else 'Not configured'}}</li>
<li>Stripe webhook signing: {{'Configured' if flags.STRIPE_WEBHOOK_SECRET else 'Missing'}}</li>
<li>Download-link signing: {{'Configured' if flags.DOWNLOAD_SIGNING_SECRET else 'Missing'}}</li>
<li>Real checkout: <strong class="missing">DISABLED — pre-launch</strong></li></ul></section>
<small>All credentials belong in Render's secure Environment screen, never GitHub, chat messages or static HTML. Connection checks do not substitute for an actual paid test order.</small>
</main></body></html>""",flags=flags)

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
