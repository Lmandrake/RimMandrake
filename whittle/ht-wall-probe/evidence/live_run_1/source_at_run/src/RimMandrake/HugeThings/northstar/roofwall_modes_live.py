"""Bounded R4 loaded-method integration, Windows Python against this clone.

PROVE: invoke existing RoofWallProbe for T2 + force-out in both measured modes.
EXPECT: T2 holes RoofConstructed in both; default wall HP unchanged, legacy HP
falls; both controls preserve roof and positive wall HP. LIES: absent subjects,
unknown settings, vacuous HP, failed hooks or a drifting mode cannot pass.
Position is assigned directly: no natural movement or clearing-job acceptance.
Load an EXISTING RM_TestSite save, guard a new scene-begin save, reload before
baseline and finally restore full measured rectangle and exact touched settings.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import time
import uuid

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
for p in (HERE, ROOT/'src/RimMandrake/Utils', ROOT/'src/RimMandrake/Utils/modcheck'):
    sys.path.insert(0, str(p))
import validation_core as V
import test_site_saves as T
import helpers as H
import game_paths as G
import titan_test_races_live as L
from live_results import aggregate

PROOF = 'RimMandrake.FlowWorks.RM_PitPrisonProof'
RECT = '92,92,24,24'
CELL = (103,103)


def require(ok, why):
    if not ok:
        raise RuntimeError(why)


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', required=True, type=Path)
    a=ap.parse_args()
    rec=dict(script=str(Path(__file__).resolve()), script_sha256=digest(__file__), level='L1',
             scope='R4 only, Position-setter teleport; no path/job or walked clearing acceptance',
             started=time.time(), calls=[], ok=False)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    def persist():
        a.out.write_text(json.dumps(rec,indent=2,default=str,allow_nan=False)+'\n',encoding='utf-8')
    b=V.Bridge()
    def call(tool, **kw):
        result=b.call(tool, **kw)
        # Credentials never enter evidence; no full Player.log is fetched.
        require(not re.search(r'bridge token:|authorization:|bearer ',json.dumps(result),re.I),'credential-bearing response refused')
        rec['calls'].append(dict(tool=tool,args=kw,result=result)); persist()
        require(result.get('success') is not False, '%s refused: %s' % (tool,result))
        return result
    def sc(method,args='',typ=PROOF):
        r=call('jawa/static_call',type=typ,method=method,args=args)
        require(r.get('success') is True and isinstance(r.get('result'),str) and not r['result'].startswith('FAIL'),str(r))
        return r['result']
    def read(field,typ=L.SETTINGS):
        r=call('jawa/mod_settings_field',typeName=typ,action='get',field=field)
        require(r.get('success') is True and isinstance(r.get('value'),str),'not a raw setting string: '+field)
        return r['value']
    def things():
        r=call('jawa/list_things',rect=RECT,limit=5000)
        require(r.get('isCompleteList') is True and r.get('countMatched')==len(r.get('things',[])), 'incomplete rectangle census')
        return r['things']
    class Adapter:
        def call(self,tool,kw): return call(tool,**kw)
    R=L.Run(Adapter(), str(a.out.with_name(a.out.stem+'_rows.json')))
    R.required_rows=(L.ROOF_ROW,)
    saved=False; baseline=None; tx=None; originals={}; debug_originals={}; difficulty=None
    snapshot='CODEX_RoofWall_Begin_'+time.strftime('%Y%m%dT%H%M%S')+'_'+uuid.uuid4().hex[:8]
    try:
        # Validate deployed pair and all compiled source hashes without rebuilding C#.
        mod=HERE.parent
        dll=mod/'Assemblies/RM_HugeThings.dll'; stamp=dll.with_suffix('.dll.srchash')
        installed=Path(G.LOCAL_MODS)/'HugeThings/Assemblies/RM_HugeThings.dll'
        text=stamp.read_text(encoding='utf-8')
        inputs=re.findall(r'^([0-9a-f]{64}) (.+)$',text,re.M)
        require(inputs and all(digest(mod/'Source'/p.strip())==h for h,p in inputs),'source stamp mismatch')
        require('# dll: '+digest(dll) in text,'DLL stamp mismatch')
        rec['artifact']=dict(repo_sha256=digest(dll),deployed_sha256=digest(installed),stamp=text,
                             stamp_sha256=digest(stamp),deployed_stamp_sha256=digest(installed.with_suffix('.dll.srchash')))
        require(rec['artifact']['repo_sha256']==rec['artifact']['deployed_sha256'] and
                rec['artifact']['stamp_sha256']==rec['artifact']['deployed_stamp_sha256'],'deployed DLL/stamp differ')
        rec['running']=call('jawa/running_mods',assembly='RM_HugeThings',details=True)
        run=rec['running']; ids=[x.lower() for x in run.get('packageIds',[])]
        # Exact ordered tier is independently checked by both preflights.
        require(run.get('count')==len(ids)==14 and len(set(ids))==14 and
                all(x in ids for x in ('ludeon.rimworld','ludeon.rimworld.royalty','ludeon.rimworld.ideology',
                'ludeon.rimworld.biotech','ludeon.rimworld.anomaly','ludeon.rimworld.odyssey',
                'mandrake.rm.hugethings','mandrake.rm.hugethingstestraces','mandrake.rm.flowworks','mandrake.rm.patches')),
                'wrong loaded all-DLC tier')
        matches=run.get('assembly',{}).get('matches',[])
        require(len(matches)==1 and matches[0].get('sha256')==digest(dll) and
                [x.lower() for x in matches[0].get('claimedBy',[])]==['mandrake.rm.hugethings'], 'loaded assembly identity ambiguous')
        originals={f:read(f) for f in L.ROOF_FIELDS}
        rec['originals']=dict(originals)
        rec['ladder']=read('tierThresholdsCustom')
        require(rec['ladder'].lower()=='false','custom startup tier ladder')
        name=T.read_registry().get('calm',{}).get('save') or T.SITES['calm']['save']
        require(name.startswith('RM_TestSite_') and (Path(G.SAVES)/(name+'.rws')).is_file(),'existing disposable fixture missing')
        rec['load']=T.load_site(call,'calm',name=name,map_controls=('modal_broker',))
        require(rec['load']['verified'],str(rec['load']))
        rec['snapshot']=T.save_site(call,snapshot,G.SAVES); saved=True
        rec['baseline_load']=T.load_site(call,'calm',name=snapshot,check=False,map_controls=('modal_broker',))
        require(rec['baseline_load']['verified'],'snapshot baseline reload failed')
        baseline=sc('Rect',RECT); rec['baseline']=baseline
        require(re.fullmatch(r'RECT sha256=[0-9a-f]{64} beds=\d+',baseline),'invalid rectangle fingerprint')
        tx=H.SettingsTransaction(T.call_session(call)); tx.__enter__()
        debug_originals={f:read(f,'Verse.DebugSettings') for f in
                         ('enableStoryteller','enableRandomMentalStates','enableRandomDiseases')}
        difficulty=call('jawa/difficulty_tune')['before']
        rec['debug_originals']=dict(debug_originals);rec['difficulty_original']=difficulty
        quiet=H.quiet_world(T.call_session(call),tx,wild_spawner=False,log_raids=False)
        rec['quiet']=quiet.evidence
        require(quiet.verified,'quiet controls unverified')
        call('rimworld/set_time_speed',speed=0)
        rec['clock_before']=call('jawa/site_state')['ticksGame']
        rec['rectangle_before_clear']=things()
        # No pawn may be removed by the rectangle clear, even on a disposable save.
        pawns=call('jawa/list_pawns',rect=RECT,limit=1000)
        require(pawns.get('success') is True and pawns.get('returned')==0 and pawns.get('truncated')==0 and pawns.get('pawns')==[],'test rectangle contains a pawn or census unreadable')
        call('jawa/set_roof_batch',ops='None:'+RECT)
        call('jawa/destroy_batch',categories='All',rects=RECT)
        require(not things(),'rectangle not empty after bounded clear')
        rec['tiers']=sc('TierReport',L.T2+','+L.CTL,L.HOOKS)
        rep=L.parse_tiers(rec['tiers'])
        require(all(rep.get(k,{}).get('tier')==tier and rep[k].get('adultTier')==tier and
                    float(rep[k]['bodySize'])==8 for k,tier in ((L.T2,'T2'),(L.CTL,'None'))),'fixture tier identity mismatch')
        empty_hash=sc('Rect',RECT)
        empty_roofs=call('jawa/get_roof_batch',rects=RECT)
        require(empty_roofs.get('cellsRead')==24*24 and empty_roofs.get('roofs')==['None'],'rectangle still roofed')
        call('jawa/set_roof_batch',ops='RoofConstructed:104,103')
        roof_hash=sc('Rect',RECT)
        require(roof_hash!=empty_hash,'fingerprint blind to planted roof')
        call('jawa/build_batch',ops='Wall:104,103',stuff='WoodLog',faction='player')
        wall_hash=sc('Rect',RECT)
        planted=things()
        require(len(planted)==1 and planted[0].get('def')=='Wall' and planted[0].get('stuff')=='WoodLog',
                'planted wood wall not measured')
        require(wall_hash!=roof_hash,'fingerprint blind to planted wall')
        call('jawa/set_roof_batch',ops='None:104,103')
        call('jawa/destroy_batch',categories='All',rects='104,103,1,1')
        require(sc('Rect',RECT)==empty_hash,'planted-change control left residue')
        rec['fingerprint_control']=dict(empty=empty_hash,roof=roof_hash,wall=wall_hash,planted=planted)
        rec['residue_checks']=[]
        def after_probe(kind,cell):
            ts=things()
            ps=call('jawa/list_pawns',rect=RECT,limit=1000)
            roofs=call('jawa/get_roof_batch',rects=RECT)
            current=sc('Rect',RECT)
            clean=(not ts and ps.get('returned')==0 and ps.get('truncated')==0 and ps.get('pawns')==[] and
                   roofs.get('cellsRead')==24*24 and roofs.get('roofs')==['None'] and current==empty_hash)
            rec['residue_checks'].append(dict(kind=kind,cell=cell,things=ts,pawns=ps,roofs=roofs,hash=current,clean=clean))
            return clean
        L.roofwall_row(R,[CELL],after_probe=after_probe); rec['roofwall']=getattr(R,'roofwall_evidence',None)
        rec['rows']=R.rows;rec['summary']=aggregate(R.rows,(L.ROOF_ROW,))
        rec['clock_after']=call('jawa/site_state')['ticksGame']
        require(rec['clock_before']==rec['clock_after'],'unexpected simulation ticks during Position-setter probe')
        require(rec['summary']['gameplay_pass'] is True,'R4 strict aggregate failed')
        rec['ok']=True
    except Exception as ex:
        rec['error']=repr(ex)
    finally:
        errors=[]
        if saved:
            try:
                rec['restore_load']=T.load_site(call,'calm',name=snapshot,check=False,map_controls=('modal_broker',))
                require(rec['restore_load']['verified'],'scene-begin reload failed')
                rec['restore_hash']=sc('Rect',RECT)
                require(baseline is not None and rec['restore_hash']==baseline,'full rectangle hash differs')
            except Exception as ex: errors.append(repr(ex))
        if tx:
            try:
                tx.__exit__(None,None,None)
                rec['difficulty_restored']=call('jawa/difficulty_tune')['before']
                require(all(rec['difficulty_restored'].get(f)==difficulty[f] for f in tx.touched_difficulty),'difficulty differs')
            except Exception as ex: errors.append(repr(ex))
        rec['restored_settings']={};rec['restored_debug']={}
        for typ, prior, key in ((L.SETTINGS,originals,'restored_settings'),('Verse.DebugSettings',debug_originals,'restored_debug')):
            for f,v in prior.items():
                try:
                    call('jawa/mod_settings_field',typeName=typ,action='set',field=f,value=v)
                    actual=read(f,typ);rec[key][f]=actual
                    require(actual==v,'exact raw restoration mismatch: '+f)
                except Exception as ex: errors.append(repr(ex))
        rec['restoration']=dict(attempted=saved,ok=saved and baseline is not None and not errors,errors=errors)
        rec['ok']=rec['ok'] and rec['restoration']['ok'];rec['finished']=time.time();persist()
        b.S.close()
    print('R4 L1 strict proof:',rec['ok'],rec.get('error',''),rec['restoration'],flush=True)
    return 0 if rec['ok'] else 1


if __name__=='__main__':
    sys.exit(main())
