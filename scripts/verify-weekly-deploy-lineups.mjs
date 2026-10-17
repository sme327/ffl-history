// Release-specific, opt-in gate after build and immediately before Wrangler upload.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
// The V007 branch below is retained as historical code. The active Week 6
// release has independent approvals, source hashes and roster/count conditions.
const current=JSON.parse(fs.readFileSync('docs/releases/show-media-current.json','utf8'));
if(current.releaseId==='weekly-slate-2026-week-06-v004'){
 assert.equal(current.releaseApproved,true,'Exact V004 cut approval required');
 assert.equal(current.deploymentApproved,true,'STOP: explicit owner deployment go has not been recorded');
 assert(current.ownerApproval.deploymentAuthorizationMessage,'Record the actual owner deploy-go message');
 const show=process.env.FFL_SHOW_ROOT??'/Users/sme/Documents/Projects/Sports/Fantasy Football Leagues/FFL Show';
 const approval=JSON.parse(fs.readFileSync(path.join(show,'weekly/2026-week-06/OWNER_APPROVAL_V004.json'),'utf8'));
 const item=current.media.find(m=>m.id===current.releaseId);
 assert(item&&item.releaseApproved&&item.deploymentApproved);
 assert.equal(approval.sha256,item.sha256);assert.equal(approval.releaseApproved,true);
 assert.equal(approval.deploymentApproved,true,'Show repo also requires explicit owner deployment authorization');
 for(const media of current.media){
  const bytes=fs.readFileSync(path.join('public',media.video));
  assert(bytes.length<25*1024*1024);assert.equal(bytes.length,media.bytes);
  assert.equal(createHash('sha256').update(bytes).digest('hex'),media.sha256,'Approved movie changed: '+media.id);
 }
 const output=path.join(show,'weekly/2026-week-06',`predeploy-check-${Date.now()}.json`);
 execFileSync('python3',[path.join(show,'renderer/scripts/check-week06-freshness.py'),'--output',output],{cwd:show,stdio:'inherit'});
 const check=JSON.parse(fs.readFileSync(output,'utf8'));
 assert(Date.now()-Date.parse(check.capturedAtStart)<5*60*1000,'Freshness check must finish inside five minutes');
 for(const [key,value]of Object.entries(check.conditions))assert.equal(value,key!=='V2_revY','STOP: spoken condition changed: '+key);
 const cards=JSON.parse(fs.readFileSync(path.join(show,'weekly/2026-week-06/release-card-data-v004.json'),'utf8'));
 const report={releaseId:current.releaseId,sha256:item.sha256,checkedAt:new Date().toISOString(),capture:output,capturedAtPacific:check.capturedAtPacific,conditions:check.conditions,pass:true,projectionGapIsNotSpoken:true,cardDataRemainsAsOf:cards.kittle.capturedAt,cardStampsNotRelabelled:true,currentValues:{kittleTransactions:check.kittleTransactionCount,tihwdMoves:check.tihwdMoves,rodgersProjection:check.decisionPlayers.Rodgers.projected,youngProjection:check.decisionPlayers.Young.projected},note:'Current values are logged, not substituted into the owner-approved movie. Its clearly stamped historical card values remain unchanged.'};
 fs.writeFileSync('docs/releases/weekly-slate-2026-week-06-final-upload-check.json',JSON.stringify(report,null,2)+'\n');
 console.log('Week 6 upload gate passed: exact approved hashes, explicit deploy go and fresh spoken roster/count conditions.');
 process.exit(0);
}
if(process.env.FFL_VERIFY_WEEK5_LINEUPS!=='1')process.exit(0);
const show=process.env.FFL_SHOW_ROOT??'/Users/sme/Documents/Projects/Sports/Fantasy Football Leagues/FFL Show';
const manifest=JSON.parse(fs.readFileSync('docs/releases/weekly-slate-2026-week-05.json','utf8'));
assert.equal(manifest.deploymentApproved,true);assert.equal(manifest.releaseVersion,'v007');
const bytes=fs.readFileSync('public'+manifest.video);
assert(bytes.length<25*1024*1024);assert.equal(bytes.length,manifest.bytes);
assert.equal(createHash('sha256').update(bytes).digest('hex'),manifest.sha256);
const qa=JSON.parse(fs.readFileSync(path.join(show,'weekly/2026-week-05/SLATE2_QA_V007.json'),'utf8'));
assert.equal(qa.fullDecode,true);assert.equal(qa.sha256,manifest.sha256);
const request=JSON.parse(fs.readFileSync(path.join(show,'weekly/2026-week-05/slate2-audio-request.json'),'utf8'));
assert(request.lines.find(l=>l.id==='wk05.graham.116').text.endsWith('leading scorer.'));
assert(!/Stroud|tenth|Yahoo/.test(request.lines.find(l=>l.id==='wk05.graham.116').text));
const output=path.join(show,'.local/weekly/2026-week-05',`predeploy-v007-${Date.now()}.json`);
execFileSync('python3',['scripts/capture-weekly-preview.py','--week','5','--output',output],{cwd:path.join(show,'renderer'),stdio:'inherit'});
const snapshot=JSON.parse(fs.readFileSync(output,'utf8'));
assert(Date.now()-Date.parse(snapshot.capturedAt)<5*60*1000);
const normal=s=>s.toLowerCase().replace(/[^a-z0-9]/g,'');
const starters=new Set(['QB','RB','WR','TE','W/R/T','K','DEF']);
const targets=[['Futball in the Groin',[['George Kittle','start'],['Rhamondre Stevenson','start']]],['Bears',[['Jaylen Waddle','start'],['Michael Wilson','bench']]],['Guinness',[['Tyler Shough','start'],['C.J. Stroud','bench']]]];
const checks=targets.map(([team,players])=>({team,players:players.map(([name,expected])=>{
 const row=snapshot.games.flatMap(g=>g.rows).find(r=>normal(r.team_name)===normal(team)&&normal(r.player_name)===normal(name));
 const state=row&&starters.has(row.slot)?'start':row?.slot==='BN'?'bench':'other';
 assert.equal(state,expected,`STOP DEPLOYMENT: ${team} / ${name} changed`);
 return {name,state,projected:row.projected};
})}));
const report={capturedAt:snapshot.capturedAt,checkedAt:new Date().toISOString(),checks,pass:true,projectionGapIsNotSpoken:true,projectionGapTestApplied:false,cardDataRemainsAsOf:manifest.lineupCheckedAt,cardStampNotRelabelledAsNewer:true,releaseSHA256:manifest.sha256};
fs.writeFileSync('docs/releases/weekly-slate-2026-week-05-final-lineup-check.json',JSON.stringify(report,null,2)+'\n');
console.log('Final lineup gate passed: all three spoken starter/bench configurations match. No projection-gap assertion remains.');
