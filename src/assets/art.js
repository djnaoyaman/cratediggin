/* Per-track generated artwork; configured images show only their own wall while loading or on failure. */
(()=>{
 const imageCache=new Map(),failedImages=new Set();
 const motionPreference=matchMedia('(prefers-reduced-motion: reduce)');
 let reduced=motionPreference.matches,motionSettled=false;
 const rand=seed=>()=>{seed|=0;seed=seed+0x6D2B79F5|0;let t=Math.imul(seed^seed>>>15,1|seed);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296};
 let frame=0,started=0,current=null,texture=null,paint=null,width=0,height=0,visible=false,motion=null;
 const cv=document.getElementById('wall'),ctx=cv.getContext('2d');
 function size(){const d=Math.min(devicePixelRatio||1,1.5);width=innerWidth;height=innerHeight;cv.width=width*d;cv.height=height*d;ctx.setTransform(d,0,0,d,0,0);if(current)prepare(current)}
 function artworkURL(song){return song.art.image?new URL(song.art.image,(window.CRATE_SITE_URL||location.origin).replace(/\/$/,'')+'/').href:null}
 function artwork(song){const url=artworkURL(song);if(!url||failedImages.has(url))return null;if(imageCache.has(url))return imageCache.get(url);const image=new Image();image.decoding='async';imageCache.set(url,image);while(imageCache.size>4){const first=imageCache.keys().next().value;if(first===url)break;imageCache.delete(first)}image.onload=()=>{if(visible&&artworkURL(current)===url){started=0;cancelAnimationFrame(frame);frame=requestAnimationFrame(draw)}};image.onerror=()=>{failedImages.add(url);imageCache.delete(url);if(visible&&artworkURL(current)===url){prepare(current);cancelAnimationFrame(frame);frame=requestAnimationFrame(draw)}};image.src=url;return image}
 function wallPalette(song){
  const colors=(song.art.palette||['#888888']).map(hex=>{const n=parseInt(hex.slice(1),16),r=(n>>16)/255,g=(n>>8&255)/255,b=(n&255)/255,max=Math.max(r,g,b),min=Math.min(r,g,b),d=max-min,l=(max+min)/2;let h=0;if(d){h=max===r?((g-b)/d)%6:max===g?(b-r)/d+2:(r-g)/d+4;h=(h*60+360)%360}return {h,s:d?d/(1-Math.abs(2*l-1)):0,l}});
  const accent=colors.reduce((a,b)=>b.s*Math.min(b.l,1-b.l)>a.s*Math.min(a.l,1-a.l)?b:a),average=colors.reduce((n,c)=>n+c.l,0)/colors.length;
  const seed=[...(song.id||song.title||'')].reduce((n,c)=>(Math.imul(n,31)+c.charCodeAt(0))>>>0,song.art.seed||0),light=average<.52?84:74,saturation=accent.s<.12?2:Math.round(5+accent.s*11);
  const tone=offset=>`hsl(${Math.round(accent.h)} ${saturation}% ${Math.max(0,Math.min(96,light+offset))}%)`;
  return {seed,kind:seed%3,top:tone(9),middle:tone(0),bottom:tone(-10)};
 }
 const motionProfiles={drift:{duration:6200,energy:.2},groove:{duration:3900,energy:.48},stomp:{duration:2600,energy:.74},burst:{duration:1500,energy:.95}};
 const clamp=n=>Math.max(0,Math.min(1,n));
 const smooth=n=>n*n*(3-2*n);
 function motionFor(song){const choice=song.art?.motion||{},mode=Object.hasOwn(motionProfiles,choice.mode)?choice.mode:'groove',profile=motionProfiles[mode],seed=(song.art?.seed||0)>>>0;return {mode,duration:Number.isFinite(choice.duration)?Math.max(1000,Math.min(8000,choice.duration)):profile.duration,energy:Number.isFinite(choice.energy)?clamp(choice.energy):profile.energy,variant:Number.isInteger(choice.variant)?((choice.variant%4)+4)%4:seed%4}}
 function reveal(source,box,elapsed,composite='source-over'){
  const {x,y,w,h}=box,p=(reduced||motionSettled)?1:clamp(elapsed/motion.duration),v=motion.variant;
  ctx.save();ctx.globalCompositeOperation=composite;
  if(p<1){
   if(motion.mode==='drift'){
    ctx.globalAlpha=smooth(p);const scale=.975+.025*smooth(p),cx=x+w/2,cy=y+h/2;ctx.translate(cx,cy);ctx.scale(scale,scale);ctx.translate(-cx,-cy);ctx.translate((v%2?1:-1)*(1-p)*w*.018,(1-p)*h*.025);
   }else{
    ctx.beginPath();
    if(motion.mode==='groove'){
     if(v===0){const bands=8,bh=h/bands;for(let i=0;i<bands;i++){const q=smooth(clamp(p*1.5-i*.065)),rw=w*q;ctx.rect(i%2?x+w-rw:x,y+i*bh,rw,bh+1)}}
     else if(v===1){const edge=x+w*smooth(p);ctx.moveTo(x-2,y-2);ctx.lineTo(edge,y-2);for(let yy=y;yy<=y+h+12;yy+=12)ctx.lineTo(edge+Math.sin(yy*.08+p*7)*9,yy);ctx.lineTo(x-2,y+h+12);ctx.closePath()}
     else if(v===2){const order=[4,0,8,2,6,1,7,3,5],cw=w/3,ch=h/3;order.forEach((cell,i)=>{const q=smooth(clamp(p*1.8-i*.1)),cx=x+(cell%3+.5)*cw,cy=y+(Math.floor(cell/3)+.5)*ch;ctx.rect(cx-cw*q/2,cy-ch*q/2,cw*q+1,ch*q+1)})}
     else{const cw=w/6;for(let i=0;i<6;i++){const q=smooth(clamp(p*1.65-(5-i)*.11)),rh=h*q;ctx.rect(x+i*cw,i%2?y+h-rh:y,cw+1,rh)}}
    }else if(motion.mode==='stomp'){
     const order=v%2?[0,2,4,1,3]:[2,1,3,0,4],cw=w/5;order.forEach((column,i)=>{const q=1-Math.pow(1-clamp(p*1.85-i*.19),3),rh=h*q;ctx.rect(x+column*cw,(column+v)%2?y+h-rh:y,cw+1,rh)})
    }else{
     const cx=x+w*(v%2?.43:.57),cy=y+h*(v<2?.43:.57),radius=Math.hypot(w,h)*.62*(1-Math.pow(1-p,2));ctx.arc(cx,cy,radius,0,Math.PI*2);
    }
    ctx.clip();
   }
  }
  ctx.drawImage(source,x,y,w,h);ctx.restore();return p;
 }
 function prepareWall(song){
  const W=width,H=height,wall=wallPalette(song),r=rand(wall.seed);
  texture=document.createElement('canvas');texture.width=W;texture.height=H;const t=texture.getContext('2d');
  const light=t.createLinearGradient(0,0,W,H);light.addColorStop(0,wall.top);light.addColorStop(.55,wall.middle);light.addColorStop(1,wall.bottom);t.fillStyle=light;t.fillRect(0,0,W,H);
  const bh=wall.kind===1?76:280,bw=wall.kind===1?220:560;t.lineWidth=wall.kind===1?2:1;
  if(wall.kind!==2)for(let y=0;y<H;y+=bh){t.strokeStyle='#34332b20';t.beginPath();t.moveTo(0,y);t.lineTo(W,y);t.stroke();t.strokeStyle='#ffffff32';t.beginPath();t.moveTo(0,y+2);t.lineTo(W,y+2);t.stroke();for(let x=wall.kind===1?(y/bh%2)*-bw/2:0;x<W;x+=bw){t.strokeStyle='#34332b18';t.beginPath();t.moveTo(x,y);t.lineTo(x,y+bh);t.stroke()}}
  if(wall.kind===2)for(let i=0;i<32;i++){t.fillStyle=i%2?'#ffffff08':'#34332b06';t.beginPath();t.ellipse(r()*W,r()*H,40+r()*150,15+r()*60,r()*Math.PI,0,Math.PI*2);t.fill()}
  for(let i=0;i<Math.min(26000,W*H/35);i++){const a=r(),z=.3+r()*1.8;t.fillStyle=a>.5?'#ffffff24':'#39372f1c';t.fillRect(r()*W,r()*H,z,z)}
  for(let i=0;i<16;i++){let x=r()*W,y=r()*H;t.strokeStyle='#4a463a1a';t.lineWidth=.4+r();t.beginPath();t.moveTo(x,y);for(let j=0;j<5;j++){x+=(r()-.5)*30;y+=r()*24;t.lineTo(x,y)}t.stroke()}
  const shade=t.createRadialGradient(W*.5,H*.43,W*.18,W*.5,H*.43,Math.hypot(W,H)*.6);shade.addColorStop(0,'#00000000');shade.addColorStop(1,'#27251d28');t.fillStyle=shade;t.fillRect(0,0,W,H);
 }
 function prepare(song){
  current=song;motion=motionFor(song);const room=document.getElementById('art-view');if(room.dataset){room.dataset.motion=motion.mode;room.dataset.motionVariant=String(motion.variant);}const semantic=document.getElementById('artwork-image');if(song.art.image){semantic.alt=song.art.alt||song.title+' — '+song.artist+'｜CRATE DIGGIN｜DJ Naoyaman';semantic.loading='eager';semantic.src=artworkURL(song);semantic.hidden=false}else{semantic.hidden=true;semantic.alt='';semantic.removeAttribute('src')}const generated=artwork(song);document.getElementById('art-view').classList.toggle('image-art',!!song.art.image);if(song.art.image){prepareWall(song);paint=null;return;}const r=rand(song.art.seed),W=width,H=height;
  const colors=song.art.palette||['#006cb6','#ffffff','#60baff','#17212a'];
  const [primary,secondary,accent,bg]=colors;
  const chicago=song.art.profile==='chicago-piano',queens=song.art.profile==='queens-throwup';const la=song.art.profile==='la-open-sky';const oak=song.art.profile==='oakland-handstyle',newark=song.art.profile==='newark-industrial',brooklyn=song.art.profile==='brooklyn-brick';
  texture=document.createElement('canvas');texture.width=W;texture.height=H;const t=texture.getContext('2d');
  t.fillStyle=bg;t.fillRect(0,0,W,H);
  // Concrete / brick surface and accumulated paint remain behind the new piece.
  const brickH=song.art.style==='blockbuster'?90:55,brickW=170;t.strokeStyle='#ffffff09';t.lineWidth=2;
  for(let y=0;y<H;y+=brickH){t.beginPath();t.moveTo(0,y);t.lineTo(W,y);t.stroke();for(let x=(y/brickH%2)*-brickW/2;x<W;x+=brickW){t.beginPath();t.moveTo(x,y);t.lineTo(x,y+brickH);t.stroke()}}
  if(chicago){t.strokeStyle=secondary+'30';t.lineWidth=2;for(let x=-H;x<W;x+=60){t.beginPath();t.moveTo(x,0);t.lineTo(x+H,H);t.stroke();}}
  if(la){const sky=t.createLinearGradient(0,0,0,H);sky.addColorStop(0,bg);sky.addColorStop(.62,primary+'80');sky.addColorStop(1,bg);t.fillStyle=sky;t.fillRect(0,0,W,H);t.strokeStyle=secondary+'44';t.lineWidth=3;t.beginPath();t.moveTo(0,H*.68);t.lineTo(W,H*.68);t.stroke();}
  if(newark){t.fillStyle=primary+'18';for(let x=0;x<W;x+=90){t.fillRect(x,0,26,H);t.fillStyle=accent+'22';t.fillRect(x+25,0,2,H);t.fillStyle=primary+'18';}t.strokeStyle=secondary+'40';t.lineWidth=8;t.strokeRect(W*.06,H*.12,W*.88,H*.65);}
  if(brooklyn){t.fillStyle=primary+'15';t.fillRect(0,H*.16,W,H*.55);t.strokeStyle=accent+'40';t.lineWidth=5;for(let y=H*.16;y<H*.73;y+=brickH){t.beginPath();t.moveTo(0,y);t.lineTo(W,y);t.stroke();}}
  if(song.art.style==='subway'){t.fillStyle=primary+'2b';t.fillRect(0,H*.15,W,H*.58);t.strokeStyle='#ffffff26';for(let y=H*.15;y<H*.73;y+=18){t.beginPath();t.moveTo(0,y);t.lineTo(W,y);t.stroke()}}
  if(song.art.style==='piece'&&!chicago){for(let i=0;i<12;i++){t.strokeStyle=i%2?primary+'30':secondary+'12';t.lineWidth=3;t.beginPath();t.arc(W*.5,H*.47,30+i*32,0,Math.PI*2);t.stroke()}}
  for(let i=0;i<Math.min(16000,W*H/100);i++){t.fillStyle=r()>.5?'#ffffff0c':'#00000030';const z=r()*2;t.fillRect(r()*W,r()*H,z,z)}
  t.save();t.translate(W*.5,H*.47);t.rotate(-.11);const g=t.createRadialGradient(0,0,0,0,0,W*.52);g.addColorStop(0,primary+'40');g.addColorStop(1,primary+'00');t.fillStyle=g;t.fillRect(-W,-H,W*2,H*2);t.restore();
  // Distant ghost tags / buff marks, never an imitation of an identifiable writer.
  t.save();t.globalAlpha=.085;t.font=`${Math.min(W*.11,120)}px 'Permanent Marker',cursive`;t.fillStyle='#fff';t.translate(W*.04,H*.24);t.rotate(-.12);t.fillText('KEEP DIGGIN',0,0);t.restore();
  paint=document.createElement('canvas');paint.width=W;paint.height=H;const p=paint.getContext('2d');
  const portrait=W/H<.9,lines=portrait?(song.art.lines||[song.art.word]):[song.art.word];
  const max=portrait?W*.83:W*.82,base=portrait?Math.min(W*.31,H*.19):Math.min(W*.13,H*.33),gap=base*.87;
  const kind=song.art.lettering||'block';
  const designs={
   subway:{font:"'Barlow Condensed',Impact,sans-serif",skew:-.12,angle:-.045,outline:.07,depth:10,drips:3},
   tag:{font:"'Caveat','Permanent Marker',cursive",skew:-.18,angle:-.09,outline:0,depth:0,drips:0},
   bubble:{font:"'Luckiest Guy','Permanent Marker',cursive",skew:0,angle:.035,outline:.13,depth:3,drips:4},
   block:{font:"'Bungee',Impact,sans-serif",skew:0,angle:0,outline:.04,depth:14,drips:0},
   stencil:{font:"'Black Ops One',Impact,sans-serif",skew:0,angle:-.06,outline:.015,depth:0,drips:0},
   angular:{font:"'Rubik Mono One',monospace",skew:-.2,angle:-.03,outline:.06,depth:7,drips:1},
   brush:{font:"'Permanent Marker',cursive",skew:-.1,angle:-.06,outline:.025,depth:0,drips:1}
  },d=designs[kind]||designs.block;
  p.save();p.translate(W*.5,H*(portrait?.43:.46));p.rotate(d.angle);p.transform(1,0,d.skew,1,0,0);p.textAlign='center';p.textBaseline='middle';p.lineJoin=kind==='angular'?'miter':'round';
  lines.forEach((line,li)=>{
   let fs=base;p.font=`900 ${fs}px ${d.font}`;const measured=p.measureText(line).width;if(measured>max)fs*=max/measured;
   p.font=`900 ${fs}px ${d.font}`;const y=(li-(lines.length-1)/2)*gap,len=p.measureText(line).width;
   if(kind==='bubble'||kind==='angular'){
    const chars=[...line],widths=chars.map(c=>p.measureText(c).width),total=widths.reduce((a,b)=>a+b,0);let x=-total/2;
    chars.forEach((c,i)=>{const cw=widths[i];p.save();p.translate(x+cw/2,y+(i%2?-1:1)*fs*(kind==='bubble'?.025:.045));p.rotate((i%2?1:-1)*(kind==='bubble'?.06:.045));p.scale(kind==='bubble'?1.04:1,kind==='bubble'?1.08:1+(i%3)*.05);
     p.strokeStyle=secondary;p.lineWidth=fs*d.outline;p.strokeText(c,0,0);p.strokeStyle=bg;p.lineWidth=fs*d.outline*.55;p.strokeText(c,0,0);p.fillStyle=kind==='bubble'?primary:(i%2?accent:primary);p.fillText(c,0,0);p.restore();x+=cw;});
   }else{
    for(let j=d.depth;j>0;j--){p.fillStyle=accent;p.fillText(line,j*.8,y+j);}
    if(d.outline){p.strokeStyle=secondary;p.lineWidth=fs*d.outline;p.strokeText(line,0,y);}
    p.fillStyle=kind==='tag'||kind==='brush'?secondary:primary;p.fillText(line,0,y);
    if(kind==='tag'){p.globalAlpha=.4;p.fillStyle=accent;p.fillText(line,2,y+2);p.globalAlpha=1;}
   }
   for(let j=0;j<d.drips;j++){const x=(r()-.5)*len*.8,yy=y+fs*.29,drop=fs*(.08+r()*.2);p.strokeStyle=primary;p.lineWidth=2+r()*3;p.lineCap='round';p.beginPath();p.moveTo(x,yy);p.lineTo(x,yy+drop);p.stroke();}
  });
  const by=gap*lines.length*.53;
  if(kind==='tag'||kind==='brush'){p.strokeStyle=accent;p.lineWidth=kind==='tag'?2:5;p.beginPath();p.moveTo(-max*.4,by);p.bezierCurveTo(-max*.1,by+18,max*.2,by-10,max*.43,by-14);p.stroke();}
  if(kind==='angular'){p.strokeStyle=secondary;p.lineWidth=3;for(let i=0;i<3;i++){const x=(i-1)*max*.25;p.beginPath();p.moveTo(x,by);p.lineTo(x+base*.25,by+base*.22);p.lineTo(x+base*.08,by+base*.19);p.stroke();}}
  if(kind==='stencil'){p.strokeStyle=accent;p.lineWidth=2;p.beginPath();p.moveTo(-max*.45,by);p.lineTo(max*.4,by-5);p.lineTo(max*.34,by-16);p.stroke();}
  p.restore();
  // Spray overshoot: dots around the lettering, rather than unrelated particles.
  for(let i=0;i<320;i++){const a=r()*Math.PI*2,rx=W*(.2+r()*.25),ry=H*(.1+r()*.11);p.fillStyle=i%3?primary+'3d':secondary+'5b';p.beginPath();p.arc(W*.5+Math.cos(a)*rx,H*.46+Math.sin(a)*ry,r()*2+.4,0,Math.PI*2);p.fill()}
  p.save();p.translate(W*.7,H*.72);p.rotate(-.12);p.textAlign='right';p.font=`${Math.min(W*.047,38)}px 'Permanent Marker',cursive`;p.fillStyle=secondary;p.fillText(song.art.tag,0,0);p.font=`${Math.min(W*.025,19)}px 'Permanent Marker',cursive`;p.fillStyle=accent;p.fillText('Crate Diggin’ / One love.',0,33);p.restore();
 }
 function draw(ts){if(!visible)return;if(!started)started=ts;
  const elapsed=ts-started,generated=artwork(current);ctx.clearRect(0,0,width,height);ctx.drawImage(texture,0,0);
  let progress=(reduced||motionSettled)?1:clamp(elapsed/motion.duration);
  if(current.art.image){
   if(generated&&generated.complete&&generated.naturalWidth){
    const landscape=width>height,top=landscape?48:70,bottom=landscape?92:170,space=Math.max(80,height-top-bottom),scale=Math.min(width/generated.naturalWidth,space/generated.naturalHeight),w=generated.naturalWidth*scale,h=generated.naturalHeight*scale;
    progress=reveal(generated,{x:(width-w)/2,y:top+(space-h)/2,w,h},elapsed,current.art.transparent?'source-over':'multiply');
   }
  }else progress=reveal(paint,{x:0,y:0,w:width,h:height},elapsed);
  if(!reduced&&!motionSettled&&progress<1)frame=requestAnimationFrame(draw);
 }
 // A preference change settles this display, including any image that loads later.
 const onMotionPreferenceChange=event=>{
  reduced=event.matches;
  if(!visible)return;
  motionSettled=true;
  cancelAnimationFrame(frame);
  draw(performance.now());
 };
 if(motionPreference.addEventListener)motionPreference.addEventListener('change',onMotionPreferenceChange);
 else if(motionPreference.addListener)motionPreference.addListener(onMotionPreferenceChange);
 window.CrateArt={motionFor,show(song){cancelAnimationFrame(frame);current=song;visible=true;motionSettled=false;started=0;cv.style.opacity='1';size();draw(performance.now());if(document.fonts)document.fonts.ready.then(()=>{if(visible){prepare(current);cancelAnimationFrame(frame);draw(performance.now())}})},change(song){if(!visible)return;cancelAnimationFrame(frame);prepare(song);motionSettled=false;started=0;cv.style.opacity='1';draw(performance.now())},hide(){visible=false;cancelAnimationFrame(frame)}};
 addEventListener('resize',()=>{if(visible){size();cancelAnimationFrame(frame);draw(performance.now())}});
 document.addEventListener('visibilitychange',()=>{if(document.hidden)cancelAnimationFrame(frame);else if(visible&&!reduced)frame=requestAnimationFrame(draw)});
})();
