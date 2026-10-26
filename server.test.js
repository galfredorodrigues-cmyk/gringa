'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { app } = require('./server');

const envKeys = [
  'CHECKOUT_PROVIDER', 'HOTMART_LINK_01', 'HOTMART_LINK_02', 'HOTMART_LINK_03',
  'HOTMART_LINK_04', 'HOTMART_LINK_BUNDLE', 'HOTMART_LINK_LAST_OFFER',
  'HOTMART_ALL_OFFERS_VERIFIED', 'HOTMART_USD_PRICES_VERIFIED',
  'HOTMART_DELIVERY_TESTED', 'HOTMART_BUNDLE_CONTENT_VERIFIED',
  'HOTMART_PAYOUTS_CONFIRMED', 'MERCHANT_POLICIES_APPROVED',
  'MERCHANT_TAX_REVIEWED', 'LIVE_READY', 'LAST_OFFER_USD_PRICE_VERIFIED',
  'LAST_OFFER_FIVE_FILES_VERIFIED', 'LAST_OFFER_DELIVERY_TESTED',
  'LAST_OFFER_POLICIES_APPROVED', 'LAST_OFFER_LAUNCH_APPROVED',
  'MERCHANT_LEGAL_NAME', 'MERCHANT_COUNTRY', 'MERCHANT_CONTACT_ADDRESS', 'SUPPORT_EMAIL',
];

function clearEnv() { for (const key of envKeys) delete process.env[key]; }
function allFlags(keys) { for (const key of keys) process.env[key] = 'yes'; }

test('HER POV routes retain the funnel while every checkout stays closed by default', async t => {
  const previous = Object.fromEntries(envKeys.map(k => [k, process.env[k]]));
  clearEnv();
  const server = app.listen(0);
  t.after(() => {
    server.close();
    for (const key of envKeys) previous[key] === undefined ? delete process.env[key] : process.env[key] = previous[key];
  });
  const base = `http://127.0.0.1:${server.address().port}`;

  const home = await fetch(base);
  assert.equal(home.status, 200);
  const html = await home.text();
  assert.match(html, /href="\/last-offer"/);
  assert.match(html, /BUNDLE CHECKOUT OPENING SOON/);
  assert.doesNotMatch(html, /pay\.hotmart\.com/);

  const offer = await fetch(`${base}/last-offer`);
  assert.equal(offer.status, 200);
  assert.equal(offer.headers.get('x-robots-tag'), 'noindex, nofollow, noarchive');
  const offerHtml = await offer.text();
  assert.match(offerHtml, /Nothing has been charged yet/);
  assert.doesNotMatch(offerHtml, /pay\.hotmart\.com/);

  const legacy = await fetch(`${base}/upgrade`, { redirect: 'manual' });
  assert.equal(legacy.status, 302);
  assert.equal(legacy.headers.get('location'), '/last-offer');

  const health = await (await fetch(`${base}/health`)).json();
  assert.equal(health.checkout_provider, 'unconfigured');
  assert.equal(health.delivery_provider, 'unconfigured');
  assert.equal(health.integration_operational, false);
  assert.equal(health.checkout_enabled, false);
  assert.equal(health.mode, 'preview');

  assert.equal((await fetch(`${base}/sample-page/first-message-formula.svg`)).status, 200);
  assert.equal((await fetch(`${base}/product-art/first-message-formula.png`)).status, 200);
  assert.equal((await fetch(`${base}/product-art/not-allowed.png`)).status, 404);
  assert.equal((await fetch(`${base}/terms`)).status, 200);
});

test('Hotmart mode reports its provider but never opens checkouts on incomplete verification', async t => {
  const previous = Object.fromEntries(envKeys.map(k => [k, process.env[k]]));
  clearEnv();
  process.env.CHECKOUT_PROVIDER = 'hotmart';
  process.env.HOTMART_LINK_01 = 'https://pay.hotmart.com/TEST-VOL-01?off=test01';
  const server = app.listen(0);
  t.after(() => {
    server.close();
    for (const key of envKeys) previous[key] === undefined ? delete process.env[key] : process.env[key] = previous[key];
  });
  const base = `http://127.0.0.1:${server.address().port}`;
  const health = await (await fetch(`${base}/health`)).json();
  assert.equal(health.checkout_provider, 'hotmart');
  assert.equal(health.delivery_provider, 'hotmart');
  assert.equal(health.integration_operational, false);
  assert.equal(health.checkout_enabled, false);
  assert.equal(health.mode, 'preview');
  assert.match(await (await fetch(base)).text(), /STARTER CHECKOUT OPENING SOON/);
});

test('verified test configuration maps the pre-checkout special price and direct bundle separately', async t => {
  const previous = Object.fromEntries(envKeys.map(k => [k, process.env[k]]));
  clearEnv();
  process.env.CHECKOUT_PROVIDER = 'hotmart';
  process.env.HOTMART_LINK_01 = 'https://pay.hotmart.com/TEST-VOL-01?off=test01';
  process.env.HOTMART_LINK_02 = 'https://pay.hotmart.com/TEST-VOL-02?off=test02';
  process.env.HOTMART_LINK_03 = 'https://pay.hotmart.com/TEST-VOL-03?off=test03';
  process.env.HOTMART_LINK_04 = 'https://pay.hotmart.com/TEST-VOL-04?off=test04';
  process.env.HOTMART_LINK_BUNDLE = 'https://pay.hotmart.com/TEST-LIBRARY?off=testbundle';
  process.env.HOTMART_LINK_LAST_OFFER = 'https://pay.hotmart.com/TEST-LIBRARY?off=testlast';
  allFlags([
    'HOTMART_ALL_OFFERS_VERIFIED', 'HOTMART_USD_PRICES_VERIFIED', 'HOTMART_DELIVERY_TESTED',
    'HOTMART_BUNDLE_CONTENT_VERIFIED', 'HOTMART_PAYOUTS_CONFIRMED',
    'MERCHANT_POLICIES_APPROVED', 'MERCHANT_TAX_REVIEWED', 'LIVE_READY',
    'LAST_OFFER_USD_PRICE_VERIFIED', 'LAST_OFFER_FIVE_FILES_VERIFIED',
    'LAST_OFFER_DELIVERY_TESTED', 'LAST_OFFER_POLICIES_APPROVED', 'LAST_OFFER_LAUNCH_APPROVED',
  ]);
  process.env.MERCHANT_LEGAL_NAME = 'HER POV LLC';
  process.env.MERCHANT_COUNTRY = 'US';
  process.env.MERCHANT_CONTACT_ADDRESS = 'Test address';
  process.env.SUPPORT_EMAIL = 'support@example.test';
  const server = app.listen(0);
  t.after(() => {
    server.close();
    for (const key of envKeys) previous[key] === undefined ? delete process.env[key] : process.env[key] = previous[key];
  });
  const base = `http://127.0.0.1:${server.address().port}`;
  const home = await (await fetch(base)).text();
  assert.match(home, /href="https:\/\/pay\.hotmart\.com\/TEST-LIBRARY\?off=testbundle"/);
  const offer = await (await fetch(`${base}/last-offer`)).text();
  assert.match(offer, /href="https:\/\/pay\.hotmart\.com\/TEST-LIBRARY\?off=testlast"/);
  assert.match(offer, /href="https:\/\/pay\.hotmart\.com\/TEST-VOL-01\?off=test01"/);
});
