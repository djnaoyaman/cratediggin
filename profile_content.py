"""Render the owner's supplied public biography with escaped text and supplied public links."""
import html,json,re

def inline(text):
    result=[];start=0
    for m in re.finditer(r'\[([^\]]+)\]\((https://[^\s)]+)\)',text):
        result.append(html.escape(text[start:m.start()]))
        result.append('<a href="'+html.escape(m[2],quote=True)+'" target="_blank" rel="noopener noreferrer">'+html.escape(m[1])+'</a>');start=m.end()
    result.append(html.escape(text[start:]));return ''.join(result)

def profile_photo(base_path, kind):
    name, width, height, alt = (("editor-provided-collage.webp",1456,816,"DJ NaoyamanのDJパフォーマンス・コラージュ（ユーザー提供）") if kind=="hero" else ("editor-provided-event.jpg",2048,1365,"DJ Naoyamanのイベント写真（ユーザー提供）"))
    return '<figure class="editor-photo editor-photo--'+kind+'"><img src="'+base_path+'/'+name+'" width="'+str(width)+'" height="'+str(height)+'" alt="'+alt+'" loading="lazy"><figcaption>ユーザー提供</figcaption></figure>'

def render_profile(root,base_path):
    data=json.loads((root/'editor_profile.json').read_text(encoding='utf-8'))
    out=['<article class="editor-profile"><header class="editor-profile-heading"><h1><span class="editor-name-accessible">'+html.escape(data['name'])+'</span><img class="editor-signature" src="'+base_path+'/'+data['signature']+'" alt="" width="1881" height="628"></h1><p class="editor-real-name">'+html.escape(data['realName'])+'</p></header>',profile_photo(base_path,"hero"),'<div class="prose">'];in_list=False
    for block in data['blocks']:
        kind=block['type'];text=block['text']
        if kind=='h2' and text=='約5万曲のクレートから':out.append(profile_photo(base_path,'event'))
        if kind=='h2' and text=='ブランドと地域の仕事':out.append("<h3>制作しているWebサイト</h3><ul><li><a href=\"https://djnaoyaman.github.io/ppp/\" onclick=\"if(location.hostname==='djnaoyaman.github.io'&amp;&amp;typeof window.gtag==='function'){try{window.gtag('event','creator_site_visit',{send_to:'G-71ENPHWEJH',target_site:'ppp',page_location:location.origin+location.pathname,page_referrer:document.referrer.split(/[?#]/)[0],transport_type:'beacon'});}catch(_){}}\" data-creator-site=\"ppp\" target=\"_blank\" rel=\"noopener noreferrer\">掌蹠膿疱症.com</a>：個人の体験と公開資料をもとに、掌蹠膿疱症の症状や治療の選択肢を整理する情報サイトです。</li><li><a href=\"https://djnaoyaman.github.io/youkai/\" onclick=\"if(location.hostname==='djnaoyaman.github.io'&amp;&amp;typeof window.gtag==='function'){try{window.gtag('event','creator_site_visit',{send_to:'G-71ENPHWEJH',target_site:'youkai',page_location:location.origin+location.pathname,page_referrer:document.referrer.split(/[?#]/)[0],transport_type:'beacon'});}catch(_){}}\" data-creator-site=\"youkai\" target=\"_blank\" rel=\"noopener noreferrer\">一見坊の【日本妖怪学体系】</a>：日本各地の妖怪と伝承を、出典・信頼度・地域のつながりから読み解く妖怪図鑑です。</li><li><a href=\"https://djnaoyaman.github.io/sakanamushi/\" onclick=\"if(location.hostname==='djnaoyaman.github.io'&amp;&amp;typeof window.gtag==='function'){try{window.gtag('event','creator_site_visit',{send_to:'G-71ENPHWEJH',target_site:'sakanamushi',page_location:location.origin+location.pathname,page_referrer:document.referrer.split(/[?#]/)[0],transport_type:'beacon'});}catch(_){}}\" data-creator-site=\"sakanamushi\" target=\"_blank\" rel=\"noopener noreferrer\">花鳥風月、そして魚と虫。</a>：魚・虫・鳥・植物にまつわる漢字を、大きな文字と読み方クイズで楽しむ図鑑です。</li><li><a href=\"https://djnaoyaman.github.io/kuranpo/\" onclick=\"if(location.hostname==='djnaoyaman.github.io'&amp;&amp;typeof window.gtag==='function'){try{window.gtag('event','creator_site_visit',{send_to:'G-71ENPHWEJH',target_site:'kuranpo',page_location:location.origin+location.pathname,page_referrer:document.referrer.split(/[?#]/)[0],transport_type:'beacon'});}catch(_){}}\" data-creator-site=\"kuranpo\" target=\"_blank\" rel=\"noopener noreferrer\">鎌・くらんぽ</a>：鎌倉の社寺と歴史を、出発点から解散点までの散歩コースで案内する街歩きガイドです。</li><li><a href=\"https://djnaoyaman.github.io/chems/\" onclick=\"if(location.hostname==='djnaoyaman.github.io'&amp;&amp;typeof window.gtag==='function'){try{window.gtag('event','creator_site_visit',{send_to:'G-71ENPHWEJH',target_site:'chems',page_location:location.origin+location.pathname,page_referrer:document.referrer.split(/[?#]/)[0],transport_type:'beacon'});}catch(_){}}\" data-creator-site=\"chems\" target=\"_blank\" rel=\"noopener noreferrer\">my Chems</a>：The Chemical Brothersの作品・人物・歴史を、出典つきの記録と私見でたどる日英の非公式アーカイブです。</li><li><a href=\"https://djnaoyaman.github.io/suburbia-classica/\" onclick=\"if(location.hostname==='djnaoyaman.github.io'&amp;&amp;typeof window.gtag==='function'){try{window.gtag('event','creator_site_visit',{send_to:'G-71ENPHWEJH',target_site:'suburbia-classica',page_location:location.origin+location.pathname,page_referrer:document.referrer.split(/[?#]/)[0],transport_type:'beacon'});}catch(_){}}\" data-creator-site=\"suburbia-classica\" target=\"_blank\" rel=\"noopener noreferrer\">SUBURBIA CLASSICA</a>：クラシックの名曲を、制作背景・構成・録音エピソードとともに聴く音楽ガイドです。</li><li><a href=\"https://djnaoyaman.github.io/sanreikotaiyoku/\" onclick=\"if(location.hostname==='djnaoyaman.github.io'&amp;&amp;typeof window.gtag==='function'){try{window.gtag('event','creator_site_visit',{send_to:'G-71ENPHWEJH',target_site:'sanreikotaiyoku',page_location:location.origin+location.pathname,page_referrer:document.referrer.split(/[?#]/)[0],transport_type:'beacon'});}catch(_){}}\" data-creator-site=\"sanreikotaiyoku\" target=\"_blank\" rel=\"noopener noreferrer\">酸冷交代浴のススメ</a>：炭酸泉と水風呂の楽しみ方を、体験・施設情報・文献から編集する入浴ガイドです。</li><li><a href=\"https://djnaoyaman.github.io/gooooooooood_expression/\" onclick=\"if(location.hostname==='djnaoyaman.github.io'&amp;&amp;typeof window.gtag==='function'){try{window.gtag('event','creator_site_visit',{send_to:'G-71ENPHWEJH',target_site:'gooooooooood_expression',page_location:location.origin+location.pathname,page_referrer:document.referrer.split(/[?#]/)[0],transport_type:'beacon'});}catch(_){}}\" data-creator-site=\"gooooooooood_expression\" target=\"_blank\" rel=\"noopener noreferrer\">gooooooooood* expression</a>：Webの動き・文字・音・インタラクションを、実例と解説から学び、試せる表現図鑑です。</li><li><a href=\"https://djnaoyaman.github.io/bookkeeping/\" onclick=\"if(location.hostname==='djnaoyaman.github.io'&amp;&amp;typeof window.gtag==='function'){try{window.gtag('event','creator_site_visit',{send_to:'G-71ENPHWEJH',target_site:'bookkeeping',page_location:location.origin+location.pathname,page_referrer:document.referrer.split(/[?#]/)[0],transport_type:'beacon'});}catch(_){}}\" data-creator-site=\"bookkeeping\" target=\"_blank\" rel=\"noopener noreferrer\">Book Keeping</a>：日商簿記・全経簿記・USCPAの仕訳や計算を反復演習し、学習記録と復習につなげる学習サイトです。</li></ul>")
        if kind=='h1':continue
        assert kind in ('h2','h3','p','li')
        if kind=='li' and not in_list:out.append('<ul>');in_list=True
        if kind!='li' and in_list:out.append('</ul>');in_list=False
        out.append('<'+kind+'>'+inline(text)+'</'+kind+'>')
    if in_list:out.append('</ul>')
    out.append('</div></article>');return ''.join(out)


EDITOR_NOTE_REPLACEMENTS = [['少しばかりよくできすぎている。', '少しばかりよくできすぎています。'], ['好きな曲を掘る。元になった音をたどる。街や仲間の話に寄り道する。', '好きな曲を掘ります。元になった音をたどります。街や仲間の話に寄り道します。'], ['そうして、いまの自分の耳を、もう一度確かめる。', 'そうして、いまの自分の耳を、もう一度確かめます。']]

def polite_editor_note(content):
    """Change only the shared note within an EDITOR static page."""
    def convert(match):
        text=match[0]
        for before,after in EDITOR_NOTE_REPLACEMENTS:
            text=text.replace(before,after)
        return text
    return re.sub(r'<section class="manifesto">.*?</section>',convert,content,count=1,flags=re.S)
