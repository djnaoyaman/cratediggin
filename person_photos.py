"""Provided portraits belong to an exact editorial identity, not production credits."""
import html

def photo_feature(features, name):
    for f in features:
        identities=[f['name'],*f.get('aliases',[])]
        if f['type']=='artist':identities+=f.get('names',[])
        if name in identities and f.get('visual',{}).get('precomposed'):return f
    return None

def photo_header(feature, base_path=''):
    v=(feature or {}).get('visual',{})
    if not v.get('precomposed'):return ''
    esc=lambda s:html.escape(str(s),quote=True)
    return '<figure class="person-photo-header" data-photo-person="'+esc(feature['id'])+'"><img class="person-photo" src="'+esc(base_path+'/'+v['photo'])+'" alt="'+esc(v['alt'])+'" decoding="async"><img class="person-photo-tag" src="'+esc(base_path+'/'+v['tag'])+'" alt="" aria-hidden="true" decoding="async"><figcaption>'+esc(v.get('credit','ユーザー提供'))+'</figcaption></figure>'
