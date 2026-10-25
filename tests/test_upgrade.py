"""Regression tests for the separate, non-purchasable HER POV upsell preview."""
import os
import unittest

os.environ.setdefault("STRIPE_MODE", "test")
os.environ.setdefault("DOWNLOAD_SIGNING_SECRET", "unit-test-upgrade-" + "x" * 48)
os.environ.setdefault("PUBLIC_BASE_URL", "https://example.test")
os.environ.setdefault("TEST_PAYMENT_LINK_ID", "plink_test_upgrade")
import app


class UpgradePreviewTests(unittest.TestCase):
    def setUp(self):
        app.app.testing = True
        self.client = app.app.test_client()

    def test_upgrade_page_contains_three_remaining_guides_and_price(self):
        response = self.client.get("/upgrade")
        self.assertEqual(response.status_code, 200)
        for item in (
            b"The Reply Decoder",
            b"The Profile Makeover",
            b"From Chat to First Date",
            b"20",
            b"9.90 first purchase",
            b"noindex,nofollow,noarchive",
        ):
            self.assertIn(item, response.data)
        self.assertEqual(response.headers["Cache-Control"], "no-store, private")
        self.assertIn("noindex", response.headers["X-Robots-Tag"])

    def test_preview_never_shows_live_purchase_link(self):
        response = self.client.get("/upgrade")
        page = response.data
        self.assertIn(b'aria-disabled="true"', page)
        self.assertIn(b"CHECKOUT COMING SOON", page)
        self.assertNotIn(b"https://pay.hotmart.com/", page)
        self.assertNotIn(b"https://buy.stripe.com/", page)
        self.assertNotIn(b'form action=', page)
        # Main storefront stays linked only to the normal product checkout.
        self.assertNotIn(b'/upgrade', self.client.get("/").data)


if __name__ == "__main__":
    unittest.main()
