// Build only the public, release-bound show pages. Other museum routes stay SSR.
// Use the installed vinext production renderer, not hand-authored HTML copies.
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {startProdServer} from '../node_modules/vinext/dist/server/prod-server.js';
const manifest=JSON.parse(await fs.readFile('docs/releases/show-media-current.json','utf8'));
assert(/^[a-z0-9-]+$/.test(manifest.releaseId));
const routes=[...new Set(['/show',...manifest.media.flatMap(item=>item.watchRoutes)])];
assert(routes.every(route=>/^\/show(?:\/pilot|\/episodes\/\d+|\/previews\/week-\d+)?$/.test(route)));
const {server,port}=await startProdServer({port:0,host:'127.0.0.1',outDir:path.resolve('dist'),noCompression:true,silent:true});
try{
 const pages=[];
 // Preflight all responses before adding any generated public HTML.
 for(const route of routes){
  const response=await fetch(`http://127.0.0.1:${port}${route}`);assert.equal(response.status,200,route);
  const html=await response.text();assert(html.includes('Across the Line')&&!/Error 1102|Preview not found|Episode not found/.test(html),route);
  assert(!html.includes('127.0.0.1'),'Do not expose local preview origins');
  const item=manifest.media.find(item=>item.watchRoutes.includes(route));
  if(item){assert(html.includes(item.version),`Stale catalog version for ${route}`);assert(html.includes(item.video),`Wrong movie for ${route}`);}
  pages.push({route,html,file:path.join('dist/client',route+'.html')});
 }
 for(const page of pages){await fs.mkdir(path.dirname(page.file),{recursive:true});await fs.writeFile(page.file,page.html);}
 const report={builtAt:new Date().toISOString(),scope:'current-manifest-show-pages-only',releaseId:manifest.releaseId,mediaManifestSHA256:createHash('sha256').update(await fs.readFile('docs/releases/show-media-current.json')).digest('hex'),pages:pages.map(p=>({route:p.route,bytes:Buffer.byteLength(p.html),sha256:createHash('sha256').update(p.html).digest('hex')}))};
 await fs.writeFile('docs/releases/show-static-pages-current.json',JSON.stringify(report,null,2)+'\n');
 console.log(`Built ${pages.length} public show pages from the current media manifest; historical Week 5 QA is untouched.`);
}finally{server.closeAllConnections();await new Promise(resolve=>server.close(resolve));}
