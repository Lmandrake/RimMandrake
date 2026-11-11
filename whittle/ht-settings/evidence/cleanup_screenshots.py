"""Remove only game-folder full captures named by this proof's screenshot calls.
The native bridge leaves full-frame copies even when outputDirectory targets a
window-cropped artifact. Keep the raw cropped evidence; hash/delete owned copies.
"""
import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];E=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src/RimMandrake/Utils'));import game_paths
names={'baseline_native_settings','ht_settings_baseline_top'}
for p in E.rglob('*_live.json'):
 r=json.loads(p.read_text())
 for c in r.get('calls',[]):
  if c.get('tool')=='rimworld/take_screenshot':names.add(c['params']['fileName'])
folder=Path(game_paths.LOCALLOW)/'Screenshots';rows=[]
for name in sorted(names):
 assert '/' not in name and '\\' not in name
 p=folder/(name+'.png');r={'name':p.name,'owned_request':name,'existed':p.exists()}
 if p.exists():r.update(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size);p.unlink()
 r['absent_after']=not p.exists();rows.append(r)
(E/'owned_full_screenshots_cleanup.json').write_text(json.dumps({'folder':str(folder),'files':rows},indent=2)+'\n')
print('owned full screenshot copies removed:',sum(r['existed'] for r in rows))
