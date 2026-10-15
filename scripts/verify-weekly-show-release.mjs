// RETIRED 2026-10-14: one-time release gate for Week 5 V007. Do not rerun. It would fail by design
// (Week 5 has left "This week") and overwrite V007's recorded live QA. See docs/SHOW_HUB.md.
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
const base=process.argv[2]??'http://127.0.0.1:4185';
const allowLocalNoRange=process.argv.includes('--allow-local-no-range');
const live=process.argv.includes('--live'),local=['127.0.0.1','localhost'].includes(new URL(base).hostname);
assert(local||(live&&base==='https://iwnh.sme327.com'),'Only the requested website or local preview may be checked');
assert(!allowLocalNoRange||local,'Never waive range checks on the live website');
const manifest=JSON.parse(await fs.readFile('docs/releases/weekly-slate-2026-week-05.json','utf8'));
if(live)assert.equal(manifest.deploymentApproved,true);
const pages=[];
const staticPages=JSON.parse(await fs.readFile('docs/releases/weekly-slate-2026-week-05-static-pages.json','utf8'));
for(const path of ['/show','/show/previews/week-5','/show/pilot','/show/episodes/1','/program/2026-week-04/recap']){
 const response=await fetch(base+path);assert.equal(response.status,200,path);
 const html=await response.text();assert(!/Preview not found|Issue not found|Episode not found/.test(html),path);
 const built=staticPages.pages.find(p=>p.route===path);
 if(built)assert.equal(createHash('sha256').update(html).digest('hex'),built.sha256,`Serve the build-time page: ${path}`);
 if(path==='/show'){
  const cards=[...html.matchAll(/<a class="atl-now-card"[^>]*>[\s\S]*?<\/a>/g)].map(m=>m[0]);
  assert(cards.some(c=>c.includes('This week')&&c.includes('/show/previews/week-5')&&c.includes('Week 5 Weekly Slate')),'Week 5 must be in This week');
  assert(cards.some(c=>c.includes('Latest episode')&&c.includes('/show/episodes/1')&&c.includes('Episode 1:')),'Episode 1 must be in Latest episode');
 }
 if(path==='/show/previews/week-5'){
  assert(html.includes(`2026-week-05.mp4?v=${manifest.version}`));
  assert(html.includes('4:41'));assert(!html.includes('<track'),'Burned-in captions must not duplicate');
  assert(!html.includes('href="/program/2026-week-05"'),'Unavailable Program draft must not become a dead link');
 }
 if(path==='/show/pilot'||path==='/show/episodes/1')assert(html.includes('20261005-v033-720p'));
 pages.push({path,status:response.status});
}
const mediaUrl=base+manifest.video+'?v='+manifest.version;
const response=await fetch(mediaUrl);assert.equal(response.status,200);
assert(response.headers.get('content-type')?.startsWith('video/mp4'));
const bytes=Buffer.from(await response.arrayBuffer());assert.equal(bytes.length,manifest.bytes);assert.equal(createHash('sha256').update(bytes).digest('hex'),manifest.sha256);
assert(bytes.length<25*1024*1024);
const range=await fetch(mediaUrl,{headers:{Range:'bytes=0-31'}});
const rangeBytes=Buffer.from(await range.arrayBuffer());
if(range.status===206){
 assert.equal(rangeBytes.length,32);assert(rangeBytes.equals(bytes.subarray(0,32)));
 assert.equal(range.headers.get('content-range'),`bytes 0-31/${manifest.bytes}`);
}else{
 assert(allowLocalNoRange,'Video seeking requires byte-range support; do not silently waive this check');
 assert.equal(range.status,200);assert(rangeBytes.equals(bytes),'The local fallback must serve the complete correct file');
}
const pilot=await fs.readFile('public/show/pilot-review.mp4');assert.equal(createHash('sha256').update(pilot).digest('hex'),'7efaea2692c49d8fb51e51b52718c6a531deddd7a62d3d1831f9126ca773e383');
const additionalRangeChecks=[];
if(range.status===206){
 for(const [url,data] of [[mediaUrl,bytes],[base+'/show/pilot-review.mp4?v=20261005-v033-720p',pilot]]){
  for(const [header,start,end] of [['bytes=-32',data.length-32,data.length-1],[`bytes=${data.length-32}-`,data.length-32,data.length-1]]){
   const r=await fetch(url,{headers:{Range:header}});assert.equal(r.status,206);
   assert.equal(r.headers.get('content-range'),`bytes ${start}-${end}/${data.length}`);
   assert.equal(r.headers.get('content-length'),'32');
   assert(Buffer.from(await r.arrayBuffer()).equals(data.subarray(start,end+1)));
   additionalRangeChecks.push({path:new URL(url).pathname,header,status:206,bytes:32});
  }
  const invalid=await fetch(url,{headers:{Range:`bytes=${data.length}-`}});assert.equal(invalid.status,416);
  assert.equal(invalid.headers.get('content-range'),`bytes */${data.length}`);
  await invalid.body?.cancel();
  additionalRangeChecks.push({path:new URL(url).pathname,header:`bytes=${data.length}-`,status:416});
 }
}
if(live){
 const p=await fetch(base+'/show/pilot-review.mp4?v=20261005-v033-720p');assert.equal(p.status,200);assert(p.headers.get('content-type')?.startsWith('video/mp4'));
 assert.equal(createHash('sha256').update(Buffer.from(await p.arrayBuffer())).digest('hex'),manifest.pilotV033PreservedSHA256);
}
const report={checkedAt:new Date().toISOString(),base,localOnly:true,status:range.status===206?'local-checks-passed':'local-pages-and-video-passed-production-range-pending',pages,video:{path:manifest.video,bytes:bytes.length,sha256:manifest.sha256,contentType:response.headers.get('content-type'),rangeStatus:range.status,rangeVerified:range.status===206},localRangeLimitation:range.status===206?null:'Installed Miniflare asset worker returns a full 200 response for Range requests; resolveAssetIntentToResponse emits OkResponse. Verify HTTP 206 seeking against the actual new URL only after authorized deployment.',pilotV033Preserved:true,burnedInCaptionsOnly:true,missingProgramLinkHidden:true,deploymentApproved:false,deployed:false};
Object.assign(report,{localOnly:local,status:live?'live-pages-media-and-range-passed':report.status,deploymentApproved:manifest.deploymentApproved,deployed:live});
Object.assign(report,{additionalRangeChecks,hubSlotsVerified:true});
const repeatedShowPageChecks=[];
for(let round=0;round<3;round++)for(const page of staticPages.pages){
 const r=await fetch(base+page.route);assert.equal(r.status,200,page.route);
 assert.equal(createHash('sha256').update(await r.text()).digest('hex'),page.sha256);
 repeatedShowPageChecks.push({round:round+1,path:page.route,status:r.status,buildTimeHTMLVerified:true});
}
Object.assign(report,{repeatedShowPageChecks});
await fs.writeFile(`docs/releases/weekly-slate-2026-week-05-${live?'live':'local'}-qa.json`,JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
