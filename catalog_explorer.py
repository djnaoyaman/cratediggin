"""Version-aware catalog counts, not market statistics or inferred geography."""
from collections import Counter
from html import escape
MISSING='__missing__'
DIMENSIONS=[('decade','年代'),('region','登録された地域'),('artist','アーティスト名義'),('producer','制作クレジット'),('category','掲載カテゴリ'),('sound','音のタグ')]
TYPES={'single':'楽曲','mix':'ミックス作品','live_video':'ライブ映像','album':'アルバム'}
def unique(records):
    seen=set();out=[]
    for t in records:
        if isinstance(t.get('id'),str) and t['id'] not in seen:seen.add(t['id']);out.append(t)
    return out
def values(t,key):
    if key=='type':return [t.get('workType','single')]
    if key in {'year','decade'}:
        y=t.get('year');return [str(y if key=='year' else y//10*10) if type(y) is int else MISSING]
    if key in {'producer','sound'}:
        v=t.get('producers' if key=='producer' else 'sounds',[])
        return list(dict.fromkeys(x for x in v if isinstance(x,str) and x.strip())) or [MISSING]
    v=t.get(key);return [v if isinstance(v,str) and v.strip() else MISSING]
def aggregate(records,key):
    c=Counter(v for t in unique(records) for v in values(t,key));return dict(c)
def summary(records):
    rows=unique(records)
    return {'total':len(rows),'types':aggregate(rows,'type'),'yearsKnown':sum(values(t,'year')[0]!=MISSING for t in rows),'producerKnown':sum(values(t,'producer')[0]!=MISSING for t in rows),'soundKnown':sum(values(t,'sound')[0]!=MISSING for t in rows),'decades':aggregate(rows,'decade')}
def label(key,v):
    if v==MISSING:return '掲載年未確認' if key in {'decade','year'} else '制作名義未登録' if key=='producer' else 'タグ未登録' if key=='sound' else '未登録'
    return v+'年代' if key=='decade' else v

def render_summary(records):
    records=unique(records);s=summary(records);n=s['total'];charts=[]
    for key,title in DIMENSIONS:
        counts=aggregate(records,key)
        rows=sorted(counts.items(),key=lambda x:(x[0]==MISSING,int(x[0]) if key=='decade' and x[0]!=MISSING else -x[1],x[0]))
        missing_rows=[r for r in rows if r[0]==MISSING];known_rows=[r for r in rows if r[0]!=MISSING]
        shown=known_rows[:8]+missing_rows;rest=known_rows[8:]
        def row(item):
            value,count=item;pct=round(count/n*100,1) if n else 0
            return '<div class="ce-bar" style="--ce-fill:'+str(pct)+'%"><span>'+escape(label(key,value))+'</span><b>'+str(count)+'作品</b></div>'
        note=''
        if key in {'producer','sound'}:
            known=s['producerKnown' if key=='producer' else 'soundKnown'];note='<p class="ce-note">登録あり '+str(known)+' / '+str(n)+'作品。複数の名義・タグは重複集計します。</p>'
        charts.append('<section class="ce-chart"><h3>'+title+'</h3>'+note+'<div class="ce-bars">'+''.join(map(row,shown))+'</div>'+('<details><summary>ほか'+str(len(rest))+'項目</summary>'+''.join(map(row,rest))+'</details>' if rest else '')+'</section>')
    return '<section class="ce-static" aria-label="収録作品の構成"><h2>収録作品を、いくつもの角度から。</h2><p>'+str(n)+'掲載作品：'+'・'.join(v+str(s['types'].get(k,0)) for k,v in TYPES.items())+'</p><p>このサイトの収録構成です。掲載年は作品・収録版の基準年で、初出年とは限りません。地域は活動文脈の登録表記で、録音地・出身地ではありません。</p><noscript><p>JavaScriptを無効にしているため、全掲載作品の集計を表示しています。条件を掛け合わせる操作はJavaScriptが必要です。下の年表から全作品へ進めます。</p></noscript><div class="ce-grid">'+''.join(charts)+'</div></section>'
