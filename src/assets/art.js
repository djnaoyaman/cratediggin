/* Per-track generated artwork; original canvas lettering remains a loading/error fallback. */
(()=>{
 const imageCache=new Map(),failedImages=new Set();
 const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
 const rand=seed=>()=>{seed|=0;seed=seed+0x6D2B79F5|0;let t=Math.imul(seed^seed>>>15,1|seed);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296};
 let frame=0,started=0,current=null,texture=null,paint=null,width=0,height=0,visible=false;
 const cv=document.getElementById('wall'),ctx=cv.getContext('2d');
 function size(){const d=Math.min(devicePixelRatio||1,1.5);width=innerWidth;height=innerHeight;cv.width=width*d;cv.height=height*d;ctx.setTransform(d,0,0,d,0,0);if(current)prepare(current)}
 function artworkURL(song){return song.art.image?new URL(song.art.image,(window.CRATE_SITE_URL||location.origin).replace(/\/$/,'')+'/').href:null}
 function artwork(song){const url=artworkURL(song);if(!url||failedImages.has(url))return null;if(imageCache.has(url))return imageCache.get(url);const image=new Image();image.decoding='async';imageCache.set(url,image);while(imageCache.size>4){const first=imageCache.keys().next().value;if(first===url)break;imageCache.delete(first)}image.onload=()=>{if(visible&&artworkURL(current)===url){cancelAnimationFrame(frame);frame=requestAnimationFrame(draw)}};image.onerror=()=>{failedImages.add(url);imageCache.delete(url);if(visible&&artworkURL(current)===url){prepare(current);cancelAnimationFrame(frame);frame=requestAnimationFrame(draw)}};image.src=url;return image}
 function prepare(song){
  current=song;const generated=artwork(song);document.getElementById('art-view').classList.toggle('image-art',!!generated);if(generated){texture=null;paint=null;return;}const r=rand(song.art.seed),W=width,H=height;
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
  const generated=artwork(current);if(generated){ctx.clearRect(0,0,width,height);ctx.fillStyle='#faf9f5';ctx.fillRect(0,0,width,height);if(generated.complete&&generated.naturalWidth){const landscape=width>height,top=landscape?48:70,bottom=landscape?92:170,space=Math.max(80,height-top-bottom),scale=Math.min(width/generated.naturalWidth,space/generated.naturalHeight),w=generated.naturalWidth*scale,h=generated.naturalHeight*scale;ctx.save();ctx.globalAlpha=reduced?1:Math.min(1,(ts-started)/650);ctx.drawImage(generated,(width-w)/2,top+(space-h)/2,w,h);ctx.restore();}if(!reduced&&ts-started<900)frame=requestAnimationFrame(draw);return;}
const primary=(current.art.palette||['#006cb6'])[0];const t=(ts-started)/1000,cycle=reduced?25:t%30;ctx.clearRect(0,0,width,height);ctx.drawImage(texture,0,0);
  // The wall gets painted left to right, settles, then receives a fresh pass.
  const progress=Math.min(1,cycle/(current.art.style==='blockbuster'?5:current.art.style==='piece'?13:9)),edge=(width+100)*progress;
  ctx.save();ctx.beginPath();if(current.art.style==='piece'){ctx.arc(width*.5,height*.46,Math.hypot(width,height)*progress,0,Math.PI*2)}else if(current.art.style==='blockbuster'){ctx.rect(0,0,width,height*progress)}else{ctx.rect(0,0,edge,height)}ctx.clip();ctx.drawImage(paint,0,0);ctx.restore();
  if(progress<1){const g=ctx.createLinearGradient(edge-55,0,edge+25,0);g.addColorStop(0,primary+'00');g.addColorStop(.5,'#74c9ff32');g.addColorStop(1,primary+'00');ctx.fillStyle=g;ctx.fillRect(edge-55,height*.23,80,height*.43)}
  if(!reduced){const sway=Math.sin(t*.11)*9;ctx.globalAlpha=.07;ctx.fillStyle='#b6dcff';ctx.fillRect(0,height*.83+sway,width,1);ctx.globalAlpha=1;frame=requestAnimationFrame(draw)}
 }
 window.CrateArt={show(song){visible=true;started=0;size();prepare(song);cancelAnimationFrame(frame);frame=requestAnimationFrame(draw);if(document.fonts)document.fonts.ready.then(()=>{if(visible){prepare(current);if(reduced)draw(performance.now())}})},change(song){cv.style.opacity='0';setTimeout(()=>{if(!visible)return;prepare(song);started=0;cv.style.opacity='1';cancelAnimationFrame(frame);frame=requestAnimationFrame(draw)},400)},hide(){visible=false;cancelAnimationFrame(frame)}};
 addEventListener('resize',()=>{if(visible){size();if(reduced||artwork(current))draw(performance.now())}});
 document.addEventListener('visibilitychange',()=>{if(document.hidden)cancelAnimationFrame(frame);else if(visible&&!reduced)frame=requestAnimationFrame(draw)});
})();
