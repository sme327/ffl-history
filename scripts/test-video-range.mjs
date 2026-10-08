import assert from 'node:assert/strict';
import {sliceVideo, videoRange} from '../worker/video-range.ts';
assert.deepEqual(videoRange('bytes=0-31',100),{start:0,end:31});
assert.deepEqual(videoRange('bytes=90-',100),{start:90,end:99});
assert.deepEqual(videoRange('bytes=-10',100),{start:90,end:99});
assert.deepEqual(videoRange('bytes=90-999',100),{start:90,end:99});
for(const range of ['bytes=100-','bytes=90-89','bytes=-0'])assert.equal(videoRange(range,100),'unsatisfiable');
for(const range of ['bytes=0-1,4-5','bytes=-','items=1-2','bytes=NaN-2'])assert.equal(videoRange(range,100),null);
for(const [start,end] of [[0,31],[45,77],[99,99]]){
 let cancelled=false;
 const input=new ReadableStream({start(c){for(let i=0;i<100;i+=7)c.enqueue(Uint8Array.from({length:Math.min(7,100-i)},(_,j)=>i+j));},cancel(){cancelled=true;}});
 const actual=new Uint8Array(await new Response(sliceVideo(input,start,end)).arrayBuffer());
 assert.deepEqual([...actual],Array.from({length:end-start+1},(_,i)=>start+i));assert(cancelled);
}
console.log('Video ranges: bounded, open, suffix, unsatisfiable, multipart fallback and chunked streaming pass.');
