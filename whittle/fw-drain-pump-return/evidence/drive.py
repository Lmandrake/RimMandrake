"""WSL orchestration; Windows Python alone invokes bridge/game tools. Always stop/stamp/release."""
import hashlib,json,os,re,shutil,subprocess,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
PRIVATE=Path('/mnt/d/ClaudeWork/rimmandrake/codex_wsl/fw-drain/pump-private')
LOG=Path('/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log')
TIER='mods__mandrake_rm_flowworks__mandrake_rm_hugethings__mandrake_rm_patches'
os.environ['RIMFLOW_SEAT']='BENCH'
R={'started':time.time(),'status':'FAIL','processes':[]}
def win(p): return subprocess.check_output(['wslpath','-w',str(p)],text=True).strip()
def run(cmd,name,timeout=600):
    t=time.time()
    with (OUT/(name+'.stdout.log')).open('w') as so,(OUT/(name+'.stderr.log')).open('w') as se:
        p=subprocess.run(cmd,cwd=ROOT,stdout=so,stderr=se,timeout=timeout)
    r={'command':cmd,'name':name,'returncode':p.returncode,'started':t,'elapsed':time.time()-t};R['processes'].append(r);return p.returncode

def scan(name):
    dst=PRIVATE/('Player-'+name+'.log');shutil.copy2(LOG,dst)
    txt=dst.read_text(encoding='utf-8-sig',errors='replace')
    pats=['Exception','Config error','Could not resolve','Error in ','Error while','Failed to']
    hits=[line for line in txt.splitlines() if any(p in line for p in pats)]
    receipt={'private_path':str(dst),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'bytes':dst.stat().st_size,'patterns':pats,'hits':hits}
    (OUT/('log-scan-'+name+'.json')).write_text(json.dumps(receipt,indent=2))
    return receipt
try:
    run(['python3','src/RimMandrake/rimflow/cli.py','bridge','who'],'bridge-held',60)
    rc=run(['python.exe',win(ROOT/'src/RimMandrake/Utils/preflight_bridge.py'),'--tier','quicktest','--modset',TIER,'--deep','--live','--seat','BENCH','--json',win(OUT/'preflight-live.json')],'preflight-live',600)
    if rc: raise RuntimeError('live preflight refused: '+str(rc))
    sc=scan('loaded')
    if sc['hits']: raise RuntimeError('load/config diagnostics need investigation: '+str(sc['hits'][:5]))
    if run(['./game','--why','FW drain pump return: fresh live preflight GREEN','up'],'stamp-up',60): raise RuntimeError('stamp up failed')
    rc=run(['python.exe',win(OUT/'run_scene.py')],'scene',900)
    scan('after-scene')
    if rc: raise RuntimeError('scene nonpass '+str(rc))
    R['status']='PASS'
except BaseException as ex:
    R['error']=repr(ex);R['traceback']=traceback.format_exc()
finally:
    errors=[]
    for cmd,name in [
      (['python.exe',win(OUT/'lifecycle.py'),'stop'],'stop-after'),
      (['./game','--why','FW drain pump return: proof ended; supported stop','down'],'stamp-down'),
      (['python3','src/RimMandrake/rimflow/cli.py','bridge','release'],'bridge-release'),
      (['python3','src/RimMandrake/rimflow/cli.py','bridge','who'],'bridge-free')]:
        try:
            rc=run(cmd,name,180)
            if rc: errors.append(name+' returned '+str(rc))
        except BaseException as ex: errors.append(name+': '+repr(ex))
    R['cleanup_errors']=errors
    free=(OUT/'bridge-free.stdout.log').read_text() if (OUT/'bridge-free.stdout.log').is_file() else ''
    R['bridge_and_lock_free']='driver lock: FREE' in free and 'bridge FREE' in free
    if errors or not R['bridge_and_lock_free']: R['status']='FAIL'
    R['finished']=time.time();(OUT/'drive.json').write_text(json.dumps(R,indent=2));print(json.dumps(R,indent=2))
raise SystemExit(0 if R['status']=='PASS' else 1)
