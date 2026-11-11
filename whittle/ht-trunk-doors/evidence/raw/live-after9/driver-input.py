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
A=RAW/(sys.argv[1] if len(sys.argv)>1 else 'live-attempt1')
A.mkdir(exist_ok=False)
import shutil
shutil.copyfile(__file__,A/'driver-input.py')
ENV=dict(os.environ)
for name in ['RM_HOST_GUARD_GEN','RM_DRIVER_PID']:
    ENV.pop(name,None)
SEAT='CODEX_STEVEDESKTOP_HUGETHINGS'
PURPOSE='HT: RIMMANDRAKE_ALLOW_HUGETHINGS_TRUNKS_TO_SEAL_DOORS'
TIER='mods__mandrake_rm_flowworks__mandrake_rm_hugethingstestraces__mandrake_rm_patches__mandrake_rm_biomes__oskarpotocki_vanillafactionsexpanded_core'
GAME=['bash','/home/mandrake/rm/runner/infrastructure/stevedesktop/rw_game.sh']
BRIDGE=['python3','src/RimMandrake/rimflow/cli.py','bridge']
BEFORE='before' in A.name
summary=dict(phase='before-fix' if BEFORE else 'after-fix',started_utc=datetime.now(timezone.utc).isoformat(),commands=[],ok=False)


def save():
    (A/'process-receipt.json').write_text(json.dumps(summary,indent=2)+'\n')


def run(name,args,required=True,timeout=900):
    prefix=('export RIMFLOW_SEAT='+SEAT+' AGENT_SEAT='+SEAT+' RIMFLOW_BRIDGE_SEAT='+SEAT+'\n'
            'source /home/mandrake/rm/runner/infrastructure/stevedesktop/testcentre_env.sh\n'
            'export RM_GUARD_SEAT='+SEAT+'\n'
            'export WSLENV="${WSLENV:+$WSLENV:}RIMFLOW_SEAT:AGENT_SEAT:RIMFLOW_BRIDGE_SEAT:RM_GUARD_SEAT:RM_HOST_GUARD_GEN:RM_DRIVER_PID"\n'
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
    bad=[r for r in report['rows'] if r['required'] and r['id']!='O02' and r['status']!='PASS']
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
    assert BEFORE or (ROOT/'whittle/ht-trunk-doors/SOURCE_COMMITTED.json').is_file(),'parent source commit absent'
    if not BEFORE:
        committed=json.loads((ROOT/'whittle/ht-trunk-doors/SOURCE_COMMITTED.json').read_text())
        script_path='src/RimMandrake/HugeThings/northstar/trunk_doors_live.py'
        script_commit=committed['script_sha']
        parent_bytes=subprocess.check_output(['git','show',script_commit+':'+script_path],cwd=ROOT)
        assert parent_bytes==(ROOT/script_path).read_bytes(),'current live script lacks exact parent commit'
        summary['parent_script_commit']=script_commit
        summary['parent_script_sha256']=hashlib.sha256(parent_bytes).hexdigest()
        save()
    assert not BEFORE or (E/'raw'/(A.name+'-source-freeze.json')).is_file(),'old source freeze absent'
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
    # Only the reviewed published dependency deltas may be applied.
    approved=json.loads((E.parent/'DEPENDENCY_APPROVED.json').read_text())
    assert len(approved['files'])==4
    for pair in approved['files']:
        assert hashlib.sha256((ROOT/pair['approved_source_path']).read_bytes()).hexdigest()==pair['approved_sha256']
        assert hashlib.sha256((ROOT/pair['backup']).read_bytes()).hexdigest()==pair['installed_sha256']
        assert hashlib.sha256(Path(pair['deployed_path']).read_bytes()).hexdigest() in (pair['installed_sha256'],pair['approved_sha256'])
    for report_path in approved['provenance']:
        report=json.loads((ROOT/report_path).read_text())
        for source in report.get('inputs',[]):
            assert hashlib.sha256((ROOT/source['path']).read_bytes()).hexdigest()==source['sha256']
    summary['dependency_authorization_sha256']=hashlib.sha256((E.parent/'DEPENDENCY_APPROVED.json').read_bytes()).hexdigest();save()
    flow_pairs=[pair for pair in approved['files'] if pair['package']=='FlowWorks']
    flow_current=all(hashlib.sha256(Path(pair['deployed_path']).read_bytes()).hexdigest()==pair['approved_sha256'] for pair in flow_pairs)
    if not flow_current:
        plan=run('flowworks-plan',['python3','src/RimMandrake/Utils/deploy_custom_mods.py','--mod','FlowWorks'],False)
        delta=re.findall(rb'^    [~+\-]  (.+)$',plan.stdout,re.M)
        assert set(delta)=={b'Assemblies/RimMandrakeFlowWorks.dll',b'Assemblies/RimMandrakeFlowWorks.dll.srchash'},delta
        run('flowworks-apply',['python3','src/RimMandrake/Utils/deploy_custom_mods.py','--mod','FlowWorks','--apply'])
    luminous=json.loads((E.parent/'LUMINOUS_DEPENDENCY_AUTHORIZATION.json').read_text())
    assert luminous['authorized'] is True
    for pair in luminous['files']:
        assert hashlib.sha256((ROOT/pair['approved_source_path']).read_bytes()).hexdigest()==pair['repo_sha256']
        assert hashlib.sha256(Path(pair['backup']).read_bytes()).hexdigest()==pair['installed_sha256']
        assert hashlib.sha256(Path(pair['source']).read_bytes()).hexdigest() in (pair['installed_sha256'],pair['repo_sha256'])
    report=json.loads((ROOT/luminous['report']).read_text())
    for source in report.get('inputs',[]):
        assert hashlib.sha256((ROOT/source['path']).read_bytes()).hexdigest()==source['sha256']
    lp=run('luminous-plan',['python3','src/RimMandrake/Utils/deploy_custom_mods.py','--mod','LuminousPigment'],False)
    delta=re.findall(rb'^    [~+\-]  (.+)$',lp.stdout,re.M)
    assert set(delta).issubset({b'Assemblies/RimMandrakeLuminousPigment.dll',b'Assemblies/RimMandrakeLuminousPigment.dll.srchash'}),delta
    if delta:run('luminous-apply',['python3','src/RimMandrake/Utils/deploy_custom_mods.py','--mod','LuminousPigment','--apply'])
    # Biomes includes the real Nogtyl plant. Its sole unrelated drift must have parent authority too.
    biomes_pairs=[pair for pair in approved['files'] if pair['package']=='Biomes']
    biomes_current=all(hashlib.sha256(Path(pair['deployed_path']).read_bytes()).hexdigest()==pair['approved_sha256'] for pair in biomes_pairs)
    if not biomes_current:
        bp=run('biomes-plan',['python3','src/RimMandrake/Utils/deploy_custom_mods.py','--compose','biomes'],False)
        delta=re.findall(rb'^    [~+\-]  (.+)$',bp.stdout,re.M)
        assert set(delta)=={b'Biomes/Cauldron/Assemblies/RimMandrake.Cauldron.dll',b'Biomes/Cauldron/Assemblies/RimMandrake.Cauldron.dll.srchash'},delta
        run('biomes-apply',['python3','src/RimMandrake/Utils/deploy_custom_mods.py','--compose','biomes','--apply'])
    if not BEFORE:
        hp=run('hugethings-plan',['python3','src/RimMandrake/Utils/deploy_custom_mods.py','--mod','HugeThings'],False)
        delta=re.findall(rb'^    [~+\-]  (.+)$',hp.stdout,re.M)
        assert set(delta).issubset({b'Assemblies/RM_HugeThings.dll',b'Assemblies/RM_HugeThings.dll.srchash',b'Defs/JobDefs/RM_JobDefs.xml',b'Defs/WorkGiverDefs/RM_WorkGivers.xml'}),delta
        if delta:run('hugethings-apply',['python3','src/RimMandrake/Utils/deploy_custom_mods.py','--mod','HugeThings','--apply'])
    if not BEFORE:
        tr=run('test-fixture-plan',['python3','src/RimMandrake/Utils/deploy_custom_mods.py','--mod','HugeThingsTestRaces'],False)
        delta=re.findall(rb'^    [~+\-]  (.+)$',tr.stdout,re.M)
        assert set(delta).issubset({b'Defs/ThingDefs_Plants/RM_TestContactPlant.xml'}),delta
        if delta:run('test-fixture-apply',['python3','src/RimMandrake/Utils/deploy_custom_mods.py','--mod','HugeThingsTestRaces','--apply'])
    run('deployment-bytes',['python3',str(E/'verify_deploy.py'),str(A/'deployment-bytes.json')])
    # Explicit parent-authorized boundary: default-game gate inspects the other host. Verify actual host, DOWN and paths first.
    latest=guard('guard-before-tier');assert latest['generation']==actual['generation'] and latest['seat']==SEAT
    down=run('status-before-tier',GAME+['status'],False);assert down.returncode==3 and b'stopped' in down.stdout
    sys.path.insert(0,str(ROOT/'src/RimMandrake/Utils'));import game_paths
    assert str(Path(game_paths.MODS_CONFIG)).startswith('/mnt/c/Users/sjlewis/'),game_paths.MODS_CONFIG
    assert str(Path(game_paths.LOCAL_MODS)).startswith('/mnt/d/SteamLibrary/'),game_paths.LOCAL_MODS
    (A/'tier-paths.json').write_text(json.dumps({'ModsConfig':game_paths.MODS_CONFIG,'LOCAL_MODS':game_paths.LOCAL_MODS,'RM_STEAMAPPS':ENV.get('RM_STEAMAPPS'),'host_generation':actual['generation']},indent=2)+'\n')
    run('tier-apply',['python3','src/RimMandrake/Utils/modset_builder.py','--tier',TIER,'--apply','--by',SEAT,'--not-my-bridge',
        'Parent-authorized default-host gate mismatch only: fresh CODEX_STEVEDESKTOP_HUGETHINGS own stevedesktop host_guard generation '+str(actual['generation'])+' and driver '+ENV['RM_DRIVER_PID']+' verified HELD, actual game DOWN and SteveDesktop paths independently verified; other-host O02 is N/A.'])
    run('sanitize-old-log',['python3',str(E/'sanitize_old_log.py'),str(A/'old-log-sanitization.json')])
    preflight('preflight-offline')
    real=run('powershell-path',['which','powershell.exe']).stdout.decode().strip()
    adapter=E/'steam_adapter'
    assert real!=str(adapter/'powershell.exe')
    ENV['HT_POWERSHELL_REAL']=real;ENV['PATH']=str(adapter)+os.pathsep+ENV['PATH']
    ENV['HT_STEAM_ADAPTER_RECEIPT']=str(A/'steam-route.jsonl')
    launch_start=time.time()
    launch=run('up',GAME+['up','--wait'],False,timeout=850)
    # rw_game's early process check is only five seconds. One Steam request gets
    # a separate 240-second creation budget, then 600 seconds for its fresh bridge.
    created=None
    while time.time()-launch_start<240:
        status=run('creation-status',GAME+['status'],False)
        if status.returncode==0 and b'running pid=' in status.stdout:
            created=time.time();break
        time.sleep(5)
    assert created is not None,'one Steam request produced no process within 240 seconds'
    initial_game_pid=re.search(rb'running pid=(\d+)',status.stdout).group(1)
    summary['game_pid']=initial_game_pid.decode();save()
    bridge_deadline=created+600
    while time.time()<bridge_deadline:
        status=run('bridge-status',GAME+['status'],False)
        if status.returncode==0 and b'bridge port in Player.log: 5174' in status.stdout:break
        time.sleep(5)
    else:raise RuntimeError('fresh process did not establish bridge within 600 seconds')
    time.sleep(45)
    routes=[json.loads(line) for line in (A/'steam-route.jsonl').read_text().splitlines()]
    assert len(routes)==1 and routes[0]['route']=='steam://rungameid/294100' and routes[0]['generation']==ENV['RM_HOST_GUARD_GEN']
    preflight('preflight-live',True);log('startup-log')
    current=guard('guard-live');assert current['generation']==actual['generation'] and current['identity']==actual['identity']
    script=ROOT/'src/RimMandrake/HugeThings/northstar/trunk_doors_live.py'
    win=lambda path:run('winpath-'+path.stem,['wslpath','-w',str(path)]).stdout.decode().strip()
    shutil.copyfile(script,A/'trunk-doors-input.py')
    script_sha=hashlib.sha256(script.read_bytes()).hexdigest()
    proof=run('trunk-doors',['python.exe',win(script),'--out',win(A/'trunk-doors.json')],False,timeout=1200)
    assert hashlib.sha256(script.read_bytes()).hexdigest()==script_sha,'proof script changed during execution'
    observed=json.loads((A/'trunk-doors.json').read_text())
    assert observed['restoration']['ok'],'restoration failed'
    if BEFORE:
        assert proof.returncode==1 and not observed['ok'] and observed.get('failure_stage')=='MOD_seal' and 'growth did not seal workshop doorway' in observed.get('error',''),observed.get('error')
        assert observed['sealed']['access'] is True and observed['sealed']['blockers']==[] and observed['geometry_control']['restored_access'] is True
        assert set(observed['doorway_claims'])=={'99,101','100,101'}
        summary['old_behavior_reproduced']=True
    else:
        assert proof.returncode==0 and observed['ok'],observed.get('error')
    end_status=run('status-proof-end',GAME+['status'])
    assert re.search(rb'running pid=(\d+)',end_status.stdout).group(1)==initial_game_pid,'game process changed'
    log('post-proof-log')
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
if summary['ok'] and not BEFORE:
    target=Path('/home/mandrake/codex-steve/ht-loop/evidence/trunk-doors.json');target.parent.mkdir(parents=True,exist_ok=True)
    assert not target.exists(),'accepted compact proof already exists; preserve it'
    target.write_text(json.dumps(observed,separators=(',',':'))+'\n')
    summary['live_copy']={'path':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
    save()
sys.exit(0 if summary['ok'] else 1)
