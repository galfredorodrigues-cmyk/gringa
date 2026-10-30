# HER POV — Meta Pixel verification and release checklist

This change improves **consented** Meta event coverage. It does **not** turn on tracking before consent, bypass browser blockers, or claim to record every visitor. The customer's rejection of marketing tracking must be honored.

## Site events and expected behavior

- On the HER POV home page or `/last-offer`, choosing **Accept all** loads Meta Pixel `1175307691488519` and emits one `PageView` per loaded page. Choosing **Analytics only** sends GA4 only. Choosing **Reject optional** sends no marketing tracking.
- A visitor who accepts marketing tracking while already viewing an offer can produce `ViewContent` once for the starter guide (USD 9.90) or the Complete Library (USD 29.90). Standard `ViewContent` must be measured separately from `Purchase`.
- Clicking a Hotmart link on the storefront emits consented custom `CheckoutLinkClick` (and GA4 `begin_checkout`) only. **Do not** emit Meta standard `InitiateCheckout` from the link click: that is a navigation attempt, not a confirmed checkout load. The Hotmart checkout owns standard `InitiateCheckout` (its page-visit event), to avoid double-counting.
- **No `Purchase` event should ever be generated on a button click or simply by visiting the storefront's thank-you page.** Only a verified completed Hotmart order may generate `Purchase`.
- Product view events are deduplicated per consented analytics provider, including when someone switches from GA4-only to enabling Meta later.

## Critical Hotmart integration (requires signed-in producer access)

The GitHub site **cannot** by itself observe completed purchases on the separate Hotmart checkout. Within the Hotmart account, for **each selling product**, open **Tools > Tracking Pixel > Facebook + Instagram**, set Pixel ID `1175307691488519`, configure supported **checkout-view and completed-sale / Purchase** events, and save. For any available WEB + Conversions API setup, follow Hotmart's instructions and check event deduplication using matching event IDs. Only do this if the seller has the necessary legal basis/consent and Hotmart/Meta accounts are authorized.

Official setup reference: https://suportehotmart.zendesk.com/hc/pt-br/articles/115004826368-Como-configurar-o-Pixel-da-Meta-na-Hotmart

## Acceptance tests before spending more on ads

1. Run `npm test` in the GitHub branch.
2. Deploy the reviewed changes to **Hostinger**. The GitHub repository is not automatically synchronized with the hosted Node app. This PR alone does **not** change the live site.
3. Open the production home page with a clean browser profile, before clicking consent, and verify there is **no Meta Pixel network request**.
4. Select **Accept all**, then use **Meta Events Manager > Test Events** to verify exactly one `PageView` for that loaded page. The events should use Pixel ID `1175307691488519`.
5. Scroll to starter and Complete Library offers to confirm each `ViewContent` appears once. Change consent settings, revisit a section, and verify no duplicate events.
6. Open the Hotmart checkout using a real product button and verify an `InitiateCheckout` in Test Events. Note that network-based tracking can be blocked by browser restrictions.
7. Confirm the selected Hotmart product has the exact same Pixel ID and a verified **completed order** produces one `Purchase`, with no false `Purchase` for abandoned checkouts. Do not create a paid test order without separate authorization.
8. Verify mobile page loading, consent behavior, product links and checkout readiness (`/health`) on the actual Hostinger deployment, not only on GitHub.

## Reading the metrics

Meta's *Landing Page Views* metric depends on measuring the destination. A low ratio of landing page views to outbound clicks can also result from privacy consent, blockers, poor loading or navigation interruptions; it is **not** by itself proof that the website failed. Compare consented Meta events, first-party aggregate server performance, browser tests, and paid landing page analytics before changing campaign budgets.
