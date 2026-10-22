"""Narrow unresolved evidence notices, separate from audio and article completion."""
import json,html
LABEL='要調査'
CLOSING='この点は確認でき次第更新します。'
def load_notes(root,tracks):
 notes=json.loads((root/'article_research_notes.json').read_text(encoding='utf-8'))
 assert isinstance(notes,dict) and set(notes)<={t['id'] for t in tracks}
 for id,note in notes.items():
  assert isinstance(note,dict) and set(note)=={'missingEvidence'},id
  assert isinstance(note['missingEvidence'],str) and note['missingEvidence'].strip(),id
 return notes
def render_notice(track):
 n=track.get('articleResearch')
 if not n:return ''
 return '<aside class="article-research-note" aria-label="'+LABEL+'"><h2>'+LABEL+'</h2><p>'+html.escape(n['missingEvidence'])+'</p><p>'+CLOSING+'</p></aside>'
def markdown_notice(track):
 n=track.get('articleResearch')
 return '\n\n## '+LABEL+'\n\n'+n['missingEvidence']+'\n\n'+CLOSING if n else ''
