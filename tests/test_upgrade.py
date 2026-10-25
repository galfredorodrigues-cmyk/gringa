"""No-charge Last Chance Offer routing, pricing and safe checkout guard tests."""
import os
import unittest
from unittest.mock import patch

os.environ.setdefault("STRIPE_MODE", "test")
os.environ.setdefault("DOWNLOAD_SIGNING_SECRET", "unit-test-last-offer-" + "x" * 40)
os.environ.setdefault("PUBLIC_BASE_URL", "https://example.test")
os.environ.setdefault("TEST_PAYMENT_LINK_ID", "plink_test_upgrade")
import app


class LastOfferTests(unittest.TestCase):
    def setUp(self):
        app.app.testing = True
        self.client = app.app.test_client()

    def test_last_offer_in_preview_has_clear_choices_but_no_live_payment(self):
        with patch.dict(os.environ, {
            "STRIPE_MODE": "test", "CHECKOUT_PROVIDER": "hotmart",
            "LIVE_READY": "no", "HOTMART_LINK_LAST_OFFER": "",
            "LAST_OFFER_LAUNCH_APPROVED": "no",
        }):
            response = self.client.get("/last-offer")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers["Cache-Control"], "no-store, private")
            self.assertIn("noindex", response.headers["X-Robots-Tag"])
            page = response.data
            for item in (
                b"Last Chance Offer", b"The Reply Decoder", b"The Profile Makeover",
                b"From Chat to First Date", b"21.90", b"29.90",
                b"9.90", b"YES", b"NO", b"LOSE THIS OFFER", b"CHECKOUT COMING SOON",
            ):
                self.assertIn(item, page)
            self.assertNotIn(b"$12", page)
            self.assertIn(b'aria-disabled="true"', page)
            self.assertNotIn(b"https://pay.hotmart.com/", page)
            self.assertNotIn(b"https://buy.stripe.com/", page)
            self.assertNotIn(b'<form action=', page)

    def test_legacy_upgrade_url_redirects_to_last_offer(self):
        resp = self.client.get("/upgrade")
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers["Location"], "/last-offer")
        self.assertIn("noindex", resp.headers["X-Robots-Tag"])

    def test_original_homepage_still_has_all_sections_and_both_choices(self):
        with patch.dict(os.environ, {"STRIPE_MODE":"test", "CHECKOUT_PROVIDER":"hotmart", "LIVE_READY":"no"}):
            page = self.client.get("/").data
            self.assertIn(b'id="choose"', page)
            self.assertIn(b'id="starter-choice"', page)
            self.assertIn(b'id="complete-choice"', page)
            self.assertIn(b"THE FOUNDATION", page)
            self.assertIn(b"THE COMPLETE LIBRARY", page)
            self.assertIn(b"STARTER CHECKOUT OPENING SOON", page)
            self.assertIn(b"BUNDLE CHECKOUT OPENING SOON", page)
            self.assertIn(b"$9.90", page)
            self.assertIn(b"$29.90", page)
            self.assertEqual(page.count(b'href="/last-offer"'), 2)
            self.assertLess(page.index(b'id="choose"'), page.index(b'id="bundle"'))
            for retained in (
                b'id="problem"', b'id="method"', b'id="example"',
                b'id="inside"', b'id="offer"', b'id="series"',
                b'id="faq"', b"You had something to say.",
                b"Then you deleted it.", b"Four real-world skills.",
            ):
                self.assertIn(retained, page)
            self.assertNotIn(b'/upgrade', page)
            self.assertNotIn(b"https://pay.hotmart.com/", page)
            self.assertNotIn(b"https://buy.stripe.com/", page)

    def _ready_hotmart(self):
        return {
            "CHECKOUT_PROVIDER": "hotmart",
            "HOTMART_LINK_01": "https://pay.hotmart.com/AA01",
            "HOTMART_LINK_02": "https://pay.hotmart.com/AA02",
            "HOTMART_LINK_03": "https://pay.hotmart.com/AA03",
            "HOTMART_LINK_04": "https://pay.hotmart.com/AA04",
            "HOTMART_LINK_BUNDLE": "https://pay.hotmart.com/AA05",
            "HOTMART_LINK_LAST_OFFER": "https://pay.hotmart.com/AA06",
            "MERCHANT_LEGAL_NAME": "Test Merchant LLC",
            "MERCHANT_COUNTRY": "US",
            "MERCHANT_CONTACT_ADDRESS": "Test Address",
            "SUPPORT_EMAIL": "test@example.test",
            **{k: "yes" for k in app.HOTMART_VERIFICATION_FLAGS},
            **{k: "yes" for k in app.LAST_OFFER_FLAGS},
        }

    def test_last_offer_requires_separate_validation_even_when_standard_checkout_ready(self):
        ready = self._ready_hotmart()
        with patch.dict(os.environ, ready):
            self.assertTrue(app.hotmart_checkout_open())
            self.assertEqual(app.last_offer_checkout_url(), ready["HOTMART_LINK_LAST_OFFER"])
            offer = self.client.get("/last-offer").data
            self.assertIn(ready["HOTMART_LINK_LAST_OFFER"].encode(), offer)
            self.assertIn(ready["HOTMART_LINK_01"].encode(), offer)
            homepage = self.client.get("/").data
            self.assertIn(ready["HOTMART_LINK_BUNDLE"].encode(), homepage)
            self.assertNotIn(ready["HOTMART_LINK_01"].encode(), homepage)
            self.assertNotIn(ready["HOTMART_LINK_LAST_OFFER"].encode(), homepage)

        for flag in app.LAST_OFFER_FLAGS:
            unsafe = dict(ready)
            unsafe[flag] = "no"
            with patch.dict(os.environ, unsafe):
                self.assertEqual(app.last_offer_checkout_url(), "", flag)
                page = self.client.get("/last-offer").data
                self.assertNotIn(ready["HOTMART_LINK_LAST_OFFER"].encode(), page)
                self.assertIn(ready["HOTMART_LINK_01"].encode(), page)

        for bad_link in ("", "http://pay.hotmart.com/AA06",
                         "https://evil.test/AA06", ready["HOTMART_LINK_BUNDLE"]):
            with patch.dict(os.environ, {**ready, "HOTMART_LINK_LAST_OFFER": bad_link}):
                self.assertEqual(app.last_offer_checkout_url(), "", bad_link)

        with patch.dict(os.environ, {**ready, "LIVE_READY": "no"}):
            self.assertEqual(app.last_offer_checkout_url(), "")
            page = self.client.get("/last-offer").data
            self.assertNotIn(b"https://pay.hotmart.com/", page)


if __name__ == "__main__":
    unittest.main()
