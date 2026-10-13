'use strict';
window.CrateTimeline = (songs,esc) => {
 const years=songs.flatMap(s=>[s.year,...s.samples.filter(x=>x.year).map(x=>x.year)]);
 const start=Math.floor(Math.min(...years)/5)*5,end=Math.ceil(Math.max(...years)/5)*5,left=410,px=28,W=left+(end-start)*px+110,H=80+songs.length*72;
 const xx=y=>left+(y-start)*px;
 let svg='<rect width="'+W+'" height="'+H+'" fill="#fff"/><rect x="'+xx(1990)+'" y="38" width="'+(10*px)+'" height="'+(H-38)+'" fill="#006cb608"/>';
 for(let y=start;y<=end;y++){const x=xx(y);svg+='<line x1="'+x+'" y1="38" x2="'+x+'" y2="'+H+'" stroke="'+(y%5===0?'#d3dce3':'#edf0f3')+'"/>'+(y%5===0?'<text x="'+x+'" y="26" font-size="11" fill="#626971">'+y+'</text>':'')}
 songs.forEach((s,i)=>{const y=72+i*72,x=xx(s.year),sample=s.samples.find(q=>q.main&&q.year);svg+='<line x1="15" y1="'+(y+42)+'" x2="'+W+'" y2="'+(y+42)+'" stroke="#edf0f3"/><a href="#/song/'+s.id+'"><title>'+esc(s.title+' / '+s.artist)+'</title><text x="18" y="'+y+'" font-size="13" fill="#101114" font-weight="600" textLength="'+Math.min(365,s.title.length*7)+'" lengthAdjust="spacingAndGlyphs">'+esc(s.title)+'</text><text x="18" y="'+(y+20)+'" font-size="10" fill="#626971">'+esc(s.artist+' / '+s.region)+'</text><circle cx="'+x+'" cy="'+(y-4)+'" r="6" fill="#006cb6"/><text x="'+(x+10)+'" y="'+y+'" fill="#006cb6" font-size="11">'+s.year+'</text></a>';if(sample){const sx=xx(sample.year);svg+='<line x1="'+sx+'" y1="'+(y-4)+'" x2="'+(x-8)+'" y2="'+(y-4)+'" stroke="#95adbe" stroke-dasharray="3 4"/><circle cx="'+sx+'" cy="'+(y-4)+'" r="4" fill="#626971"/><text x="'+sx+'" y="'+(y+24)+'" fill="#626971" font-size="10">'+esc(sample.year+' / '+sample.title)+'</text>'}});
 return '<div class="tl-scroll" tabindex="0" aria-label="楽曲とサンプル元の年表。上下左右にスクロールできます"><svg width="'+W+'" height="'+H+'" viewBox="0 0 '+W+' '+H+'" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="'+songs.length+'曲の年代順年表">'+svg+'</svg></div>';
};
