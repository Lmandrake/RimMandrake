#!/usr/bin/env python3
"""Bounded P1 live proof on the all-DLC HugeThingsTestRaces + FlowWorks tier.

Uses an existing disposable calm save, a synthetic harness-only two-contact oak,
and grounded elephant test races. Never worldgen or flight. PROVE: distant pawn's
only corridor exit stays open; 100 sparse plants eventually realize their contacts
under the declared production scheduler cap; obstructed T3 conversion survives reload, retries
without wiping its obstruction, and cannot butcher around the site-only contract.
LIES: zero blockers / zero workload deferral, a pawn already trapped, a missing corpse,
a disabled site feature, accepted-but-not-executed orders, or absent controls cannot
pass. Restore the whole scene-begin save, verify its rectangle hash and all statics.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
for p in (ROOT/'src/RimMandrake/Utils', ROOT/'src/RimMandrake/Utils/modcheck'):
    sys.path.insert(0, str(p))
import validation_core as V
import test_site_saves as T
import helpers as H
from game_paths import SAVES

MC = 'RimMandrake.HugeThings.MapComponent_HugeFootprints'
HOOKS = 'RimMandrake.TitanicCreatures.TitanValidationHooks'
SETTINGS = 'RimMandrake.HugeThings.RM_HugeThingsSettings'
PROOF = 'RimMandrake.FlowWorks.RM_PitPrisonProof'
RECT = '40,70,185,155'
BLOCKER = 'RM_HugeTrunkBlocker'
PLANT = 'RM_TestContactPlant'
SCHEDULER_SOURCE = (HERE.parent/'Source/MapComponent_HugeFootprints.cs').read_text(encoding='utf-8')
WORK_CAP = int(re.search(r'const int WorkUnitsPerTick = (\d+);', SCHEDULER_SOURCE)[1])
VISIT_CAP = int(re.search(r'const int RefreshesPerTick = (\d+);', SCHEDULER_SOURCE)[1])


def require(ok, why):
    if not ok:
        raise AssertionError(why)


def kv(txt):
    return dict(re.findall(r'(\w+)=([^\s|]+)', str(txt)))


class HarnessRefusal(RuntimeError):
    pass


class Run:
    def __init__(self, receipt):
        self.b = V.Bridge()
        self.rec = receipt
        self.prior = {}

    def call(self, tool, allow=False, **args):
        r = self.b.call(tool, **args)
        self.rec['calls'].append(dict(tool=tool, args=args, result=r))
        if not allow and r.get('success') is False:
            raise HarnessRefusal(f'{tool} refused: {r}')
        return r

    def sc(self, method, args='', typ=MC):
        r = self.call('jawa/static_call', type=typ, method=method, args=args)
        require('result' in r and not str(r['result']).startswith('FAIL'), str(r))
        return str(r['result'])

    def setting(self, field, value):
        if field not in self.prior:
            self.prior[field] = self.call('jawa/mod_settings_field', typeName=SETTINGS, field=field, action='get')['value']
        self.call('jawa/mod_settings_field', typeName=SETTINGS, field=field, action='set', value=str(value))
        got = self.call('jawa/mod_settings_field', typeName=SETTINGS, field=field, action='get')['value']
        require(str(got).lower() == str(value).lower(), f'{field} did not stick')

    def ticks(self, n):
        before = self.call('jawa/site_state')['ticksGame']
        self.b.ticks(n)
        after = self.call('jawa/site_state')['ticksGame']
        require(after-before == n, f'tick delta {after-before} != {n}')

    def things(self, defname, rect):
        r = self.call('jawa/list_things', defName=defname, rect=rect, limit=1000)
        require('things' in r and r.get('countMatched') == len(r['things']), f'incomplete census: {r}')
        return r['things']

    def stage(self, roots):
        r = self.call('jawa/artboard_stage', phase='subjects', pause=True, killHostiles=False,
                      ops='\n'.join(f'id=p{i}|kind=plant|x={x}|z={z}|def={PLANT}|growth=1' for i,(x,z) in enumerate(roots)))
        require(len(r.get('ops', [])) == len(roots) and all(x.get('ok') for x in r['ops']), f'plant staging: {r}')

    def reachable(self, pawn):
        # This tool issues an order even for waitTicks=0. Read CanReach as the answer,
        # stop immediately while paused, and require that no time or position changed.
        r = self.call('jawa/order_pawn', allow=True, pawnId=pawn, x=112, z=100,
                      pathEndMode='oncell', waitTicks=0, unpause=False, draft=True)
        self.call('jawa/stop_job', pawnId=pawn, mode='stopall')
        rows = r.get('pawns', [])
        require(len(rows)==1 and r.get('ticksElapsed')==0 and rows[0]['start']==rows[0]['end'], f'bad paused reach probe: {r}')
        return rows[0]['canReach'] is True

    def footprints(self):
        # Removing natural rock supports without its roof drops CollapsedRocks
        # during the closure clock, re-obstructing a successfully cleared site.
        self.call('jawa/set_roof_batch', ops='None:70,90,48,22;None:120,120,100,100')
        self.call('jawa/destroy_batch', categories='All', rects='70,90,48,22;120,120,100,100')
        self.call('jawa/set_terrain_batch', ops='Soil:70,90,48,22;Soil:120,120,100,100')
        walls = [(x,z) for x in range(75,101) for z in (99,101)] + [(75,100)]
        self.call('jawa/build_batch', ops=';'.join(f'Wall:{x},{z}' for x,z in walls), stuff='WoodLog', faction='player')
        p = self.call('jawa/spawn_pawn', kindDef='Colonist', x=77, z=100, faction='player', count=1, xenotype='Baseliner')['pawns']
        require(len(p)==1, str(p))
        pawn = p[0]['id']
        require(self.reachable(pawn), 'corridor pawn already trapped before plant')
        self.stage([(102,100)])
        self.ticks(120)
        probe = self.sc('DebugPlantState', 'current|102,100')
        self.rec['closure'] = dict(probe=probe, reachable=self.reachable(pawn), blockers=self.things(BLOCKER,'98,98,9,5'))
        f = kv(probe)
        require(f.get('claimed')=='2' and f.get('realized')=='1' and f.get('pending')=='1', f'closure has no positive realized/refused pair: {probe}')
        require(self.rec['closure']['reachable'] and len(self.things(BLOCKER,'100,100,1,1'))==0,
                'plant closed the distant pawn corridor')
        roots=[(130+8*x,130+8*z) for x in range(10) for z in range(10)]
        self.stage(roots)
        samples=[]
        for tick in range(1,241):
            self.ticks(1)
            txt=self.sc('DebugCounts','current')
            f=kv(txt)
            used, cap=map(int,f['work'].split('/'))
            require(cap==WORK_CAP and 0<=used<=cap and int(f['ownersVisited'])<=VISIT_CAP,
                    f'scheduler cap violated: {txt}')
            samples.append(dict(tick=tick, counts=txt))
            if int(f['realized'])>=201:
                break
        self.rec['budget_samples']=samples
        count=len(self.things(BLOCKER,'120,120,100,100'))
        require(int(kv(samples[0]['counts'])['realized'])<201, 'no deferred-work pressure on the first tick')
        self.rec['work_cap']=WORK_CAP
        self.rec['visit_cap']=VISIT_CAP
        self.rec['cap_exhaustion_observed']=any(int(kv(s['counts'])['budgetRefusals'])>0 for s in samples)
        # This live workload proves owner slicing and eventual realization. The
        # production-code offline harness separately forces exhaustion across maps;
        # a live counter that never hits its cap is not evidence of exhaustion.
        require(count==200, f'budget starvation: {count}/200 sparse contacts after {len(samples)} ticks')
        require(self.reachable(pawn), 'stress planting closed the corridor')
        self.rec['footprints']='PASS'

    def corpse(self, tx):
        self.setting('corpseSiteEnabled',True)
        self.setting('yieldCurveEnabled',False)
        gated=self.sc('ButcherYieldReport','RM_TestTitanT3Adult',HOOKS)
        require(kv(gated).get('meat')=='0' and kv(gated).get('leather')=='0', 'T3 bypass with curve off: '+gated)
        self.setting('corpseSiteEnabled',False)
        control=self.sc('ButcherYieldReport','RM_TestTitanT3Adult',HOOKS)
        require(int(kv(control)['meat'])>0, 'disabled-feature butcher control produced no meat')
        self.setting('corpseSiteEnabled',True)
        self.call('jawa/set_roof_batch', ops='None:46,166,9,9')
        self.call('jawa/destroy_batch', categories='All', rects='46,166,9,9')
        self.call('jawa/set_terrain_batch', ops='Soil:46,166,9,9')
        self.call('jawa/build_batch',ops='Wall:51,171',stuff='WoodLog',faction='player')
        wall=self.things('Wall','51,171,1,1')
        require(len(wall)==1, 'obstruction not built')
        before=int(kv(self.sc('SiteReport','',HOOKS))['sites'])
        killed=self.sc('KillTitanAt','RM_TestTitanT3Adult|50,170',HOOKS)
        corpse=kv(killed)['corpse']
        self.ticks(251)
        require(any(t['id']==corpse for t in self.things('Corpse_RM_TestTitanT3Adult','46,166,9,9')), 'blocked corpse disappeared')
        require(self.things('Wall','51,171,1,1')==wall, 'conversion wiped or damaged its obstruction')
        require(int(kv(self.sc('SiteReport','',HOOKS))['sites'])==before, 'blocked site converted')
        name='CODEX_HugeP1_Occupied_'+time.strftime('%Y%m%dT%H%M%S')
        self.rec['occupied_save']=T.save_site(self.call,name,SAVES)
        loaded=T.load_site(self.call,'calm',name=name,check=False,map_controls=('modal_broker',))
        self.rec['occupied_load']=loaded
        require(loaded['verified'],str(loaded))
        H.quiet_world(T.call_session(self.call),tx,wild_spawner=False,log_raids=False)
        require(any(t['id']==corpse for t in self.things('Corpse_RM_TestTitanT3Adult','46,166,9,9')), 'corpse lost on occupied reload')
        require(self.things('Wall','51,171,1,1')==wall, 'obstruction lost on reload')
        self.call('jawa/destroy_batch',categories='All',rects='51,171,1,1')
        self.ticks(251)
        after=self.sc('SiteReport','',HOOKS)
        require(not self.things('Corpse_RM_TestTitanT3Adult','46,166,9,9'), 'conversion never retried')
        require(int(kv(after)['sites'])==before+1 and int(kv(after)['meat'])>0, 'site lacks raw harvest pool: '+after)
        self.rec['corpse']=dict(status='PASS',butcher_gated=gated,butcher_control=control,killed=killed,site=after,obstruction=wall)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',required=True)
    a=ap.parse_args()
    rec=dict(script=__file__,calls=[],started=time.time(),scope='isolated 14-mod all-DLC synthetic-plant/grounded-elephant fixture')
    r=Run(rec)
    snap='CODEX_HugeP1_Begin_'+time.strftime('%Y%m%dT%H%M%S')
    saved=False
    baseline=None
    tx=None
    rec['artifact_sha256']=hashlib.sha256((HERE.parent/'Assemblies/RM_HugeThings.dll').read_bytes()).hexdigest()
    try:
        loaded=T.load_site(r.call,'calm')
        require(loaded['verified'],str(loaded))
        rec['snapshot']=T.save_site(r.call,snap,SAVES)
        saved=True
        require(T.load_site(r.call,'calm',name=snap,check=False)['verified'],'initial snapshot reload failed')
        baseline=r.sc('Rect',RECT,PROOF)
        rec['baseline']=baseline
        tx=H.SettingsTransaction(T.call_session(r.call))
        tx.__enter__()
        rec['quiet']=H.quiet_world(T.call_session(r.call),tx,wild_spawner=False,log_raids=False)
        for field,value in dict(giantPlantsEnabled=True,plantTrunkEnabled=True,plantTrunkScale=1,giantAnimalsEnabled=True).items():
            r.setting(field,value)
        r.footprints()
        r.corpse(tx)
        rec['status']='PASS'
    except Exception as ex:
        rec['status']='UNMEASURED' if isinstance(ex,HarnessRefusal) else 'FAIL'
        rec['failure_class']='HARNESS' if isinstance(ex,HarnessRefusal) else 'MOD_OR_SITE_ASSERTION'
        rec['error']=repr(ex)
    finally:
        errors=[]
        if saved:
            try:
                rec['restore_load']=T.load_site(r.call,'calm',name=snap,check=False)
                require(rec['restore_load']['verified'],'snapshot did not reload')
                rec['restore_hash']=r.sc('Rect',RECT,PROOF)
                require(baseline is not None and rec['restore_hash']==baseline,'snapshot rectangle hash differs')
            except Exception as ex: errors.append(repr(ex))
        rec['restore_settings']={}
        for field,value in r.prior.items():
            try:
                r.setting(field,value)
                rec['restore_settings'][field]=value
            except Exception as ex: errors.append(repr(ex))
        if tx:
            try: tx.__exit__(None,None,None)
            except Exception as ex: errors.append(repr(ex))
        rec['restore_errors']=errors
        if errors: rec['status']='FAIL'
        rec['finished']=time.time()
        Path(a.out).write_text(json.dumps(rec,indent=2,default=str),encoding='utf-8')
        print(rec['status'],rec.get('error',''),errors,flush=True)
    return 0 if rec['status']=='PASS' else 1


if __name__=='__main__':
    sys.exit(main())
