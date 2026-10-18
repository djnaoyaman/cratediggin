const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const core=fs.readFileSync('src/app/core.js','utf8'),helpers=core.slice(0,core.indexOf(' const songs=')),ctx={};vm.runInNewContext(helpers+';globalThis.label=youtubeLinkLabel;globalThis.count=workCount;globalThis.unit=workUnit;',ctx);
assert.equal(ctx.label({youtube:{official:true}}),'公式YouTubeで開く ↗');
assert.equal(ctx.label({youtube:{official:false}}),'YouTubeの参考投稿で開く ↗');
assert.equal(ctx.label({youtube:{}}),'YouTubeで開く ↗');
assert.equal(ctx.count([{}, {workType:'mix'}]),'1曲・1ミックス作品');assert.equal(ctx.unit([{}]),'曲');assert.equal(ctx.unit([{workType:'mix'}]),'作品');
console.log('Official, third-party and unknown YouTube labels and separate song/mix counts passed');
