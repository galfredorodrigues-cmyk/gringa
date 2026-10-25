import os
from flask import Flask, render_template_string, render_template, jsonify
app=Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"]=False
CSS="""
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#10141b;color:#f6f0e6;font:16px/1.6 Inter,Arial,sans-serif}a{color:#d8b987}header{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #403b30;padding:17px max(5%,calc((100% - 1120px)/2));gap:24px}.brand{font-family:Georgia,serif;font-size:24px;letter-spacing:.17em;color:#d8b987;font-weight:bold}nav a{font-size:13px;letter-spacing:.08em;margin-left:16px;text-decoration:none;color:#e4d8c7}.wrap{width:min(1120px,90%);margin:auto}.hero{padding:95px 0 100px;display:grid;grid-template-columns:1.15fr .85fr;align-items:center;gap:50px}.eyebrow{color:#d8b987;font-size:11px;letter-spacing:.27em;text-transform:uppercase;font-weight:700}h1,h2,h3{font-family:Georgia,serif;line-height:1.1;font-weight:400}h1{font-size:clamp(46px,5.5vw,80px);letter-spacing:-.04em;margin:20px 0}h1 em,h2 em{color:#d8b987;font-style:normal}.lead{color:#c4bcb2;font-size:18px;max-width:560px}.tags{display:flex;gap:12px;flex-wrap:wrap;margin:28px 0}.tags span{border:1px solid #494338;color:#d8cbbc;border-radius:99px;padding:7px 13px;font-size:12px}.price{font-family:Georgia,serif;font-size:46px;color:#e6c28d}.price small{font:14px Arial,sans-serif;color:#ada99f}.button{padding:17px 30px;border-radius:40px;background:#d8b987;color:#161616;font-weight:800;letter-spacing:.06em;border:0;display:inline-block}.button.disabled{background:#3f4144;color:#c8c4b9;cursor:not-allowed}.small{font-size:12px;color:#908d87}.cover{position:relative;background:radial-gradient(ellipse,#37342e,#171b23 65%);border-radius:20px;padding:44px}.book{min-height:545px;background:linear-gradient(135deg,#262a30 0%,#070b10 60%,#383026 100%);border:1px solid #98794f;box-shadow:18px 22px 50px #000b;padding:31px 23px;text-align:center;display:flex;flex-direction:column;justify-content:space-between}.book .line{height:1px;background:#9b7953;margin:14px auto;width:90%}.book .title{font:39px/1.08 Georgia,serif}.gold{color:#d8b987}.chat{border:1px solid #88704f;background:#17191b;padding:16px;border-radius:18px;text-align:left;font-size:13px;color:#ddd}.section{padding:76px 0}.section.alt{background:#f1ebdf;color:#202020}.section h2{font-size:clamp(33px,4vw,54px);max-width:770px}.section p{max-width:760px}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}.card{padding:25px;border:1px solid #544e43;border-radius:14px}.card h3{color:#d8b987;font-size:24px}footer{padding:40px 0;border-top:1px solid #4d4336;font-size:13px;color:#b4afa6}.notice{padding:15px 22px;border:1px solid #726042;border-radius:10px;margin-top:26px;color:#e6c28d}details{border-bottom:1px solid #4c483e;padding:15px 0}summary{cursor:pointer} @media(max-width:800px){.hero{grid-template-columns:1fr;padding:45px 0}.grid{grid-template-columns:1fr 1fr}header{flex-direction:column}.cover{max-width:440px;margin:auto;width:100%}}@media(max-width:480px){.grid{grid-template-columns:1fr}.book{min-height:490px}}"""
SHELL="""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="The First Message Formula by HER POV: 50 adaptable openers, a practical C.A.R.E. framework and a free bonus cheat sheet."><title>HER POV | The First Message Formula</title><style>{{css}}</style></head><body><header><div class="brand">HER POV.</div><nav><a href="/">THE GUIDE</a><a href="/terms">TERMS</a><a href="/privacy">PRIVACY</a><a href="/refunds">REFUNDS</a></nav></header>{{body|safe}}<footer><div class="wrap">HER POV · An educational guide for adults. No guaranteed replies or outcomes. · <a href="/terms">Terms</a> · <a href="/privacy">Privacy</a> · <a href="/refunds">Refunds</a></div></footer></body></html>"""
def render(body):
    return render_template_string(SHELL,css=CSS,body=body)
@app.get("/")
def home():
    return render_template("home.html")

POLICIES={
"terms":("Terms of Use","Draft for merchant approval. HER POV provides educational digital content for adults. The guide does not guarantee any particular interaction, response or dating outcome. The purchaser receives a personal, non-transferable license to download and read the files; redistribution or resale is prohibited. The merchant's legal identity, country, contact details and applicable law must be confirmed before accepting payments."),
"privacy":("Privacy Notice","Draft for merchant approval. Once launched, customer emails and order information will be processed solely to deliver purchases, provide support, prevent fraud and meet legal obligations, subject to final processor disclosures and retention periods. The payment provider handles payment details; HER POV does not store card numbers. No marketing messages will be sent without a lawful basis. Contact information must be supplied before launch."),
"refunds":("Refund Information","Draft for merchant approval. Contact support with the purchase receipt for assistance or refund requests. Applicable statutory consumer rights are preserved. The final refund window, eligibility conditions, merchant contact and jurisdiction must be published before checkout activation.")
}
@app.get("/<policy>")
def policy(policy):
    if policy not in POLICIES:
        return "Not found",404
    name,desc=POLICIES[policy]
    return render(f'<main class="wrap section"><div class="eyebrow">HER POV · CUSTOMER POLICIES</div><h1>{name}</h1><p class="lead">{desc}</p><p><a href="/">Back to the guide</a></p></main>')
@app.get("/health")
def health():
    from commerce import readiness
    return jsonify(status="ok",live_ready=False,checkout_enabled=False,fulfillment_configured=not readiness(),mode="preview")
from commerce import register as register_delivery
register_delivery(app)
if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT","8000")))
