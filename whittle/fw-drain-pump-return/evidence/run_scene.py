"""Windows-only outer restoration wrapper; production extension runner executes unchanged."""
import hashlib,json,os,subprocess,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
for p in (ROOT/'src/RimMandrake/Utils',ROOT/'src/RimMandrake/Utils/modcheck',ROOT/'src/RimMandrake/FlowWorks/northstar'):
    sys.path.insert(0,str(p))
os.environ['RIMFLOW_SEAT']='BENCH'
os.environ.pop('RM_FOCUS_OPT_IN',None)
import test_site_saves as T
import settings_registry as REG
from rimdrive import Session
from game_paths import SAVES
import extension_proof as E
R={'started':time.time(),'calls':[],'restore':{'errors':[]},'status':'FAIL'}
name='WHITTLE_PumpReturn_Begin_'+time.strftime('%Y%m%dT%H%M%S')
prior=[]; debug={}; difficulty={}; baseline=None
saves_before=T.saves_stat(SAVES)
canonical={}

def persist():
    (OUT/'scene.json').write_text(json.dumps(R,indent=2,default=str),encoding='utf-8')
def need(ok,msg):
    if not ok: raise AssertionError(msg)

with Session(lock=None) as s:
    def call(tool,**kw):
        r=s.call(tool,**kw)
        R['calls'].append({'tool':tool,'args':kw,'result':r})
        need(isinstance(r,dict) and r.get('success') is not False, str((tool,kw,r)))
        return r
    def static(typ,field,value=None,write=False):
        kw=dict(typeName=typ,field=field,action='get')
        if write: kw.update(action='set',value=str(value))
        r=call('jawa/mod_settings_field',**kw)
        if not write: need('value' in r,'no value '+str(kw)); return r['value']
    def debug_read(): return {x['name']:x['value'] for x in call('jawa/debug_settings',action='list')['fields']}
    def rect():
        mi=call('jawa/map_info')
        arg='0,0,%s,%s'%(mi['sizeX'],mi['sizeZ'])
        r=call('jawa/static_call',type='RimMandrake.FlowWorks.RM_PitPrisonProof',method='Rect',args=arg)['result']
        need(str(r).startswith('RECT sha256='),'bad rect '+str(r)); return r
    def reload_baseline():
        r=T.load_site(call,'calm',name=name,check=False,map_controls=('modal_broker',))
        need(r['verified'],'baseline reload '+str(r)); return r
    try:
        for filename in ('CANONICAL_ASHKARR_START_2026-09-12.rws','ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws'):
            path=Path(SAVES)/filename
            need(path.is_file(),'canonical save unreadable '+filename)
            canonical[filename]=hashlib.sha256(path.read_bytes()).hexdigest()
        R['canonical_before']=canonical
        R['saves_before']=saves_before
        debug=debug_read(); R['debug_before']=debug
        for row in REG.ROWS:
            k=(row['cls'],row['field'])
            if not any((x['type'],x['field'])==k for x in prior):
                prior.append({'type':k[0],'field':k[1],'value':static(*k)})
        R['settings_before']=prior; persist()
        R['site']=T.load_site(call,'calm'); need(R['site']['verified'],'registered site failed')
        backup=Path('D:/ClaudeWork/rimmandrake/codex_wsl/fw-drain/pump-private')/('saves-before-'+name)
        R['saves_backup']={'directory':str(backup),'files':T.backup_saves(SAVES,str(backup))}
        R['snapshot']=T.save_site(call,name,SAVES)
        R['baseline_reload']=reload_baseline()
        baseline=rect(); R['baseline_rect']=baseline
        difficulty=call('jawa/difficulty_tune')['before']; R['difficulty_before']=difficulty
        cols=call('rimworld/list_colonists'); R['baseline_colonists']=cols
        need(len(cols.get('colonists',[]))>=3,'no usable colony: prohibit runner worldgen fallback')
        # Source fixture requirements, restored to actual prior values even if nondefault.
        for typ,field,value in [
            (E.EXT.S_FW,'depthEngineEnabled',True),
            (E.EXT.S_FW,'depthEngineLiveForTests',True),
            (E.EXT.S_FW,'liquidPumpEnabled',True),
            ('RimMandrake.FlowWorks.Hose.RM_HoseSettings','tankModesEnabled',True)]:
            static(typ,field,value,True); need(str(static(typ,field)).lower()==str(value).lower(),'fixture switch '+field)
        R['mode_precondition']={'tankModesEnabled':static('RimMandrake.FlowWorks.Hose.RM_HoseSettings','tankModesEnabled')}
        ident=call('jawa/type_probe',typeName='RimMandrake.FlowWorks.RM_MapComponent_Excavation')
        expected=hashlib.sha256((ROOT/'src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll').read_bytes()).hexdigest()
        R['assembly']=ident
        need(ident.get('mvidMatchesFile') is True and ident.get('assemblyFileSha256')==expected,'loaded identity mismatch')
        persist()
        cmd=[sys.executable,str(ROOT/'src/RimMandrake/FlowWorks/northstar/extension_proof.py'),'--live','--chains','liquid_pump','--out',str(OUT/'result.json')]
        R['runner_command']=cmd
        with (OUT/'runner.stdout.log').open('w',encoding='utf-8') as so,(OUT/'runner.stderr.log').open('w',encoding='utf-8') as se:
            p=subprocess.run(cmd,cwd=ROOT,stdout=so,stderr=se,timeout=600)
        R['runner_returncode']=p.returncode
        result=json.loads((OUT/'result.json').read_text(encoding='utf-8'))
        rows=result['chains'][0]['components']
        need(result['chains_run']==['liquid_pump'],'wrong chains')
        need([x['name'] for x in rows]==['pump_unpowered_idle','pump_draws_into_tank','pump_off_idles','pump_pours_back'],'missing chain rows')
        need(p.returncode==0 and result.get('all_green') is True and all(x['verdict']=='PASS' for x in rows),'production chain nonpass')
        R['status']='PASS'
    except BaseException as ex:
        R['status']='FAIL'; R['error']=repr(ex); R['traceback']=traceback.format_exc()
    finally:
        if baseline is not None:
            try:
                R['restore']['reload']=reload_baseline()
                R['restore']['rect']=rect()
                need(R['restore']['rect']==baseline,'whole map fingerprint differs')
            except BaseException as ex: R['restore']['errors'].append('scene: '+repr(ex))
        # Each debt is independent: failed reload cannot skip static restores.
        R['restore']['settings']=[]
        for x in prior:
            try:
                now=static(x['type'],x['field'])
                if now!=x['value']: static(x['type'],x['field'],x['value'],True)
                after=static(x['type'],x['field'])
                R['restore']['settings'].append(dict(x,after=after,changed=now!=x['value']))
                need(after==x['value'],'setting '+x['field'])
            except BaseException as ex: R['restore']['errors'].append('setting: '+repr(ex))
        try:
            now=debug_read()
            for k,v in debug.items():
                if now.get(k)!=v: call('jawa/debug_settings',action='set',field=k,value=v)
            R['restore']['debug']=debug_read()
            need(R['restore']['debug']==debug,'debug mismatch')
        except BaseException as ex: R['restore']['errors'].append('debug: '+repr(ex))
        if difficulty:
            try:
                keys=('threatScale','allowBigThreats')
                call('jawa/difficulty_tune',**{k:difficulty[k] for k in keys})
                R['restore']['difficulty']=call('jawa/difficulty_tune')['before']
                need(R['restore']['difficulty']==difficulty,'difficulty mismatch')
            except BaseException as ex: R['restore']['errors'].append('difficulty: '+repr(ex))
        try:
            after=T.saves_stat(SAVES)
            R['saves_added']=sorted(set(after)-set(saves_before))
            R['saves_changed']=[n for n in saves_before if after.get(n)!=saves_before[n]]
            R['canonical_after']={n:hashlib.sha256((Path(SAVES)/n).read_bytes()).hexdigest() for n in canonical}
            need(not R['saves_changed'],'an existing save changed')
            need(R['canonical_after']==canonical,'canonical hash changed')
        except BaseException as ex: R['restore']['errors'].append('saves: '+repr(ex))
        R['restore']['status']='FAIL' if R['restore']['errors'] else 'PASS'
        if R['restore']['errors']: R['status']='FAIL'
        R['finished']=time.time(); persist()
print(R['status'],R.get('error',''),R['restore']['status'],flush=True)
sys.exit(0 if R['status']=='PASS' else 1)
