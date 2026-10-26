'use strict';

const express = require('express');
const nunjucks = require('nunjucks');
const fs = require('node:fs');
const path = require('node:path');

const app = express();
const ROOT = __dirname;
const PORT = Number(process.env.PORT || 3000);
const TEMPLATE_DIR = path.join(ROOT, 'templates');
const ASSET_SLUGS = new Set([
  'first-message-formula', 'reply-decoder', 'profile-makeover',
  'from-chat-to-first-date', 'complete-library',
]);
const LEGAL_KEYS = new Set(['terms', 'privacy', 'refunds', 'contact']);
const HOTMART_LINK_KEYS = [
  'HOTMART_LINK_01', 'HOTMART_LINK_02', 'HOTMART_LINK_03',
  'HOTMART_LINK_04', 'HOTMART_LINK_BUNDLE',
];
const HOTMART_FLAGS = [
  'HOTMART_ALL_OFFERS_VERIFIED', 'HOTMART_USD_PRICES_VERIFIED',
  'HOTMART_DELIVERY_TESTED', 'HOTMART_BUNDLE_CONTENT_VERIFIED',
  'HOTMART_PAYOUTS_CONFIRMED', 'MERCHANT_POLICIES_APPROVED',
  'MERCHANT_TAX_REVIEWED', 'LIVE_READY',
];
const LAST_FLAGS = [
  'LAST_OFFER_USD_PRICE_VERIFIED', 'LAST_OFFER_FIVE_FILES_VERIFIED',
  'LAST_OFFER_DELIVERY_TESTED', 'LAST_OFFER_POLICIES_APPROVED',
  'LAST_OFFER_LAUNCH_APPROVED',
];
const SLUGS = new Set([
  'first-message-formula', 'reply-decoder', 'profile-makeover',
  'from-chat-to-first-date',
]);

function hotmartUrl(raw) {
  if (!raw || raw.length > 600 || /\s/.test(raw)) return '';
  try {
    const u = new URL(raw);
    if (u.protocol !== 'https:' || !['pay.hotmart.com', 'go.hotmart.com'].includes(u.hostname.toLowerCase()) ||
        !u.pathname.slice(1) || u.username || u.password || u.hash) return '';
    return raw;
  } catch { return ''; }
}

function hotmartLinks() {
  return Object.fromEntries(HOTMART_LINK_KEYS.map(k => [k, hotmartUrl(process.env[k] || '')]));
}

function merchantDataConfirmed() {
  const keys = ['MERCHANT_LEGAL_NAME', 'MERCHANT_COUNTRY', 'MERCHANT_CONTACT_ADDRESS', 'SUPPORT_EMAIL'];
  const email = (process.env.SUPPORT_EMAIL || '').trim();
  return keys.every(k => (process.env[k] || '').trim()) && email.includes('@') && email.length < 256;
}

function hotmartCheckoutOpen() {
  const links = Object.values(hotmartLinks());
  return process.env.CHECKOUT_PROVIDER === 'hotmart' &&
    HOTMART_FLAGS.every(f => process.env[f] === 'yes') && merchantDataConfirmed() &&
    links.every(Boolean) && new Set(links).size === HOTMART_LINK_KEYS.length;
}

function lastOfferCheckoutUrl() {
  if (!hotmartCheckoutOpen() || !LAST_FLAGS.every(f => process.env[f] === 'yes')) return '';
  const url = hotmartUrl(process.env.HOTMART_LINK_LAST_OFFER || '');
  return url && !Object.values(hotmartLinks()).includes(url) ? url : '';
}

function checkoutOpen() {
  // This Hostinger adaptation deliberately supports the requested Hotmart
  // integration only. Legacy Stripe/SendOwl stays on the Render Flask app.
  return hotmartCheckoutOpen();
}

const views = nunjucks.configure(TEMPLATE_DIR, {
  autoescape: true,
  express: app,
  noCache: process.env.NODE_ENV !== 'production',
});
views.addGlobal('url_for', (endpoint, options = {}) => {
  if (endpoint === 'static') return `/static/${String(options.filename || '').replace(/^\/+/, '')}`;
  if (endpoint === 'last_offer') return '/last-offer';
  return '/';
});

app.disable('x-powered-by');
app.use((req, res, next) => {
  res.set('X-Content-Type-Options', 'nosniff');
  res.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  next();
});
app.use('/static', express.static(path.join(ROOT, 'static'), {
  fallthrough: false, maxAge: process.env.NODE_ENV === 'production' ? '1d' : 0,
}));

app.get('/', (req, res) => {
  const ready = checkoutOpen();
  const links = ready ? hotmartLinks() : {};
  res.render('home.html', {
    checkout_ready: ready,
    checkout_provider: 'hotmart',
    checkout_url: links.HOTMART_LINK_01 || '',
    bundle_checkout_ready: ready,
    bundle_checkout_url: links.HOTMART_LINK_BUNDLE || '',
    hotmart_links: {
      '02': links.HOTMART_LINK_02 || '', '03': links.HOTMART_LINK_03 || '',
      '04': links.HOTMART_LINK_04 || '',
    },
  });
});

app.get('/last-offer', (req, res) => {
  const ready = checkoutOpen();
  const offer = lastOfferCheckoutUrl();
  const starter = ready ? (hotmartLinks().HOTMART_LINK_01 || '') : '';
  res.set('Cache-Control', 'no-store, private');
  res.set('X-Robots-Tag', 'noindex, nofollow, noarchive');
  res.render('upgrade.html', {
    starter_checkout_url: starter,
    offer_checkout_url: offer,
    starter_checkout_ready: Boolean(starter),
    offer_checkout_ready: Boolean(offer),
  });
});

app.get('/upgrade', (req, res) => {
  res.set('Cache-Control', 'no-store, private');
  res.set('X-Robots-Tag', 'noindex, nofollow, noarchive');
  res.redirect(302, '/last-offer');
});

app.get('/sample-page/:file', (req, res, next) => {
  const match = /^([a-z-]+)\.svg$/.exec(req.params.file);
  if (!match || !SLUGS.has(match[1])) return res.sendStatus(404);
  const file = path.join(ROOT, 'static', 'sample-pages', `${match[1]}.svg`);
  if (!fs.existsSync(file)) return res.sendStatus(404);
  res.set('Cache-Control', 'public, max-age=86400, s-maxage=86400');
  res.set('Content-Security-Policy', "default-src 'none'; style-src 'unsafe-inline'; sandbox");
  res.type('image/svg+xml').sendFile(file, err => { if (err) next(err); });
});

app.get('/product-art/:file', (req, res, next) => {
  const match = /^([a-z-]+)\.png$/.exec(req.params.file);
  if (!match || !ASSET_SLUGS.has(match[1])) return res.sendStatus(404);
  const file = path.join(ROOT, 'static', 'product-art', `${match[1]}.png`);
  if (!fs.existsSync(file)) return res.sendStatus(404);
  res.set('Cache-Control', 'public, max-age=86400, s-maxage=86400');
  res.sendFile(file, err => { if (err) next(err); });
});

app.get(['/terms', '/privacy', '/refunds', '/contact'], (req, res) => {
  const key = req.path.slice(1);
  if (!LEGAL_KEYS.has(key)) return res.sendStatus(404);
  let legal;
  try { legal = JSON.parse(fs.readFileSync(path.join(ROOT, 'legal-content.json'), 'utf8'))[key]; }
  catch { return res.sendStatus(503); }
  const clean = value => String(value || '').trim().slice(0, 350);
  const email = clean(process.env.SUPPORT_EMAIL).slice(0, 255);
  res.render('legal.html', {
    ...legal,
    support_email: email.includes('@') ? email : '',
    legal_name: clean(process.env.MERCHANT_LEGAL_NAME).slice(0, 200),
    merchant_country: clean(process.env.MERCHANT_COUNTRY).slice(0, 100),
    merchant_address: clean(process.env.MERCHANT_CONTACT_ADDRESS),
    ready: checkoutOpen(),
  });
});

app.get('/health', (req, res) => {
  const provider = (process.env.CHECKOUT_PROVIDER || '').trim().toLowerCase();
  const links = hotmartLinks();
  const linksValid = Object.values(links).every(Boolean) && new Set(Object.values(links)).size === HOTMART_LINK_KEYS.length;
  const isHotmart = provider === 'hotmart';
  const enabled = checkoutOpen();
  res.json({
    status: 'ok', checkout_provider: provider || 'unconfigured',
    delivery_provider: isHotmart ? 'hotmart' : (provider === 'stripe' ? 'stripe' : 'unconfigured'),
    integration_operational: isHotmart && linksValid && process.env.HOTMART_DELIVERY_TESTED === 'yes',
    checkout_enabled: enabled, live_ready: enabled, mode: enabled ? 'live' : 'preview',
  });
});

app.use((err, req, res, next) => {
  if (res.headersSent) return next(err);
  if (err.status === 404) return res.sendStatus(404);
  if (process.env.NODE_ENV !== 'production') console.error(err);
  res.sendStatus(500);
});

if (require.main === module) {
  app.listen(PORT, '0.0.0.0', () => console.log(`HER POV listening on ${PORT}`));
}

module.exports = { app, hotmartCheckoutOpen, lastOfferCheckoutUrl, checkoutOpen };
