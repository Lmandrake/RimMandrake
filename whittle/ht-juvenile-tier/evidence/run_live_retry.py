"""Native Codex-owned bounded Entry-state round. Always DOWN/release immediately; no build, ledger or publication."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import signal
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[3]
E=Path(__file__).resolve().parent
RAW=E/'raw'
A=RAW/(sys.argv[1] if len(sys.argv)>1 else 'live-attempt2')
A.mkdir(exist_ok=False)
ENV=dict(os.environ)
for name in ['RM_HOST_GUARD_GEN','RM_DRIVER_PID']:
    ENV.pop(name,None)
SEAT='CODEX_STEVEDESKTOP_HUGETHINGS'
PURPOSE='HT: RIMMANDRAKE_REVIEW_HUGETHINGS_JUVENILE_PASSAGE_CLASSIFICATION'
TIER='mods__mandrake_rm_flowworks__mandrake_rm_hugethings__mandrake_rm_patches__mandrake_rm_biomes__oskarpotocki_vanillafactionsexpanded_core'
GAME=['bash','/home/mandrake/rm/runner/infrastructure/stevedesktop/rw_game.sh']
BRIDGE=['python3','src/RimMandrake/rimflow/cli.py','bridge']
summary=dict(started_utc=datetime.now(timezone.utc).isoformat(),commands=[],ok=False)


def save():
    (A/'process-receipt.json').write_text(json.dumps(summary,indent=2)+'\n')


def run(name,args,required=True,timeout=900):
    prefix=('export RIMFLOW_SEAT='+SEAT+' AGENT_SEAT='+SEAT+' RIMFLOW_BRIDGE_SEAT='+SEAT+'\n'
            'source /home/mandrake/rm/runner/infrastructure/stevedesktop/testcentre_env.sh\n'
            'export WSLENV="${WSLENV:+$WSLENV:}RIMFLOW_SEAT:AGENT_SEAT:RIMFLOW_BRIDGE_SEAT:RM_HOST_GUARD_GEN:RM_DRIVER_PID"\n'
            'export RM_CODEX_SIDE=wsl\n')
    if (A/(name+'.stdout.txt')).exists():
        name+='-'+str(len(summary['commands']))
    started=time.time()
    p=subprocess.Popen(['bash','-c',prefix+shlex.join(args)],cwd=ROOT,env=ENV,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
    error=None
    try:out,err=p.communicate(timeout=timeout)
    except BaseException as exc:
        error=repr(exc);os.killpg(p.pid,signal.SIGTERM)
        try:out,err=p.communicate(timeout=10)
        except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);out,err=p.communicate()
    def safe(data):
        return b'\n'.join(b'[credential line redacted]' if re.search(rb'bridge token:|authorization:|bearer ',line,re.I) else line for line in data.split(b'\n'))
    for ext,data in [('stdout.txt',safe(out)),('stderr.txt',safe(err)),('rc',str(p.returncode).encode()+b'\n')]:
        (A/(name+'.'+ext)).write_bytes(data)
    summary['commands'].append(dict(name=name,args=args,rc=p.returncode,elapsed_seconds=time.time()-started,error=error))
    save();print(name,'rc',p.returncode,flush=True)
    if error:raise RuntimeError(name+' interrupted: '+error)
    if required and p.returncode:raise RuntimeError(name+' failed; inspect raw streams')
    return subprocess.CompletedProcess(args,p.returncode,out,err)


def guard(name):
    return json.loads(run(name,['python3','src/RimMandrake/rimflow/host_guard.py','status','--json']).stdout)


def preflight(name,live=False):
    path=A/(name+'.json')
    args=['/home/mandrake/.cache/ht-warning-venv/bin/python3','src/RimMandrake/Utils/preflight_bridge.py','--tier','quicktest','--modset',TIER,'--deep','--all','--seat',SEAT,'--json',str(path)]
    if live:args+=['--live']
    run(name,args,False)
    report=json.loads(path.read_text())
    bad=[r for r in report['rows'] if r['id']!='O02' and r['status']!='PASS' and (r['required'] or r['id']=='O10' or r['status']=='FAIL')]
    (A/(name+'-applicability.json')).write_text(json.dumps({'O02':'N/A other-host bridge row only; actual host lease proved separately','other_required_nonpasses':bad},indent=2)+'\n')
    assert not bad,[(r['id'],r['status'],r['reason']) for r in bad]


def log(name):
    sys.path.insert(0,str(ROOT/'src/RimMandrake/Utils'));import game_paths
    lines=Path(game_paths.PLAYER_LOG).read_text(errors='replace').splitlines()
    exceptions=[(i+1,s) for i,s in enumerate(lines) if re.search(r'Exception|Traceback',s)]
    configs=[(i+1,s) for i,s in enumerate(lines) if 'Config error' in s]
    parse=[(i+1,s) for i,s in enumerate(lines) if re.search(r'Error while loading|could not parse|exception parsing|XML error|Could not resolve cross.ref|Could not find type named',s,re.I)]
    selected={'first_exception':exceptions[0] if exceptions else None,'exception_count':len(exceptions),'config_errors':configs,'parse_errors':parse}
    # Never write full Player.log or endpoint credentials.
    assert not re.search(r'bridge token:|authorization:|bearer ',json.dumps(selected),re.I)
    (A/(name+'.json')).write_text(json.dumps(selected,indent=2)+'\n')
    assert not exceptions and not configs and not parse,'first Player.log cause needs investigation'


held=False
try:
    assert (ROOT/'whittle/ht-juvenile-tier/SOURCE_COMMITTED.json').is_file(),'parent source commit absent'
    before=guard('guard-before');assert before['state']=='FREE',before
    run('take',BRIDGE+['take','--host','stevedesktop','--idle-ok','--for',PURPOSE])
    held=True
    actual=guard('guard-taken')
    assert actual['state']=='HELD' and actual['host']=='stevedesktop' and actual['seat']==SEAT and actual['purpose']==PURPOSE,actual
    assert actual['generation']>before['generation'],actual
    ENV['RM_HOST_GUARD_GEN']=str(actual['generation']);ENV['RM_DRIVER_PID']=str(actual['identity']['pid'])
    summary['actual_fresh_driver']=actual;save()
    run('lease-before',BRIDGE+['who','--host','stevedesktop'])
    run('down-before-deploy',GAME+['down'])
    authority=json.loads((ROOT/'whittle/ht-juvenile-tier/DEPENDENCY_AUTHORIZATION.json').read_text())
    assert authority['authorized'] is True
    assert authority['allowed_delta']==[['~','Assemblies/RimMandrakeFlowWorks.dll'],['~','Assemblies/RimMandrakeFlowWorks.dll.srchash']]
    assert authority['expected_dll_sha256']=='a4b1acd85657946b4e66ab6b134d7ee7d7bc4ab09eb88038cc95c9c97766d6cb'
    sys.path.insert(0,str(ROOT/'src/RimMandrake/Utils'));import game_paths
    assert str(Path(game_paths.MODS_CONFIG)).startswith('/mnt/c/Users/sjlewis/'),game_paths.MODS_CONFIG
    assert str(Path(game_paths.LOCAL_MODS)).startswith('/mnt/d/SteamLibrary/'),game_paths.LOCAL_MODS
    run('dependency-before-check',['python3',str(E/'verify_dependency.py'),'before',str(A/'dependency-before.json')])
    run('dependency-apply',authority['command'])
    run('dependency-after-check',['python3',str(E/'verify_dependency.py'),'after',str(A/'dependency-after.json')])
    # Previous round already installed and selected these exact inputs; no repeat writes needed.
    run('deploy-byte-check',['python3',str(E/'verify_deploy.py'),str(A/'deployment-bytes.json')])
    preflight('preflight-offline')
    real=run('powershell-path',['which','powershell.exe']).stdout.decode().strip()
    adapter=E/'steam_adapter'
    assert real!=str(adapter/'powershell.exe')
    ENV['HT_POWERSHELL_REAL']=real;ENV['PATH']=str(adapter)+os.pathsep+ENV['PATH']
    ENV['HT_STEAM_ADAPTER_RECEIPT']=str(A/'steam-route.jsonl')
    launch=run('up',GAME+['up','--wait'],False)
    if launch.returncode:
        for index in range(12):
            time.sleep(5)
            result=run('delayed-status-'+str(index),GAME+['status'],False)
            if result.returncode==0 and b'bridge port in Player.log: 5174' in result.stdout:break
        else:raise RuntimeError('Steam launch did not establish process/bridge')
    time.sleep(45)
    routes=[json.loads(line) for line in (A/'steam-route.jsonl').read_text().splitlines()]
    assert len(routes)==1 and routes[0]['route']=='steam://rungameid/294100' and routes[0]['generation']==ENV['RM_HOST_GUARD_GEN']
    preflight('preflight-live',True);log('startup-log')
    current=guard('guard-live');assert current['generation']==actual['generation'] and current['identity']==actual['identity']
    script=ROOT/'src/RimMandrake/HugeThings/northstar/juvenile_tier_live.py'
    win=lambda path:run('winpath-'+path.stem,['wslpath','-w',str(path)]).stdout.decode().strip()
    run('entry-before',['python.exe',win(E/'observe_entry.py'),win(A/'entry-before.json')])
    run('loaded-method-probe',['python.exe',win(script),'--out',win(A/'loaded-methods.json'),'--juvenile-race','RM_ReefbackJuv','--adult-race','RM_Reefback'],timeout=600)
    run('entry-after',['python.exe',win(E/'observe_entry.py'),win(A/'entry-after.json')])
    assert json.loads((A/'entry-before.json').read_text())['ticksGame']==json.loads((A/'entry-after.json').read_text())['ticksGame']
    observed=json.loads((A/'loaded-methods.json').read_text());assert observed['ok'] and observed['restoration']['ok']
    log('post-probe-log')
    target=Path('/home/mandrake/codex-steve/ht-loop/evidence/juvenile-tier.json');target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(observed,separators=(',',':'))+'\n')
    summary['live_copy']={'path':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
    summary['ok']=True
except Exception as exc:
    summary['error']=str(exc);print('FAILED',exc,flush=True)
finally:
    if held:
        try:run('down-finally',GAME+['down'])
        except Exception as exc:summary['down_error']=str(exc);summary['ok']=False
        try:
            run('release',BRIDGE+['release','--host','stevedesktop'])
            run('lease-after',BRIDGE+['who','--host','stevedesktop'])
            after=guard('guard-after');assert after['state']=='FREE',after
            stopped=run('status-after',GAME+['status'],False);assert stopped.returncode==3 and b'stopped' in stopped.stdout
        except Exception as exc:summary['release_error']=str(exc);summary['ok']=False
    summary['finished_utc']=datetime.now(timezone.utc).isoformat();save()
sys.exit(0 if summary['ok'] else 1)
