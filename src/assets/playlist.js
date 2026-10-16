'use strict';
window.CratePlaylist=(tracks,storage)=>{
 const valid=new Set(tracks.map(s=>s.id)),key='crate-my-playlist';let state={name:'MY CRATE',ids:[]};
 try{const saved=JSON.parse(storage.getItem(key)||'null');if(saved&&Array.isArray(saved.ids))state={name:String(saved.name||'MY CRATE').slice(0,40),ids:[...new Set(saved.ids.filter(id=>valid.has(id)))]}}catch(_){}
 const save=()=>{try{storage.setItem(key,JSON.stringify(state));return true}catch(_){return false}};
 return {get name(){return state.name},get ids(){return state.ids.slice()},has:id=>state.ids.includes(id),rename:name=>{state.name=String(name).trim().slice(0,40)||'MY CRATE';return save()},add:id=>{if(!valid.has(id))return false;if(!state.ids.includes(id))state.ids.push(id);return save()},remove:id=>{const index=state.ids.indexOf(id);if(index<0)return null;state.ids.splice(index,1);return {id,index,saved:save()}},restore:item=>{if(!item||!valid.has(item.id))return false;if(!state.ids.includes(item.id))state.ids.splice(Math.max(0,Math.min(item.index,state.ids.length)),0,item.id);return save()},move:(id,delta)=>{const index=state.ids.indexOf(id),next=index+delta;if(index<0||next<0||next>=state.ids.length)return false;[state.ids[index],state.ids[next]]=[state.ids[next],state.ids[index]];return save()}};
};
