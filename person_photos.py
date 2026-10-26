"""Provided portraits belong to an exact editorial identity, not production credits."""
import html

def photo_feature(features, name):
    for f in features:
        identities=[f['name'],*f.get('aliases',[])]
        if f['type']=='artist':identities+=f.get('names',[])
        if name in identities and (f.get('visual',{}).get('precomposed') or f.get('visual',{}).get('nameOnly')):return f
    return None

def photo_header(feature, base_path=''):
    v=(feature or {}).get('visual',{})
    esc=lambda s:html.escape(str(s),quote=True)
    if v.get('nameOnly'):
        return '<figure class="person-tag-header" data-tag-person="'+esc(feature['id'])+'"><img src="'+esc(base_path+'/'+v['tag'])+'" alt="'+esc(v['alt'])+'" decoding="async"><figcaption>Original graffiti · Designed by DJ Naoyaman</figcaption></figure>'
    if not v.get('precomposed'):return ''
    return '<figure class="person-photo-header" data-photo-person="'+esc(feature['id'])+'"><img class="person-photo" src="'+esc(base_path+'/'+v['photo'])+'" alt="'+esc(v['alt'])+'" decoding="async"><img class="person-photo-tag" src="'+esc(base_path+'/'+v['tag'])+'" alt="" aria-hidden="true" decoding="async"><figcaption>'+esc(v.get('credit','ユーザー提供'))+'</figcaption></figure>'
