"""Render the authored client About and current release history into static HTML."""
import json,subprocess
from catalog import work_count

def about_html(root, tracks):
    source=(root/'src/app/editorial.js').read_text()
    functions=source[source.index(' function about()'):source.index(' const editorProfileHTML')]
    release=(root/'releases.json').read_text()
    js='const view={};const window={CRATE_RELEASE:'+release+'};const songs=[];function top(){return ""}function esc(s){return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/\\"/g,"&quot;")}function workCount(){return '+json.dumps(work_count(tracks))+'}'+functions+';about();process.stdout.write(view.innerHTML+releaseHistory())'
    return subprocess.check_output(['node'],input=js,text=True)
