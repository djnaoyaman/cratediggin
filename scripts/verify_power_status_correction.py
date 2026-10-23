from pathlib import Path
import argparse,json,hashlib,html,copy
from approved_power_status_correction import F,current_power_status_correction_file,historical_power_status_correction_file
R=Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest();read=lambda p:current_power_status_correction_file(p,(R/p).read_bytes())
p=argparse.ArgumentParser();p.add_argument('--source-only',action='store_true');a=p.parse_args()
for path,h in F['protected'].items():assert sha(read(path))==(F['generatedAuditSHA256']if path=='audit-reports/maintenance.json'else h),path
assert sha(read(F['previousHelper']['path']))==F['previousHelper']['afterSHA256']
for path,c in F['files'].items():
 raw=(R/path).read_bytes();assert sha(current_power_status_correction_file(path,raw))==c['afterSHA256'];assert sha(historical_power_status_correction_file(path,raw))==c['beforeSHA256']
 for mutated in [raw+b' ',raw[:-1]]:
  try:historical_power_status_correction_file(path,mutated)
  except AssertionError:pass
  else:raise AssertionError('Unapproved correction accepted '+path)
T=json.loads(read('tracks.json'));old=json.loads(historical_power_status_correction_file('tracks.json',(R/'tracks.json').read_bytes()));i=F['trackIndex'];t=T[i];before=old[i];assert len(T)==len(old)==566 and len({x['id']for x in T})==566;assert T[:i]+T[i+1:]==old[:i]+old[i+1:]and t==F['track']and before==F['beforeTrack']
assert t['id']=='rapsody-power'and t['youtube']==before['youtube']and t['youtube']['id']=='sVsehWDsoR0';assert all(t['youtube'][k]is False for k in ['playbackVerified','embeddedPlaybackVerified','japanPlaybackVerified','exactMasterVerified'])
notice='利用者の環境で再生確認済み（2026年10月24日）。環境により再生できない場合があります。';assert t['editorialStatus']==t['audioVerificationStatus']==t['editorSelectionMemory']['text']==notice
expected=copy.deepcopy(before);expected['editorialStatus']=expected['audioVerificationStatus']=notice;expected['editorSelectionMemory']['text']=notice;expected['sources'][2]['label']='Rapsody — アーティスト所在地（Bandcamp）';expected['sources'][2]['kind']='プロフィール地域情報';expected['userReportedPlayback']={'status':'reported_playable','reportedDate':'2026-10-24','timezone':'Asia/Tokyo','environment':'iOS','videoId':'sVsehWDsoR0','provenance':'利用者からの再生報告','agentObserved':False,'universalAvailabilityConfirmed':False};assert t==expected
assert t['essaySources']==before['essaySources']and [s['url']for s in t['sources']]==[s['url']for s in before['sources']];assert t['sources'][2]['url']=='https://rapsody.bandcamp.com/album/for-everything';assert sha(historical_power_status_correction_file('audit-reports/maintenance.json',(R/'audit-reports/maintenance.json').read_bytes()))==F['generatedAuditBeforeSHA256']
if not a.source_only:
 D=R/'dist';actual=json.loads((R/'tracks.json').read_text());generated=json.loads((D/'tracks.js').read_text().split('window.TRACKS = ',1)[1].strip().removesuffix(';'));assert [x['id']for x in generated]==[x['id']for x in actual];live=next(x for x in actual if x['id']==t['id']);g=next(x for x in generated if x['id']==t['id']);assert g['youtube']==live['youtube'];page=html.unescape((D/f'tracks/{t["id"]}.html').read_text());md=(D/f'songs/{t["id"]}.md').read_text()
 for v in [live['title'],live['artist'],live['editorSelectionMemory']['text'],live['sources'][2]['label'],live['sources'][2]['url'],live['youtube']['url']]:assert v in page and v in md,v
print('Power correction PASS: one exact row,565 unchanged,4 agent verification flags false,user report explicit,source index preserved,strict compact inverse/mutation rejection.')
