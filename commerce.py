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
    return ("""<div style="font-family:Arial,sans-serif;max-width:580px;margin:auto">
<p style="color:#b28d55;letter-spacing:3px">HER POV</p><h2>Your First Message Formula is ready</h2>
<p>Thank you for your purchase. Both PDFs are ready for secure download.</p>
<p><a href="""" + '"' + main + '"' + """>Download your e-book</a></p>
<p><a href="""" + '"' + bonus + '"' + """>Download the bonus cheat sheet</a></p>
<p>These personal links expire 30 days after the purchase. Save your copies to your device.</p>
<p>Need help? Reply to this email. HER POV · Digital download · No subscription.</p></div>""")

def send_order_email(session):
    email = (session.get("customer_details") or {}).get("email") or session.get("customer_email")
    if not email or "@" not in email:
        raise RuntimeError("No payer email")
    if not env("RESEND_API_KEY") or not env("RESEND_FROM_EMAIL"):
        raise RuntimeError("Email sender not configured")
    payload = {"from": env("RESEND_FROM_EMAIL"), "to": [email],
               "subject": "Your HER POV e-book + free bonus",
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
        # Browser cross-origin upload requests are blocked by a required custom header.
        if request.headers.get("X-HERPOV-Upload") != "authorized":
            abort(403)
        kind=request.form.get("kind")
        f=request.files.get("file")
        if kind not in FILENAMES or not f:
            abort(400)
        data=f.read(15*1024*1024+1)
        try:
            storage.upload(kind,data)
        except (RuntimeError,ValueError):
            abort(503)
    return jsonify({"ebook":storage.exists("ebook"),"bonus":storage.exists("bonus"),
                    "storage_configured":storage.configured()})

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
