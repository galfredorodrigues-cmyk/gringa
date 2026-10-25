import os
import time
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault("STRIPE_MODE", "test")
os.environ.setdefault("DOWNLOAD_SIGNING_SECRET", "unit-test-key-not-for-production-" + "x"*40)
os.environ.setdefault("PUBLIC_BASE_URL", "https://example.test")
os.environ.setdefault("TEST_PAYMENT_LINK_ID", "plink_test_private_ci")
import app
import commerce
import private_storage

class StorefrontTests(unittest.TestCase):
    def setUp(self):
        app.app.testing = True
        self.client=app.app.test_client()
        self.created=int(time.time()) - 60
        self.session={
            "id":"cs_test_123456789ABCDEFG", "created":self.created,
            "payment_status":"paid", "status":"complete","currency":"usd",
            "amount_total":990, "payment_link":"plink_test_private_ci",
            "livemode":False, "customer_details":{"email":"buyer@example.test"}}

    def test_storefront_preview_cannot_charge(self):
        page=self.client.get("/")
        self.assertEqual(page.status_code,200)
        self.assertIn(b"CHECKOUT OPENING SOON",page.data)
        self.assertNotIn(b"https://buy.stripe.com/14A9AN",page.data)

    def test_sendowl_launch_requires_every_independent_approval(self):
        ready = {
            "STRIPE_MODE": "live",
            "SENDOWL_PRODUCT_LINKED": "yes",
            "SENDOWL_ALL_PRODUCTS_LINKED": "yes",
            "SENDOWL_BUNDLE_TESTED": "yes",
            "SENDOWL_DELIVERY_TESTED": "yes",
            "STRIPE_PAYOUTS_CONFIRMED": "yes",
            "MERCHANT_POLICIES_APPROVED": "yes",
            "MERCHANT_TAX_REVIEWED": "yes",
            "LIVE_READY": "yes",
        }
        with patch.dict(os.environ, ready):
            self.assertTrue(app.checkout_open())
            html = self.client.get("/").data
            self.assertIn(b"GET INSTANT ACCESS", html)
            self.assertIn(b"buy.stripe.com", html)
            assert self.client.get("/health").get_json()["checkout_enabled"] is True
        for missing in ready:
            unsafe = dict(ready)
            unsafe[missing] = "no"
            with patch.dict(os.environ, unsafe):
                self.assertFalse(app.checkout_open(), missing)
                self.assertIn(b"CHECKOUT OPENING SOON", self.client.get("/").data)
                self.assertNotIn(b"buy.stripe.com", self.client.get("/").data)

    def test_bundle_payment_url_needs_valid_link_and_every_approval(self):
        ready = {
            "STRIPE_MODE":"live",
            "SENDOWL_PRODUCT_LINKED":"yes",
            "SENDOWL_ALL_PRODUCTS_LINKED":"yes",
            "SENDOWL_BUNDLE_TESTED":"yes",
            "SENDOWL_DELIVERY_TESTED":"yes",
            "STRIPE_PAYOUTS_CONFIRMED":"yes",
            "MERCHANT_POLICIES_APPROVED":"yes",
            "MERCHANT_TAX_REVIEWED":"yes",
            "LIVE_READY":"yes",
        }
        url = "https://buy.stripe.com/test-bundle-private-ci"
        with patch.dict(os.environ, {**ready,"BUNDLE_PAYMENT_LINK_URL":url}):
            self.assertIn(b"GET ALL 4 GUIDES",self.client.get("/").data)
            self.assertIn(url.encode(),self.client.get("/").data)
            with patch.dict(os.environ,{"LIVE_READY":"no"}):
                self.assertIn(b"BUNDLE CHECKOUT OPENING SOON",self.client.get("/").data)
                self.assertNotIn(url.encode(),self.client.get("/").data)
            with patch.dict(os.environ,{"BUNDLE_PAYMENT_LINK_URL":"https://example.net/wrong"}):
                self.assertIn(b"BUNDLE CHECKOUT OPENING SOON",self.client.get("/").data)
                self.assertNotIn(b"example.net/wrong",self.client.get("/").data)

    def test_legal_pages_provide_substantive_prelaunch_disclosures(self):
        for path, phrase in [
            ("/terms", b"Terms of Purchase"),
            ("/privacy", b"Privacy Notice"),
            ("/refunds", b"Refunds &amp; Digital Delivery"),
            ("/contact", b"Contact &amp; Order Support"),
        ]:
            response=self.client.get(path)
            self.assertEqual(response.status_code, 200, path)
            self.assertIn(phrase, response.data, path)
            self.assertIn(b"Pre-launch policy notice", response.data)
            self.assertIn(b"Operator &amp; contact", response.data)
            self.assertIn(b"HER POV", response.data)
        self.assertIn(b"Contact &amp; Support",self.client.get("/").data)

    def test_legal_contact_stays_unverified_until_owner_confirms(self):
        with patch.dict(os.environ,{"MERCHANT_LEGAL_NAME":"Example Company LLC",
                                   "MERCHANT_COUNTRY":"United States",
                                   "MERCHANT_CONTACT_ADDRESS":"123 Placeholder Street",
                                   "SUPPORT_EMAIL":"help@example.test"}):
            html=self.client.get("/privacy").data
            self.assertIn(b"Example Company LLC",html)
            self.assertIn(b"help@example.test",html)
            self.assertIn(b"Pre-launch policy notice",html)

    def test_health_and_no_live_claim(self):
        response=self.client.get("/health")
        self.assertEqual(response.status_code,200)
        self.assertFalse(response.get_json()["checkout_enabled"])

    def test_reject_unsigned_webhook(self):
        with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET":"whsec_fake_ci"}, clear=False):
            r=self.client.post("/webhook/stripe",data=b'{"x": 1}',headers={"Stripe-Signature":"t=0,v1=deadbeef"})
        self.assertEqual(r.status_code,400)

    def test_download_requires_valid_token(self):
        r=self.client.get("/download?sid=cs_test_123456789ABCDEFG&kind=ebook&exp=0&sig=invalid")
        self.assertEqual(r.status_code,403)

    def test_links_bound_to_payer_session_and_kind(self):
        a=commerce.download_link(self.session,"ebook")
        b=commerce.download_link(self.session,"bonus")
        self.assertNotEqual(a,b)
        self.assertIn("sig=",a)
        self.assertIn("kind=bonus",b)

    def test_cannot_fulfill_unpaid_session(self):
        with patch.object(commerce,"stripe_client") as sc:
            sc.return_value.v1.checkout.sessions.retrieve.return_value={
                **self.session,"payment_status":"unpaid"}
            self.assertIsNone(commerce.verify_session(self.session["id"]))

    def test_wrong_payment_link_rejected(self):
        with patch.object(commerce,"stripe_client") as sc:
            sc.return_value.v1.checkout.sessions.retrieve.return_value={
                **self.session,"payment_link":"plink_another"}
            self.assertIsNone(commerce.verify_session(self.session["id"]))

    def test_paid_session_is_verified(self):
        with patch.object(commerce,"stripe_client") as sc:
            sc.return_value.v1.checkout.sessions.retrieve.return_value=dict(self.session)
            out=commerce.verify_session(self.session["id"])
            self.assertEqual(out["id"],self.session["id"])

    def test_no_private_storage_credentials(self):
        with patch.dict(os.environ, {"S3_BUCKET":"","S3_ACCESS_KEY_ID":""}):
            self.assertFalse(private_storage.configured())
            self.assertFalse(private_storage.exists("ebook"))

    def test_upload_invalid_pdf_is_rejected(self):
        with self.assertRaises(ValueError):
            private_storage.upload("ebook",b"not a pdf"*30)

    def test_purchase_email_idempotent_order_key(self):
        response=Mock();response.json.return_value={"id":"sent-ci"};response.raise_for_status.return_value=None
        with patch.dict(os.environ, {"RESEND_API_KEY":"re_fake_ci","RESEND_FROM_EMAIL":"orders@example.test"}):
            with patch.object(commerce.requests,"post",return_value=response) as sender:
                self.assertEqual(commerce.send_order_email(self.session),"sent-ci")
        self.assertIn("Idempotency-Key",sender.call_args.kwargs["headers"])
        self.assertIn(self.session["id"],sender.call_args.kwargs["headers"]["Idempotency-Key"])
        self.assertIn("bonus",sender.call_args.kwargs["json"]["html"].lower())

    def test_sandbox_webhook_does_not_send_email(self):
        ev={"type":"checkout.session.completed","data":{"object":{"id":self.session["id"]}}}
        with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET":"whsec_fake_ci","ALLOW_SANDBOX_EMAILS":"no"}):
            with patch.object(commerce.stripe.Webhook,"construct_event",return_value=ev),\
                 patch.object(commerce,"verify_session",return_value=self.session),\
                 patch.object(private_storage,"configured",return_value=True),\
                 patch.object(private_storage,"exists",return_value=True),\
                 patch.object(commerce,"send_order_email") as email:
                r=self.client.post("/webhook/stripe",data=b'event',headers={"Stripe-Signature":"fake"})
                self.assertEqual(r.status_code,200)
                email.assert_not_called()

    def test_owner_upload_not_public(self):
        self.assertEqual(self.client.get("/admin/assets").status_code,401)
        self.assertEqual(self.client.get("/_status").status_code,401)

if __name__=="__main__":
    unittest.main()
