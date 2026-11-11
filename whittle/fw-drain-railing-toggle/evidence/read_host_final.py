"""Read Windows process table and actual shared lock file without rewriting project state caches."""
from pathlib import Path
import subprocess,csv,io,json,time,os
h=Path(__file__).resolve().parent;root=h.parents[2]
cmd=['tasklist.exe','/FI','IMAGENAME eq RimWorldWin64.exe','/FO','CSV','/NH']
p=subprocess.run(cmd,capture_output=True,timeout=30);assert p.returncode==0,p.stderr
(h/'latest_tasklist_stdout.txt').write_bytes(p.stdout);(h/'latest_tasklist_stderr.txt').write_bytes(p.stderr)
rows=list(csv.reader(io.StringIO(p.stdout.decode(errors='replace'))));game=[r for r in rows if r and r[0].lower()=='rimworldwin64.exe']
lock=Path('/mnt/d/ClaudeWork/rimmandrake/scratch/DRIVER_LOCK.json')
assert not os.environ.get('RIMFLOW_DRIVER_LOCK'),'unexpected lock override: inspect actual lock selection'
bridge=(root/'infrastructure/state/BRIDGE').read_text();free=[r for r in bridge.splitlines() if r.startswith('FREE')]
r=dict(time=time.time(),command=cmd,returncode=p.returncode,process_rows=rows,matching_game_processes=game,game='NOT RUNNING' if not game else 'RUNNING',shared_driver_lock_path=str(lock),shared_driver_lock_exists=lock.exists(),bridge_mirror=bridge,recorded_down_receipt='game_down_stdout.txt',purpose='Fresh direct read only; no game/bridge mutation or project-state cache write')
(h/'latest_host_readback.json').write_text(json.dumps(r,indent=2)+'\n');assert not game and not lock.exists() and len(free)==1,r
print('MEASURED NOT RUNNING; shared host driver lock absent/FREE; bridge record FREE; prior DOWN stamp retained')
