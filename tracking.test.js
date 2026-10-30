'use strict';
const test=require('node:test');const assert=require('node:assert/strict');
const {eventData,readConsent,createCore}=require('./static/js/tracking');
function harness(config={googleAds:'AW-18540742704',ga4:'',metaPixel:'',checkoutLabel:''}){const log=[];const sink={google:(...x)=>log.push(['google',...x]),meta:(...x)=>log.push(['meta',...x]),loadGoogle:x=>log.push(['loadGoogle',x]),loadMeta:x=>log.push(['loadMeta',x]),local:(...x)=>log.push(['local',...x]),page:()=>({page_location:'https://vitrinyx.com/last-offer',page_referrer:''})};return {core:createCore(config,sink),log};}
test('no consent never loads Google or Meta or records funnel activity',()=>{const {core,log}=harness();assert.equal(core.track('quiz_complete'),false);assert.deepEqual(log,[]);core.choose({analytics:false,marketing:false});assert.equal(log.some(x=>x[0].startsWith('load')),false);assert.equal(core.track('begin_checkout',{offer:'starter',value:9.9}),false);});
test('advertising consent loads the confirmed Google tag once and never invents a purchase',()=>{const {core,log}=harness();core.choose({marketing:true});core.choose({marketing:true});assert.equal(log.filter(x=>x[0]==='loadGoogle').length,1);assert.equal(log.find(x=>x[0]==='loadGoogle')[1],'AW-18540742704');assert.equal(core.track('purchase',{value:29.9}),false);assert.equal(log.some(x=>x[0]==='meta'),false);assert.equal(log.some(x=>x[2]==='conversion'),false);});
test('withdrawal stops subsequent funnel events',()=>{const {core,log}=harness();core.choose({marketing:true});assert.equal(core.track('quiz_start'),true);core.choose({marketing:false,analytics:false});const before=log.length;assert.equal(core.track('quiz_complete'),false);assert.equal(log.length,before);assert.equal(log.at(-1)[3].ad_storage,'denied');});
test('event payloads do not contain quiz answers, text, emails or raw URLs',()=>{const payload=eventData('begin_checkout',{offer:'last-chance',value:21.9,email:'private@example.com',answer:'dating detail',message:'private message',url:'https://example.com/?secret=x'});assert.deepEqual(payload,{offer:'last-chance',value:21.9,currency:'USD'});assert.deepEqual(eventData('quiz_complete',{answer:'private'}),{});assert.equal(eventData('purchase'),null);});
test('confirmed purchases and all three commercial amounts remain distinct',()=>{for(const [offer,value] of [['starter',9.9],['bundle',29.9],['last-chance',21.9]])assert.deepEqual(eventData('begin_checkout',{offer,value}),{offer,value,currency:'USD'});assert.equal(eventData('begin_checkout',{value:999}).value,undefined);});
test('expired, malformed and incomplete consent records do not authorize tracking',()=>{const now=Date.now();for(const raw of ['bad','null','{}',JSON.stringify({version:3,analytics:true,marketing:true,savedAt:now-181*86400000})])assert.equal(readConsent(raw,now),null);assert.equal(readConsent(JSON.stringify({version:3,analytics:false,marketing:true,savedAt:now}),now).marketing,true);});

test('Meta uses the confirmed pixel only after advertising consent and stops after withdrawal',()=>{const {core,log}=harness({googleAds:'AW-18540742704',metaPixel:'1175307691488519'});core.choose({analytics:true,marketing:false});assert.equal(log.some(x=>x[0]==='loadMeta'),false);core.choose({marketing:true});core.choose({marketing:true});assert.deepEqual(log.filter(x=>x[0]==='loadMeta'),[['loadMeta','1175307691488519']]);core.track('page_view');core.track('begin_checkout',{offer:'bundle',value:29.9});assert.ok(log.some(x=>x[0]==='meta'&&x[2]==='PageView'));assert.ok(log.some(x=>x[0]==='meta'&&x[2]==='InitiateCheckout'&&x[3].value===29.9));core.choose({marketing:false});const before=log.length;core.track('quiz_complete');assert.equal(log.length,before);assert.equal(core.track('purchase'),false);});
test('previous Google-only consent is not reused for Meta activation',()=>{assert.equal(readConsent(JSON.stringify({version:1,analytics:true,marketing:true,savedAt:Date.now()})),null);});

test('GA4 analytics permission does not grant advertising or initialize Meta',()=>{const {core,log}=harness({googleAds:'AW-18540742704',ga4:'G-D62D560WV7',metaPixel:'1175307691488519'});core.choose({analytics:true,marketing:false});core.track('quiz_complete',{answer:'private'});assert.deepEqual(log.filter(x=>x[0]==='loadGoogle'),[['loadGoogle','G-D62D560WV7']]);assert.equal(log.some(x=>x[0]==='loadMeta'),false);const e=log.find(x=>x[0]==='google'&&x[1]==='event'&&x[2]==='quiz_complete');assert.equal(e[3].send_to,'G-D62D560WV7');assert.equal(e[3].answer,undefined);});

test('resaving privacy choices never duplicates page views and newly allowed vendors receive one',()=>{const {core,log}=harness({googleAds:'AW-18540742704',ga4:'G-D62D560WV7',metaPixel:'1175307691488519'});core.choose({analytics:true});core.track('page_view');core.choose({analytics:true});core.track('page_view');core.choose({analytics:true,marketing:true});core.track('page_view');core.choose({analytics:true,marketing:true});core.track('page_view');assert.equal(log.filter(x=>x[0]==='local'&&x[1]==='page_view').length,1);assert.equal(log.filter(x=>x[0]==='google'&&x[1]==='event'&&x[2]==='page_view').length,1);assert.equal(log.filter(x=>x[0]==='meta'&&x[1]==='track'&&x[2]==='PageView').length,1);});
const {install}=require('./static/js/tracking');
test('analytics-only button records the funnel in GA4 without loading advertising, and rejection stops it',()=>{
 const scripts=[],saved=new Map(); let click;
 const fields={analytics:{checked:false},marketing:{checked:false}};
 const panel={setAttribute(){},querySelector(s){return s.includes('analytics')?fields.analytics:s.includes('marketing')?fields.marketing:{focus(){}};},addEventListener(type,fn){click=fn;}};
 const d={title:'HER POV',head:{appendChild(s){scripts.push(s.src);}},body:{appendChild(){}},createElement(tag){return tag==='section'?panel:{addEventListener(){}};},addEventListener(){}};
 const w={document:d,location:{origin:'https://vitrinyx.com',pathname:'/',href:'https://vitrinyx.com/'},localStorage:{getItem(k){return saved.get(k)||null;},setItem(k,v){saved.set(k,v);}}};
 install(w,d);
 assert.ok(panel.innerHTML.includes('data-consent="analytics"'));
 click({target:{closest(){return {dataset:{consent:'analytics'}};}}});
 assert.deepEqual(scripts,['https://www.googletagmanager.com/gtag/js?id=G-D62D560WV7']);
 assert.equal(JSON.parse(saved.get('herpov_consent_v3')).marketing,false);
 assert.equal(w.HerPovTracking.track('quiz_complete'),true);
 assert.ok(w.dataLayer.some(x=>x[0]==='event'&&x[1]==='quiz_complete'&&x[2].send_to==='G-D62D560WV7'));
 assert.equal(w.fbq,undefined);
 click({target:{closest(){return {dataset:{consent:'none'}};}}});
 assert.equal(w.HerPovTracking.track('quiz_start'),false);
 assert.equal(w.HerPovTracking.track('purchase'),false);
});

test('HER POV campaign attribution is kept without forwarding arbitrary queries or identifiers',()=>{
 const {campaignData}=require('./static/js/tracking');
 const campaign=campaignData('?utm_source=meta&utm_medium=paid_social&utm_campaign=herpov_us_test01&utm_content=creative_b&email=private@example.com&fbclid=private&answer=private');
 assert.deepEqual(campaign,{campaign_source:'meta',campaign_medium:'paid_social',campaign_name:'herpov_us_test01',campaign_content:'creative_b'});
 assert.deepEqual(campaignData('?utm_source=private@example.com&utm_campaign=private@example.com&utm_content=https://private.example&token=secret'),{});
 const log=[];const core=createCore({ga4:'G-D62D560WV7'}, {google:(...x)=>log.push(x),loadGoogle(){},campaign:()=>campaign,page:()=>({page_location:'https://vitrinyx.com/'}),local(){}});
 core.choose({analytics:true,marketing:false});
 const config=log.find(x=>x[0]==='config');assert.equal(config[2].campaign_source,'meta');assert.equal(config[2].campaign_content,'creative_b');assert.equal(config[2].allow_google_signals,false);
 const before=log.length;core.choose({analytics:false,marketing:false});assert.equal(log.length,before+1);assert.equal(core.track('quiz_complete'),false);
});

test('PageView is emitted automatically once when a visitor permits Meta or GA4',()=>{
 const {core,log}=harness({googleAds:'',ga4:'G-D62D560WV7',metaPixel:'1175307691488519'});
 core.choose({analytics:false,marketing:false});
 assert.equal(log.some(x=>x[0]==='meta'),false);
 core.choose({analytics:true,marketing:false});
 core.choose({analytics:true,marketing:false});
 assert.equal(log.filter(x=>x[0]==='google'&&x[1]==='event'&&x[2]==='page_view').length,1);
 assert.equal(log.filter(x=>x[0]==='meta'&&x[2]==='PageView').length,0);
 core.choose({analytics:true,marketing:true});
 core.choose({analytics:true,marketing:true});
 assert.equal(log.filter(x=>x[0]==='meta'&&x[1]==='track'&&x[2]==='PageView').length,1);
});

test('visible product views use standard Meta ViewContent only with marketing consent and never invent Purchase',()=>{
 const {core,log}=harness({googleAds:'',ga4:'G-D62D560WV7',metaPixel:'1175307691488519'});
 core.choose({analytics:true,marketing:false});
 core.track('offer_view');
 core.track('offer_view');
 assert.equal(log.filter(x=>x[0]==='google'&&x[2]==='offer_view').length,1);
 assert.equal(log.filter(x=>x[0]==='meta'&&x[2]==='ViewContent').length,0);
 core.choose({analytics:true,marketing:true});
 core.track('offer_view');
 core.track('offer_view');
 core.track('library_view');
 core.track('library_view');
 const viewed=log.filter(x=>x[0]==='meta'&&x[1]==='track'&&x[2]==='ViewContent');
 assert.equal(viewed.length,2);
 assert.deepEqual(viewed.map(x=>[x[3].content_ids[0],x[3].value]),[['first-message-formula',9.9],['complete-library',29.9]]);
 assert.equal(log.filter(x=>x[0]==='google'&&x[2]==='offer_view').length,1);
 assert.equal(log.filter(x=>x[0]==='meta'&&x[2]==='Purchase').length,0);
});

test('consent granted while an offer is already visible catches the missed visibility event once',()=>{
 let click,observed;
 const offer={id:'offer',getBoundingClientRect(){return {top:100,bottom:200,height:100};}};
 const panel={setAttribute(){},querySelector(s){return s.includes('analytics')?{set checked(v){}}:s.includes('marketing')?{set checked(v){}}:{focus(){}};},addEventListener(type,fn){click=fn;}};
 const d={title:'HER POV',documentElement:{clientHeight:800},head:{appendChild(){}},body:{appendChild(){}},getElementById(id){return id==='offer'?offer:null;},createElement(tag){return tag==='section'?panel:{addEventListener(){}};},addEventListener(){}};
 const w={document:d,location:{origin:'https://vitrinyx.com',pathname:'/',href:'https://vitrinyx.com/'},localStorage:{getItem(){return null;},setItem(){}},innerHeight:800,
   IntersectionObserver:function(fn){observed=fn;this.observe=()=>{};}};
 install(w,d);
 observed([{isIntersecting:true,target:offer}]);
 assert.equal(w.fbq,undefined);
 click({target:{closest(){return {dataset:{consent:'all'}};}}});
 assert.ok(w.fbq);
 assert.equal(w.fbq.queue.filter(x=>x[0]==='track'&&x[1]==='PageView').length,1);
 assert.equal(w.fbq.queue.filter(x=>x[0]==='track'&&x[1]==='ViewContent').length,1);
 observed([{isIntersecting:true,target:offer}]);
 assert.equal(w.fbq.queue.filter(x=>x[0]==='track'&&x[1]==='ViewContent').length,1);
});
