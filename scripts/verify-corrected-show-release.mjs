// General manifest-bound checks; never overwrites the retired V007 live record.
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
const base=process.argv[2],output=process.argv[3];
assert(base&&output,'Supply base URL and a new explicitly named QA output path');
assert(!(await fs.stat(output).catch(()=>null)),'Preserve previous QA evidence; choose a new output path');
const manifest=JSON.parse(await fs.readFile('docs/releases/show-media-current.json','utf8'));
const pages=JSON.parse(await fs.readFile('docs/releases/show-static-pages-current.json','utf8'));
assert.equal(pages.releaseId,manifest.releaseId);
const sha=b=>createHash('sha256').update(b).digest('hex'),checks=[];
for(let round=0;round<3;round++)for(const page of pages.pages){
 const response=await fetch(new URL(page.route,base));assert.equal(response.status,200,page.route);
 const bytes=Buffer.from(await response.arrayBuffer());assert.equal(sha(bytes),page.sha256,page.route);
 checks.push({kind:'page',round,route:page.route,status:response.status,sha256:sha(bytes)});
}
for(const item of manifest.media){
 const url=new URL(item.video+'?v='+item.version,base);
 const response=await fetch(url);assert.equal(response.status,200);assert.match(response.headers.get('content-type')??'',/^video\/mp4/);
 const bytes=Buffer.from(await response.arrayBuffer());assert.equal(bytes.length,item.bytes);assert.equal(sha(bytes),item.sha256);
 const ranges=[['bytes=0-31',0,31],['bytes=-32',bytes.length-32,bytes.length-1],[`bytes=${bytes.length-32}-`,bytes.length-32,bytes.length-1]];
 for(const [range,start,end]of ranges){
  const part=await fetch(url,{headers:{Range:range}});assert.equal(part.status,206,`${item.id}: ${range}`);
  assert.equal(part.headers.get('content-range'),`bytes ${start}-${end}/${bytes.length}`);assert.equal(part.headers.get('content-length'),'32');
  assert(Buffer.from(await part.arrayBuffer()).equals(bytes.subarray(start,end+1)));
 }
 const invalid=await fetch(url,{headers:{Range:`bytes=${bytes.length}-`}});assert.equal(invalid.status,416);await invalid.arrayBuffer();
 checks.push({kind:'movie',id:item.id,video:item.video,bytes:bytes.length,sha256:sha(bytes),contentType:response.headers.get('content-type'),prefixSuffixOpenRanges:true,unsatisfiableRange416:true});
}
const hub=await (await fetch(new URL('/show',base))).text();
// A played preview belongs in the archive, not necessarily the This Week slot.
assert(hub.includes(manifest.expectedHub.latestEpisode));
for(const route of manifest.expectedHub.pastPreviews)assert(hub.includes(route),`Missing archived preview ${route}`);
if(manifest.expectedHub.currentPreview===null)assert(hub.includes('Next preview coming soon'),'No unplayed published preview is expected');
else assert(hub.includes(manifest.expectedHub.currentPreview),'Missing current preview');
await fs.writeFile(output,JSON.stringify({checkedAt:new Date().toISOString(),base,releaseId:manifest.releaseId,checks,hubArchiveAndLatestEpisode:true,rawHeadersOrCredentialsIncluded:false,ownerEarCheckPending:!manifest.releaseApproved,releaseApproved:manifest.releaseApproved,deploymentApproved:manifest.deploymentApproved},null,2)+'\n');
console.log('Manifest-bound movie, range, repeated-page and archive checks passed; browser playback remains a separate check.');
