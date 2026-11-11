"""Execute all final offline processes after production/spec edits."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

root=Path(__file__).resolve().parents[3]
here=Path(__file__).resolve().parent
raw=here/'raw'
game='/mnt/d/SteamLibrary/steamapps/common/RimWorld'
def win(p):
    return subprocess.check_output(['wslpath','-w',str(p)],text=True).strip()
def run(name,cmd,timeout=180):
    p=subprocess.run([sys.executable,str(here/'run_process.py'),'--name',name,'--timeout',str(timeout),'--',*cmd],cwd=root)
    if p.returncode:
        raise SystemExit(p.returncode)
for f in ('read_engine.ps1','check_float.ps1','run_process.py'):
    shutil.copyfile(here/f,raw/f)
run('validator-final',[sys.executable,'skills/rimworld-modding/scripts/validate_patch.py',
    'src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Races/RM_SeaBeasts_Invented.xml'])
run('selftests-final',[sys.executable,'src/RimMandrake/Utils/run_selftests.py','--only','selftest_def_duplicate_fields'])
run('engine-final',['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',win(here/'read_engine.ps1'),
    '-GameDir',win(Path(game))],100)
run('float-final',['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',win(here/'check_float.ps1')],100)
run('measure-final',[sys.executable,'src/RimMandrake/HugeThings/northstar/measure_reefback_combat.py',
    '--game-dir',game,'--engine-il',str(raw/'engine-final.stdout.txt'),
    '--baseline-root',str(raw/'before'),'--out',str(raw/'final')])
paths=[
    'src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Races/RM_SeaBeasts_Invented.xml',
    'src/RimMandrake/HugeThings/northstar/measure_reefback_combat.py',
    'design/Jawa/worldbuilding/biomes/miasma_fauna_roster_2026-09-23.md',
    'design/RimMandrake/hugethings_codex_2026-11-09/REEFBACK_CALF_DECISION.md',
    'design/RimMandrake/hugethings_codex_2026-11-09/REEFBACK_NURSERY_COMBAT.md',
    'infrastructure/state/delegated/2026-11-11/RIMMANDRAKE_RECONCILE_HUGETHINGS_REEFBACK_NURSERY_COMBAT.json']
manifest=[]
for rel in paths:
    data=(root/rel).read_bytes()
    manifest.append({'file':rel,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
(raw/'changed-source-hashes.json').write_text(json.dumps(manifest,indent=2)+'\n')
# Source diffs admitted to the judge contain source/specs, never builder decisions.
p=subprocess.run(['git','diff','--',paths[0],paths[2]],cwd=root,capture_output=True)
(raw/'production-spec.diff').write_bytes(p.stdout)
(raw/'production-spec-diff.receipt.json').write_text(json.dumps({'command':p.args,'rc':p.returncode,
    'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr':p.stderr.decode()},indent=2)+'\n')
p=subprocess.run(['git','diff','--no-index','--','/dev/null',paths[1]],cwd=root,capture_output=True)
(raw/'instrument.diff').write_bytes(p.stdout)
(raw/'instrument-diff.receipt.json').write_text(json.dumps({'command':p.args,'rc':p.returncode,
    'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr':p.stderr.decode()},indent=2)+'\n')
# Full review diff stays outside the judge's source-only allowlist.
chunks=[]
for rel in paths:
    tracked=subprocess.run(['git','ls-files','--error-unmatch','--',rel],cwd=root,capture_output=True).returncode==0
    cmd=['git','diff','--',rel] if tracked else ['git','diff','--no-index','--','/dev/null',rel]
    p=subprocess.run(cmd,cwd=root,capture_output=True)
    chunks.append(p.stdout)
(here/'review.diff').write_bytes(b'\n'.join(chunks))
run('diff-check-final',['git','diff','--check','--',*paths])
