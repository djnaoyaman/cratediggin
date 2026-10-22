"""Data-only exemption: proof before convenience; no browser is treated as passed."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).parent))
import select_checks as S


def raw(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True).encode()


class SimpleContentTests(unittest.TestCase):
    def case(self, field='essayTitle', value='A precise discovery'):
        m=json.loads((Path(__file__).parent/'manifest.json').read_text())
        a={'id':'one','title':'Original Mix','artist':'Artist','year':1995,
           'essayTitle':'Old heading','deck':'Deck','context':'Context',
           'essay':['Verified paragraph'], 'listening':['Listening invitation'],
           'sources':[{'label':'Interview','url':'https://example.org/interview','kind':'interview'}],
           'essaySources':[[0]],'facts':[{'text':'Fact','sources':[0]}],
           'samples':[], 'youtube':{'id':'same'},'art':'same'}
        b=copy.deepcopy(a);b[field]=value
        other=copy.deepcopy(a);other['id']='two'
        old,new=raw([a,other]),raw([b,other])
        fixture='scripts/fixtures/unit-simple-content.json'
        static={'id':'unit-simple-static','argv':['python','scripts/unit_simple.py'],'env':{},'kind':'static','legacy':False,'requires_build':True,'label':'unit static'}
        browser={'id':'unit-simple-browser','argv':['node','scripts/unit_simple_browser.cjs'],'env':{},'kind':'browser','legacy':False,'requires_build':True,'label':'unit browser'}
        m['commands'] += [static,browser]
        m['groups']['unit_simple']=[static['id'],browser['id']]
        m['script_dependencies'][static['argv'][1]]=[fixture]
        m['scoped_content_changes']['tracks.json']=[{'before_sha256':hashlib.sha256(old).hexdigest(),'after_sha256':hashlib.sha256(new).hexdigest(),'groups':['unit_simple']}]
        f={'files':{'tracks.json':{'beforeSHA256':hashlib.sha256(old).hexdigest(),'afterSHA256':hashlib.sha256(new).hexdigest()}},'rows':[{'id':'one','before':a,'after':b,'allowedFields':[field]}]}
        before={'tracks.json':old,S.MANIFEST_PATH:raw(m),fixture:raw(f)}
        after={**before,'tracks.json':new}
        changes=[{'status':'M','old_path':'tracks.json','new_path':'tracks.json'}]
        return m,before,after,changes,fixture

    def plan(self,case,event='pull_request'):
        m,a,b,c,_=case
        return S.select_changes(m,c,a.get,b.get,event)

    def test_positive_all_three_events_preserve_all_nonbrowser_work(self):
        for event in S.EVENTS:
            with self.subTest(event=event):
                case=self.case()
                with patch.object(S,'simple_content_exemption',return_value=None):
                    full=self.plan(case,event)
                narrow=self.plan(case,event)
                self.assertTrue(full['browser_required']);self.assertFalse(narrow['browser_required'])
                self.assertEqual([x for x in full['selected'] if x['kind']=='static'],narrow['selected'])
                for key in ['build_required','syntax','python_compile','integrity_groups','source_drift_check','blockers','changes','classified']:
                    self.assertEqual(full[key],narrow[key],key)
                self.assertEqual(narrow['simple_content_exemption']['track_ids'],['one'])
                self.assertTrue(any('not executed, not a pass' in s['reason'] and 'data-only' in s['reason'] for s in narrow['skipped']))

    def test_each_allowed_field(self):
        values={'essayTitle':'New','deck':'New deck','context':'New context','essay':['New paragraph'],'listening':['New invitation'],'essaySources':[[]], 'sources':[{'label':'Updated','url':'https://example.org/new','kind':'interview'}]}
        for field,value in values.items():
            with self.subTest(field=field):self.assertIsNotNone(self.plan(self.case(field,value))['simple_content_exemption'])

    def test_sensitive_fields_never_exempt_even_exact_fixture(self):
        for field,value in {'title':'Changed version','artist':'Other','year':1996,'youtube':{'id':'different'},'art':'new','producer':['Someone'],'facts':[],'samples':[{'title':'New sample'}]}.items():
            with self.subTest(field=field):self.assertIsNone(self.plan(self.case(field,value))['simple_content_exemption'])

    def test_invalid_schemas_and_indices_never_exempt(self):
        cases=[('essayTitle',''),('essay',[7]),('listening',[]),('essaySources',[[True]]),('essaySources',[[1]]),('essaySources',[]),('sources',[]),('sources',[{'label':'X','url':'javascript:bad','kind':'x'}]),('sources',[{'label':'X','url':'https://ok.test/','kind':'x','extra':'x'}])]
        for field,value in cases:
            with self.subTest(field=field,value=value):self.assertIsNone(self.plan(self.case(field,value))['simple_content_exemption'])

    def test_no_readers_or_bad_json(self):
        m,a,b,c,f=self.case()
        self.assertIsNone(S.simple_content_exemption(m,c,None,None))
        for bad in [b'[]',b'not JSON',b'[{"id":"a","id":"b"}]',b'{}']:
            q=dict(b);q['tracks.json']=bad
            self.assertIsNone(S.simple_content_exemption(m,c,a.get,q.get))

    def test_reordered_added_deleted_duplicate_or_no_actual_change(self):
        m,a,b,c,f=self.case();items=json.loads(b['tracks.json'])
        for changed in [items[::-1],items[:1],items+[items[0]], [items[0],items[0]],json.loads(a['tracks.json'])]:
            q=dict(b);q['tracks.json']=raw(changed)
            self.assertIsNone(S.simple_content_exemption(m,c,a.get,q.get))

    def test_any_support_runtime_or_unknown_change_retains_browsers(self):
        for path in ['scripts/ci/select_checks.py','scripts/ci/manifest.json','scripts/fixtures/unit-simple-content.json','scripts/unit_simple.py','src/app/song-ui.js','src/assets/style.css','assets/new.png','unknown.txt','editorial_deepdives.json']:
            case=self.case();m,a,b,c,f=case;c.append({'status':'M','old_path':path,'new_path':path});b[path]=b'new content'
            self.assertIsNone(self.plan(case)['simple_content_exemption'],path)

    def test_nonmodify_rename_and_duplicate_diff(self):
        m,a,b,c,f=self.case()
        for status in ['A','D','R100','C100','T']:
            bad=[dict(c[0],status=status)]
            self.assertIsNone(S.simple_content_exemption(m,bad,a.get,b.get))
        self.assertIsNone(S.simple_content_exemption(m,c+c,a.get,b.get))

    def test_fixture_dependency_pin_rows_and_fields_are_required(self):
        for mode in ['missing','changed','hash','rows','fields','unlinked','manifest']:
            m,a,b,c,f=self.case()
            if mode=='missing':a.pop(f)
            elif mode=='changed':b[f]=b'{}'
            elif mode=='manifest':b[S.MANIFEST_PATH]+=b' '
            elif mode=='unlinked':m['script_dependencies']['scripts/unit_simple.py']=[]
            else:
                j=json.loads(a[f])
                if mode=='hash':j['files']['tracks.json']['afterSHA256']='0'*64
                if mode=='rows':j['rows'][0]['after']['essayTitle']='Not approved'
                if mode=='fields':j['rows'][0]['allowedFields'].append('youtube')
                a[f]=b[f]=raw(j)
            self.assertIsNone(S.simple_content_exemption(m,c,a.get,b.get),mode)

    def test_version_only_release_allowed_but_history_change_not(self):
        case=self.case();m,a,b,c,f=case
        old={'version':'22.137','history':[],'timezone':'UTC','policy':'same'}
        a['releases.json']=raw(old);b['releases.json']=raw(dict(old,version='22.138'))
        c.append({'status':'M','old_path':'releases.json','new_path':'releases.json'})
        self.assertIsNotNone(self.plan(case)['simple_content_exemption'])
        b['releases.json']=raw(dict(old,history=['new']))
        self.assertIsNone(self.plan(case)['simple_content_exemption'])

    def test_exact_fixture_cannot_hide_nonallowed_type_drift(self):
        for position in (0,1):
            for oldvalue,newvalue in [(1,True),(1,1.0),({'official':1},{'official':True})]:
                m,a,b,c,f=self.case();old=json.loads(a['tracks.json']);new=json.loads(b['tracks.json'])
                old[position]['addedOrder']=oldvalue;new[position]['addedOrder']=newvalue
                a['tracks.json']=raw(old);b['tracks.json']=raw(new)
                oh=hashlib.sha256(a['tracks.json']).hexdigest();nh=hashlib.sha256(b['tracks.json']).hexdigest()
                m['scoped_content_changes']['tracks.json'][0].update(before_sha256=oh,after_sha256=nh)
                q=json.loads(a[f]);q['files']['tracks.json'].update(beforeSHA256=oh,afterSHA256=nh)
                q['rows'][0].update(before=old[0],after=new[0])
                a[f]=b[f]=raw(q);a[S.MANIFEST_PATH]=b[S.MANIFEST_PATH]=raw(m)
                self.assertIsNone(S.simple_content_exemption(m,c,a.get,b.get),(position,oldvalue,newvalue))

    def test_fixture_rows_require_type_sensitive_equality(self):
        m,a,b,c,f=self.case();old=json.loads(a['tracks.json']);new=json.loads(b['tracks.json'])
        old[0]['addedOrder']=new[0]['addedOrder']=1
        a['tracks.json']=raw(old);b['tracks.json']=raw(new)
        oh=hashlib.sha256(a['tracks.json']).hexdigest();nh=hashlib.sha256(b['tracks.json']).hexdigest()
        m['scoped_content_changes']['tracks.json'][0].update(before_sha256=oh,after_sha256=nh)
        q=json.loads(a[f]);q['files']['tracks.json'].update(beforeSHA256=oh,afterSHA256=nh)
        q['rows'][0].update(before=old[0],after=new[0]);q['rows'][0]['before']['addedOrder']=True
        a[f]=b[f]=raw(q);a[S.MANIFEST_PATH]=b[S.MANIFEST_PATH]=raw(m)
        self.assertIsNone(S.simple_content_exemption(m,c,a.get,b.get))

    def test_release_nonversion_type_drift_never_exempt(self):
        for value in (True,1.0):
            m,a,b,c,f=self.case();old={'version':'22.137','history':[1],'timezone':'UTC','policy':'same'}
            a['releases.json']=raw(old);b['releases.json']=raw(dict(old,version='22.138',history=[value]))
            c.append({'status':'M','old_path':'releases.json','new_path':'releases.json'})
            self.assertIsNone(S.simple_content_exemption(m,c,a.get,b.get))

    def test_preexisting_blocker_cannot_be_masked(self):
        case=self.case();case[3].append({'status':'A','old_path':None,'new_path':'unknown'})
        p=self.plan(case);self.assertTrue(p['blockers']);self.assertIsNone(p['simple_content_exemption'])

if __name__=='__main__':unittest.main()
