const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const router=fs.readFileSync('src/app/router.js','utf8'),fn=router.match(/ function artDockGeometry[^\n]+/)[0],context={};vm.runInNewContext(fn+';this.geometry=artDockGeometry',context);
for(const inline of [false,true])for(const [w,h] of [[320,900],[390,844],[768,900],[1280,900]]){const b=context.geometry(w,h,inline);assert(b);assert(b.width>=200&&b.height>=(inline?42:200));assert(b.left>=0&&b.top>=0&&b.left+b.width<=w&&b.top+b.height<=h);assert(b.artWidth<=b.left||b.artHeight<=b.top,'ART and provider areas are disjoint');assert(b.artWidth>=300&&b.artHeight>=420)}
for(const [w,h] of [[200,900],[320,420]])assert.equal(context.geometry(w,h,false),null);
for(const [w,h] of [[568,320],[600,320],[667,320],[740,360],[844,390]]){const b=context.geometry(w,h,false);assert(b&&b.height===200&&b.artWidth>=260);assert(b.left+b.width<=w&&b.top+b.height<=h)}
assert(!router.includes('requestFullscreen'));assert(!router.includes('exitFullscreen'));assert(!router.includes("e.key==='Tab'"),'No button-only modal trap');assert(router.includes('artPreviousOverflow'));assert(router.includes('frame?.isConnected'));
const template=fs.readFileSync('templates/index.html','utf8');assert(template.includes('role="region" aria-label="アートとプレイヤー"'));assert(!template.includes('aria-modal="true"'));assert(template.includes('</div><button class="start-overlay"'),'Start control outside provider viewport');
const css=fs.readFileSync('src/assets/style.css','utf8');assert(css.includes('.art-provider-dock iframe[hidden]{display:none!important}'));
console.log('ART geometry, insufficient-space refusal, nonmodal source contract and hidden native-owner isolation passed; browser geometry remains separate');
