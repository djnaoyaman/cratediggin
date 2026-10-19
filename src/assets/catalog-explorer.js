'use strict';
(function(root){
 const missing='__missing__',keys=['type','decade','year','region','artist','producer','category','sound','q'];
 const dimensions=[['decade','年代'],['region','登録された地域'],['artist','アーティスト名義'],['producer','制作クレジット'],['category','掲載カテゴリ'],['sound','音のタグ']];
 const types={single:'楽曲',mix:'ミックス作品',live_video:'ライブ映像',album:'アルバム'};
 const strings=v=>[...new Set((Array.isArray(v)?v:[]).filter(x=>typeof x==='string'&&x.trim()))];
 const knownYear=t=>Number.isInteger(t.year)&&!Number.isNaN(t.year);
 function values(t,key){if(key==='type')return[t.workType||'single'];if(key==='year')return[knownYear(t)?String(t.year):missing];if(key==='decade')return[knownYear(t)?String(Math.floor(t.year/10)*10):missing];if(key==='producer'||key==='sound'){const x=strings(t[key==='producer'?'producers':'sounds']);return x.length?x:[missing]}return[typeof t[key]==='string'&&t[key].trim()?t[key]:missing]}
 function unique(records){const seen=new Set();return records.filter(t=>t&&typeof t.id==='string'&&!seen.has(t.id)&&seen.add(t.id))}
 function parse(input){const p=input instanceof URLSearchParams?input:new URLSearchParams(String(input||'').startsWith('#/')?String(input).slice(String(input).indexOf('?')+1):String(input||''));const s={};for(const k of keys){const v=p.get(k);if(v&&v.length<=200)s[k]=v}return s}
 function serialize(state){const p=new URLSearchParams();for(const k of keys)if(typeof state[k]==='string'&&state[k])p.set(k,state[k]);return p.toString()}
 function filter(records,state={}){return unique(records).filter(t=>keys.every(k=>!state[k]||(k==='q'?([t.title,t.artist].join(' ').normalize('NFKC').toLowerCase().includes(state[k].trim().normalize('NFKC').toLowerCase())):values(t,k).includes(state[k]))))}
 function aggregate(records,key){const map=new Map();for(const t of unique(records))for(const v of values(t,key))map.set(v,(map.get(v)||0)+1);return [...map].map(([value,count])=>({value,count})).sort((a,b)=>a.value===missing?1:b.value===missing?-1:key==='decade'||key==='year'?Number(a.value)-Number(b.value):b.count-a.count||a.value.localeCompare(b.value,'ja'))}
 function label(key,value){if(value===missing)return key==='decade'||key==='year'?'掲載年未確認':key==='producer'?'制作名義未登録':key==='sound'?'タグ未登録':'未登録';return key==='type'?(types[value]||value):key==='decade'?value+'年代':key==='year'?value+'年':value}
 function summary(records){const rows=unique(records),coverage=key=>rows.filter(t=>values(t,key)[0]!==missing).length;return{total:rows.length,types:aggregate(rows,'type'),yearsKnown:coverage('year'),producerKnown:coverage('producer'),soundKnown:coverage('sound'),decades:aggregate(rows,'decade')}}
 const api={missing,keys,dimensions,types,values,unique,parse,serialize,filter,aggregate,label,summary};root.CrateExplorer=api;if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(typeof window!=='undefined'?window:globalThis);
