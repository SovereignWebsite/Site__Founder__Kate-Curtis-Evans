// Run from the repository root: node tools/thumbs.js  (needs Playwright and Python with Pillow)
// Screenshot the first screen of each design into site/img/designs/<slug>.webp at 640 px wide.
const {chromium}=require('playwright');
const {execFileSync}=require('child_process');
const fs=require('fs');
const site=require('path').resolve(__dirname,'../site')+'/';
const D=[['index.html','board','light'],['designs/1.html','transcript','light'],['designs/2.html','edit','dark'],['designs/newsroom.html','newsroom','dark'],['designs/5.html','brief','light']];
(async()=>{const b=await chromium.launch();fs.mkdirSync(site+'img/designs',{recursive:true});
for(const [f,slug,scheme] of D){
  const p=await b.newPage({viewport:{width:1280,height:800},colorScheme:scheme,deviceScaleFactor:1});
  await p.goto('file://'+site+f);
  await p.addStyleTag({content:'.pick,.family{display:none!important}'});
  await p.waitForTimeout(300);
  const png=require('os').tmpdir()+'/thumb-'+slug+'.png';
  await p.screenshot({path:png});
  execFileSync('python3',['-c',`from PIL import Image;Image.open('${png}').convert('RGB').resize((640,400)).save('${site}img/designs/${slug}.webp','WEBP',quality=72)`]);
  console.log(slug,fs.statSync(site+'img/designs/'+slug+'.webp').size);
  await p.close();}
await b.close();})();
