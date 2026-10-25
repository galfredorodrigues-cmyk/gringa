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
            b"21.90",
            b"12",
            b"9.90 starter purchase", 
            b"noindex,nofollow,noarchive",
        ):
            self.assertIn(item, response.data)
        self.assertEqual(response.headers["Cache-Control"], "no-store, private")
        self.assertIn("noindex", response.headers["X-Robots-Tag"])

    def test_original_homepage_has_both_clear_purchase_choices(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        page = response.data
        self.assertIn(b'id="choose"', page)
        self.assertIn(b'id="starter-choice"', page)
        self.assertIn(b'id="complete-choice"', page)
        self.assertIn(b"THE FOUNDATION", page)
        self.assertIn(b"THE COMPLETE LIBRARY", page)
        self.assertIn(b"STARTER CHECKOUT OPENING SOON", page)
        self.assertIn(b"BUNDLE CHECKOUT OPENING SOON", page)
        self.assertIn(b"$9.90", page)
        self.assertIn(b"$29.90", page)
        self.assertLess(page.index(b'id="choose"'), page.index(b'id="bundle"'))
        for retained in (
            b'id="problem"', b'id="method"', b'id="example"',
            b'id="inside"', b'id="offer"', b'id="series"',
            b'id="faq"', b"You had something to say.",
            b"Then you deleted it.", b"Four real-world skills.",
        ):
            self.assertIn(retained, page)
        self.assertNotIn(b'/upgrade', page)
        self.assertNotIn(b'https://pay.hotmart.com/', page)
        self.assertNotIn(b'https://buy.stripe.com/', page)

    def test_preview_never_shows_live_purchase_link(self):
        response = self.client.get("/upgrade")
        page = response.data
        self.assertIn(b'aria-disabled="true"', page)
        self.assertIn(b"COMING SOON", page)
        self.assertNotIn(b"https://pay.hotmart.com/", page)
        self.assertNotIn(b"https://buy.stripe.com/", page)
        self.assertNotIn(b'form action=', page)
        # The public homepage must not expose the exclusive post-purchase upsell.
        self.assertNotIn(b'/upgrade', self.client.get("/").data)


if __name__ == "__main__":
    unittest.main()
