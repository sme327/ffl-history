// Build only the public, release-bound show pages. Other museum routes stay SSR.
// Use the installed vinext production renderer, not hand-authored HTML copies.
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {startProdServer} from '../node_modules/vinext/dist/server/prod-server.js';
const routes=['/show','/show/previews/week-5','/show/pilot','/show/episodes/1'];
const manifest=JSON.parse(await fs.readFile('docs/releases/weekly-slate-2026-week-05.json','utf8'));
const {server,port}=await startProdServer({port:0,host:'127.0.0.1',outDir:path.resolve('dist'),noCompression:true,silent:true});
try{
 const pages=[];
 // Preflight all responses before adding any generated public HTML.
 for(const route of routes){
  const response=await fetch(`http://127.0.0.1:${port}${route}`);assert.equal(response.status,200,route);
  const html=await response.text();assert(html.includes('Across the Line')&&!/Error 1102|Preview not found|Episode not found/.test(html),route);
  assert(!html.includes('127.0.0.1'),'Do not expose local preview origins');
  if(route==='/show/previews/week-5')assert(html.includes(manifest.version));
  if(route==='/show/pilot'||route==='/show/episodes/1')assert(html.includes('20261005-v033-720p'));
  pages.push({route,html,file:path.join('dist/client',route+'.html')});
 }
 for(const page of pages){await fs.mkdir(path.dirname(page.file),{recursive:true});await fs.writeFile(page.file,page.html);}
 const report={builtAt:new Date().toISOString(),scope:'four-public-show-pages-only',releaseVersion:manifest.releaseVersion,pages:pages.map(p=>({route:p.route,bytes:Buffer.byteLength(p.html),sha256:createHash('sha256').update(p.html).digest('hex')}))};
 await fs.writeFile('docs/releases/weekly-slate-2026-week-05-static-pages.json',JSON.stringify(report,null,2)+'\n');
 console.log('Built four public show pages with the installed production renderer.');
}finally{server.closeAllConnections();await new Promise(resolve=>server.close(resolve));}
