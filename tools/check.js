// Checks every page at 320, 390 and 1366 px, light and dark: sideways scroll, top bar height on phones,
// links under 24 px, and anything loaded from another site. Prints CHECK lines for problems, then done.
// Run from the repository root: node tools/check.js
const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch();const base='file://'+require('path').resolve(__dirname,'../site')+'/';
const pages=['index.html','designs/1.html','designs/2.html','designs/newsroom.html','designs/5.html','designs/index.html','designs/4.html','designs/profile.html','start/index.html','agents/index.html','admin/index.html','admin/board.html','admin/policy.html','admin/made.html','admin/guide/index.html','admin/guide/05-images.html','admin/guide/09-interview.html'];
for(const pg of pages) for(const [w,h] of [[320,700],[390,844],[1366,900]]) for(const s of ['light','dark']){
 const p=await b.newPage({viewport:{width:w,height:h},colorScheme:s});let bytes=0;
 p.on('response',async r=>{try{bytes+=(await r.body()).length}catch{}});
 await p.goto(base+pg,{waitUntil:'load'});
 const r=await p.evaluate(()=>{
  const sw=document.documentElement.scrollWidth;
  const pick=document.querySelector('.pick'),fam=document.querySelector('.family');
  const hdr=Math.round(pick?pick.getBoundingClientRect().bottom:0);
  const small=[...document.querySelectorAll('a,button,summary')].filter(e=>{const c=e.getBoundingClientRect();if(!c.width||getComputedStyle(e).visibility=='hidden')return false;
   if(e.closest('p,li')&&e.closest('p')&&e.closest('p').textContent.trim().length>e.textContent.trim().length+5)return false; // inline in sentence
   return c.height<24&&e.offsetParent!==null}).map(e=>e.textContent.trim().slice(0,30));
  const ext=[...document.querySelectorAll('[src],link[href]:not([rel=canonical])')].map(e=>e.src||e.href).filter(u=>/^https?:/.test(u));
  return {sw,hdr,small:small.slice(0,4),ext};});
 const bad=r.sw>w||r.ext.length||r.small.length||(w<=390&&r.hdr>210);
 if(bad) console.log('CHECK',pg,w,s,JSON.stringify(r));
 if(w==1366&&s=='light'&&pg=='index.html') console.log('first load bytes home',bytes);
 await p.close();}
console.log('done');await b.close();})();
