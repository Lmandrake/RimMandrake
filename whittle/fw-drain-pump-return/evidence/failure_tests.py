"""Execute the actual outer wrappers offline with injected bridge/process failures; never attach or overwrite live receipts."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import types
from unittest.mock import patch

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]

def executable(path,out):
    tree=ast.parse(path.read_text())
    for node in tree.body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='OUT' for t in node.targets):
            node.value=ast.Call(func=ast.Name(id='Path',ctx=ast.Load()),args=[ast.Constant(str(out))],keywords=[])
    return compile(ast.fix_missing_locations(tree),str(path),'exec')


def scene_failure(tmp,failed_reload):
    fw='RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings';hose='RimMandrake.FlowWorks.Hose.RM_HoseSettings'
    initial={(fw,'depthEngineEnabled'):'True',(fw,'depthEngineLiveForTests'):'False',(fw,'liquidPumpEnabled'):'False',(hose,'tankModesEnabled'):'False'}
    values=dict(initial);debug={'enableStoryteller':True};difficulty={'threatScale':1,'allowBigThreats':True};events=[]
    class S:
        def __init__(self,**kw):pass
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def call(self,tool,**kw):
            events.append((tool,kw))
            if tool=='jawa/mod_settings_field':
                k=(kw['typeName'],kw['field'])
                if kw['action']=='set':values[k]=kw['value']
                return {'success':True,'value':values[k]}
            if tool=='jawa/debug_settings':
                if kw['action']=='set':debug[kw['field']]=kw['value']
                return {'success':True,'fields':[{'name':k,'value':v} for k,v in debug.items()]}
            if tool=='jawa/difficulty_tune':
                before=dict(difficulty);difficulty.update(kw)
                return {'success':True,'before':before,'after':dict(difficulty)}
            if tool=='jawa/map_info':return {'sizeX':250,'sizeZ':250}
            if tool=='jawa/static_call':return {'result':'RECT sha256=fixture beds=0'}
            if tool=='rimworld/list_colonists':return {'colonists':[1,2,3]}
            if tool=='jawa/type_probe':return {'mvidMatchesFile':True,'assemblyFileSha256':hashlib.sha256((ROOT/'src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll').read_bytes()).hexdigest()}
            raise AssertionError(tool)
    saves=tmp/'saves';saves.mkdir()
    for n in ['CANONICAL_ASHKARR_START_2026-09-12.rws','ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws']:(saves/n).write_bytes(b'fixture canonical')
    loads=[]
    def load(*a,**kw):
        loads.append(kw);return {'verified':not(failed_reload and len(loads)==3)}
    T=types.ModuleType('test_site_saves');T.saves_stat=lambda *a:{'prior.rws':(12,1)};T.backup_saves=lambda *a:1;T.save_site=lambda *a:{'path':'fixture.rws'};T.load_site=load
    reg=types.ModuleType('settings_registry');reg.ROWS=[{'cls':k[0],'field':k[1]} for k in initial]
    session=types.ModuleType('rimdrive');session.Session=S
    gp=types.ModuleType('game_paths');gp.SAVES=str(saves)
    extension=types.ModuleType('extension_proof');extension.EXT=types.SimpleNamespace(S_FW=fw)
    (tmp/'result.json').write_bytes((HERE/'result.json').read_bytes())
    def fail_runner(*a,**kw):
        values[(fw,'liquidPumpEnabled')]='False';debug['enableStoryteller']=False;difficulty['threatScale']=0
        return types.SimpleNamespace(returncode=1)
    modules={'test_site_saves':T,'settings_registry':reg,'rimdrive':session,'game_paths':gp,'extension_proof':extension}
    with patch.dict(sys.modules,modules),patch.object(subprocess,'run',side_effect=fail_runner):
        try:exec(executable(HERE/'run_scene.py',tmp),{'__file__':str(HERE/'run_scene.py')})
        except SystemExit as e:assert e.code==1
    r=json.loads((tmp/'scene.json').read_text())
    assert r['status']=='FAIL' and r['runner_returncode']==1
    assert values==initial and debug=={'enableStoryteller':True} and difficulty=={'threatScale':1,'allowBigThreats':True}
    assert len(loads)==3 and r['canonical_before']==r['canonical_after']
    assert r['restore']['status']==('FAIL' if failed_reload else 'PASS')
    return {'case':'reload_failure' if failed_reload else 'runner_nonpass','status':r['status'],'restore':r['restore'],'loads':len(loads)}


def cleanup_failure(tmp):
    commands=[]
    def run(cmd,**kw):
        commands.append(cmd)
        if cmd[-2:]==['bridge','who']:
            kw['stdout'].write('driver lock: FREE\nbridge FREE\n')
        return types.SimpleNamespace(returncode=1 if '--live' in cmd else 0)
    with patch.object(subprocess,'run',side_effect=run),patch.object(subprocess,'check_output',side_effect=lambda cmd,**kw:cmd[-1]+'\n'):
        try:exec(executable(HERE/'drive.py',tmp),{'__file__':str(HERE/'drive.py')})
        except SystemExit as e:assert e.code==1
    r=json.loads((tmp/'drive.json').read_text())
    assert r['status']=='FAIL' and not r['cleanup_errors'] and r['bridge_and_lock_free']
    assert [p['name'] for p in r['processes']][-4:]==['stop-after','stamp-down','bridge-release','bridge-free']
    return {'case':'preflight_nonpass_cleanup','commands':commands,'status':r['status'],'cleanup_errors':r['cleanup_errors'],'bridge_and_lock_free':r['bridge_and_lock_free']}

rows=[]
with tempfile.TemporaryDirectory() as d:
    for name,fn in [('runner',lambda p:scene_failure(p,False)),('reload',lambda p:scene_failure(p,True)),('cleanup',cleanup_failure)]:
        tmp=Path(d)/name;tmp.mkdir();rows.append(fn(tmp))
(HERE/'failure-cases.json').write_text(json.dumps(rows,indent=2))
print('PASS actual wrapper finally: runner failure, independent setting restore after reload failure, stop/stamp/release after preflight refusal')
