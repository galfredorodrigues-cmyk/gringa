(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else api.install(root, root.document);
})(typeof window !== 'undefined' ? window : globalThis, function () {
  'use strict';
  const CONFIG = {googleAds: 'AW-18540742704', ga4: 'G-D62D560WV7', metaPixel: '1175307691488519', checkoutLabel: ''};
  const KEY = 'herpov_consent_v3';
  const EVENTS = new Set(['page_view','quiz_start','quiz_complete','offer_view','library_view','sample_view','review_offer','begin_checkout','navigation_click']);
  function eventData(name, data = {}) {
    if (!EVENTS.has(name)) return null;
    const clean = {};
    if (['starter','bundle','last-chance'].includes(data.offer)) clean.offer = data.offer;
    if (['example','method','inside','samples','offer','bundle','starter-choice'].includes(data.section)) clean.section = data.section;
    if (name === 'begin_checkout' && [9.9,21.9,29.9].includes(data.value)) {clean.value=data.value; clean.currency='USD';}
    return clean;
  }
  function readConsent(raw, now = Date.now()) {
    try {const c=JSON.parse(raw); return c.version===3 && typeof c.analytics==='boolean' && typeof c.marketing==='boolean' && typeof c.savedAt==='number' && c.savedAt<=now && now-c.savedAt<180*86400000 ? c : null;} catch {return null;}
  }
  function createCore(config, sink) {
    let consent={analytics:false,marketing:false}; let google=false, meta=false; let localPage=false, googlePage=false, metaPage=false;
    function choose(next) {
      consent={analytics:next.analytics===true,marketing:next.marketing===true};
      sink.google('consent','update',{analytics_storage:consent.analytics?'granted':'denied',ad_storage:consent.marketing?'granted':'denied',ad_user_data:consent.marketing?'granted':'denied',ad_personalization:consent.marketing?'granted':'denied'});
      if ((consent.analytics && config.ga4)||(consent.marketing && config.googleAds)) {
        if (!google) {google=true;sink.loadGoogle(consent.analytics&&config.ga4?config.ga4:config.googleAds);sink.google('js',new Date());}
        if (consent.analytics && config.ga4) sink.google('config',config.ga4,{send_page_view:false,allow_google_signals:consent.marketing,allow_ad_personalization_signals:consent.marketing,...sink.page()});
        if (consent.marketing && config.googleAds) sink.google('config',config.googleAds,sink.page());
      }
      if (consent.marketing && config.metaPixel) {
        if (!meta) {meta=true;sink.loadMeta(config.metaPixel);}
        sink.meta('consent','grant');
      } else if(meta) sink.meta('consent','revoke');
    }
    function track(name,data) {
      const clean=eventData(name,data);if(clean===null)return false;
      if (!consent.analytics && !consent.marketing)return false;
      if (name==='page_view') {
        if (!localPage) {sink.local(name,clean);localPage=true;}
        if (consent.analytics && config.ga4 && !googlePage) {sink.google('event',name,{send_to:config.ga4,...sink.page()});googlePage=true;}
        if (consent.marketing && config.metaPixel && !metaPage) {sink.meta('track','PageView');metaPage=true;}
        return true;
      }
      sink.local(name,clean);
      if (consent.analytics && config.ga4) sink.google('event',name,{...clean,send_to:config.ga4,...sink.page()});
      if (consent.marketing && config.metaPixel) {
        if(name==='begin_checkout')sink.meta('track','InitiateCheckout',{value:clean.value,currency:'USD',content_ids:[clean.offer],content_type:'product'});
        else sink.meta('trackCustom',name,clean);
      }
      if(name==='begin_checkout' && consent.marketing && config.googleAds && config.checkoutLabel) sink.google('event','conversion',{send_to:config.googleAds+'/'+config.checkoutLabel,...clean});
      return true;
    }
    return {choose,track};
  }
  function install(w,d) {
    if (!d || w.HerPovTracking)return;
    w.dataLayer=w.dataLayer||[];w.gtag=w.gtag||function(){w.dataLayer.push(arguments);};
    w.gtag('consent','default',{ad_storage:'denied',analytics_storage:'denied',ad_user_data:'denied',ad_personalization:'denied'});
    w.gtag('set','ads_data_redaction',true);
    function script(src){const s=d.createElement('script');s.async=true;s.src=src;d.head.appendChild(s);}
    const core=createCore(CONFIG,{
      google:(...args)=>w.gtag(...args),
      page:()=>({page_location:w.location.origin+w.location.pathname,page_referrer:'',page_title:d.title}),
      loadGoogle:id=>script('https://www.googletagmanager.com/gtag/js?id='+encodeURIComponent(id)),
      loadMeta:id=>{const f=function(){f.callMethod?f.callMethod.apply(f,arguments):f.queue.push(arguments);};f.queue=[];f.loaded=true;f.version='2.0';w.fbq=f;w._fbq=f;script('https://connect.facebook.net/en_US/fbevents.js');f('set','autoConfig',false,id);f('init',id);},
      meta:(...args)=>w.fbq?.(...args),local:(name,data)=>w.dataLayer.push({event:'herpov_'+name,...data})
    });
    w.HerPovTracking={track:core.track};
    let previous=null;try{previous=readConsent(w.localStorage.getItem(KEY));}catch{}
    const panel=d.createElement('section');panel.className='privacy-panel';panel.setAttribute('aria-label','Privacy choices');
    panel.innerHTML='<h2>Your privacy choices</h2><p>Choose how this site measures visits. Site analytics measures progress through the questionnaire, guide previews and checkout links. You can allow analytics without advertising. Advertising enables our Google advertising tag and Meta Pixel. Your quiz answers are not sent to these platforms. Rejecting optional measurement keeps the site and checkout working. <a href="/privacy">Read our privacy notice</a>.</p><div class="privacy-options"><label><input type="checkbox" name="analytics"> Site analytics</label><label><input type="checkbox" name="marketing"> Advertising</label></div><div class="privacy-actions"><button type="button" data-consent="all">Accept all</button><button type="button" data-consent="analytics">Allow analytics only</button><button type="button" data-consent="none">Reject optional</button><button type="button" data-consent="save">Save choices</button></div>';
    d.body.appendChild(panel);
    const reopen=d.createElement('button');reopen.type='button';reopen.className='privacy-reopen';reopen.textContent='Privacy choices';reopen.addEventListener('click',()=>{panel.hidden=false;panel.querySelector('button').focus();});d.body.appendChild(reopen);
    function setChoices(c,save){core.choose(c);panel.querySelector('[name="analytics"]').checked=c.analytics;panel.querySelector('[name="marketing"]').checked=c.marketing;if(save){try{w.localStorage.setItem(KEY,JSON.stringify({version:3,analytics:c.analytics,marketing:c.marketing,savedAt:Date.now()}));}catch{}}panel.hidden=true;core.track('page_view');}
    panel.addEventListener('click',e=>{const b=e.target.closest('button[data-consent]');if(!b)return;const a=b.dataset.consent;const c=a==='all'?{analytics:true,marketing:true}:a==='analytics'?{analytics:true,marketing:false}:a==='none'?{analytics:false,marketing:false}:{analytics:panel.querySelector('[name="analytics"]').checked,marketing:panel.querySelector('[name="marketing"]').checked};setChoices(c,true);});
    if(previous)setChoices(previous,false);
    d.addEventListener('click',e=>{const a=e.target.closest('a[href]');if(!a)return;let u;try{u=new URL(a.href,w.location.href);}catch{return;}
      if(u.origin===w.location.origin && u.pathname==='/last-offer')core.track('review_offer',{offer:'starter'});
      else if(u.protocol==='https:' && ['pay.hotmart.com','go.hotmart.com'].includes(u.hostname)){
        const last=w.location.pathname==='/last-offer'||w.location.pathname==='/upgrade';const full=last&&a.classList.contains('offer-button');
        core.track('begin_checkout',{offer:last?(full?'last-chance':'starter'):'bundle',value:last?(full?21.9:9.9):29.9});
      }else if(u.origin===w.location.origin && u.hash)core.track('navigation_click',{section:u.hash.slice(1)});
    });
    if(w.IntersectionObserver){const viewed=new Set();const observer=new w.IntersectionObserver(entries=>entries.forEach(entry=>{if(!entry.isIntersecting||viewed.has(entry.target.id))return;const name={offer:'offer_view',bundle:'library_view',samples:'sample_view'}[entry.target.id];if(core.track(name))viewed.add(entry.target.id);}),{threshold:0.15});['offer','bundle','samples'].forEach(id=>{const e=d.getElementById(id);if(e)observer.observe(e);});}
  }
  return {eventData,readConsent,createCore,install};
});
