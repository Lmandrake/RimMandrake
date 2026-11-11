#!/usr/bin/env python3
"""Focused disposable acceptance for REEL_BODY_INLET_FIX_SKIPS_DEPTH_RULES.

Windows Python; bridge held; published FlowWorks deployed. Existing calm site only,
no worldgen. Complete scene-begin save/reload and rectangle/settings verification in finally.
No ticking, jobs, fluid transfer or visual-approval claim: actual Find/Port contact and bands only.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
for p in (ROOT/'src/RimMandrake/Utils', ROOT/'src/RimMandrake/Utils/modcheck'):
    sys.path.insert(0, str(p))
PORTS = 'RimMandrake.FlowWorks.Hose.HosePorts'
PRISON = 'RimMandrake.FlowWorks.RM_PitPrisonProof'
SETTINGS = 'RimMandrake.FlowWorks.Machinery.RM_MachinerySettings'
RECT = '30,30,24,18'
REEL = (38, 36)

def require(ok, why):
    if not ok:
        raise AssertionError(why)

def run(B, T, saves, receipt, expected_sha):
    calls = receipt.setdefault('calls', [])
    def call(tool, **kw):
        r = B.call(tool, **kw)
        calls.append(dict(tool=tool, args=kw, result=r))
        require(not isinstance(r, dict) or r.get('success') is not False, str((tool,r)))
        return r
    def sc(typ, method, arg):
        r = call('jawa/static_call', type=typ, method=method, args=arg)
        require('result' in r, 'missing static result '+str(r))
        return str(r['result'])
    def rect():
        return sc(PRISON, 'Rect', RECT)
    def port(label):
        r = json.loads(sc(PORTS, 'ProofBodyInlet', '0,%d,%d'%REEL))
        require(r.get('success') is True, str(r))
        require(r['rect'] == [38,36,2,2], 'fixture footprint differs: '+str(r))
        require(r['portId'] == r['hydraulicPortId'], 'Find and hydraulic Port differ: '+str(r))
        receipt.setdefault('readings', {})[label] = r
        return r
    def setting(action, value=None):
        kw = dict(typeName=SETTINGS, field='lineCrossingRulesEnabled', action=action)
        if value is not None:
            kw['value'] = str(value)
        return call('jawa/mod_settings_field', **kw)
    def set_rules(value):
        setting('set', value)
        require(str(setting('get')['value']).lower()==str(value).lower(), 'rules readback differs')
    def build(ops, count):
        r=call('jawa/build_batch', ops=ops, faction='player', wipeExisting=False)
        require(r.get('placed')==count, 'build cardinality differs: '+str(r))
        call('jawa/map_commit')
        return r
    def dig(x,z):
        call('jawa/flowworks_excavation_drive',x=x,z=z,deepenLevels=4,setFill=0)
        r=call('jawa/flowworks_excavation_report',x=x,z=z)
        require(r.get('depth')==4 and r.get('fill')==0 and r.get('isExcavated') is True,'not dry D4: '+str(r))
        return r
    receipt['identity']=sc(PRISON,'Identity','probe')
    require('sha256='+expected_sha in receipt['identity'],'wrong loaded DLL '+receipt['identity'])
    receipt['site']=T.load_site(call,'calm')
    require(receipt['site']['verified'],'calm load failed')
    name='WHITTLE_ReelInlet_Begin_'+time.strftime('%Y%m%dT%H%M%S')
    old=setting('get')['value']
    saved=False
    try:
        receipt['snapshot']=T.save_site(call,name,saves)
        require(receipt['snapshot'].get('bytes',0)>0 and receipt['snapshot'].get('path'),'guarded snapshot missing file receipt')
        saved=True
        restored=T.load_site(call,'calm',name=name,check=False)
        require(restored['verified'],'begin snapshot reload failed')
        receipt['before']=rect()
        set_rules(True)
        call('jawa/set_roof_batch',ops='None:'+RECT)
        call('jawa/destroy_batch',rects=RECT,categories='All')
        sc('RimMandrake.FlowWorks.RM_NorthstarProofs','ProofResetRect',RECT.replace(',',';'))
        call('jawa/set_terrain_batch',ops='Soil:'+RECT)
        call('jawa/set_fog',action='unfog',rect=RECT)
        # West-facing 2x2 Position is one east of its minimum corner.
        build('RM_HoseReel:39,36,3;RM_LiquidTank:40,36',2)
        a=port('same_band_multicell')
        require(a['portId']>=0 and a['side']==[1,0] and a['contact']==[40,36]
                and a['bodyBand']==a['contactBand']==0,'same-band body inlet absent')
        # Tank occupies x=40..41,z=36..37 (read back selected real contact above).
        # Dig only first edge contact: the same tank remains reachable at its second contact.
        receipt['depth_first']=dig(40,36)
        a2=port('alternate_contact_same_tank')
        require(a2['portId']==a['portId'] and a2['contact']==[40,37]
                and a2['bodyBand']==a2['contactBand']==0,'valid later tank contact not selected')
        receipt['depth_second']=dig(40,37)
        b=port('sheer_wall_refused')
        require(b['portId']==-1,'body inlet crossed sheer wall')
        set_rules(False)
        off=port('rules_off')
        require(off['portId']==a['portId'] and off['contact']==[40,36]
                and off['bodyBand']==off['contactBand']==0,'rules-off legacy contact absent')
        set_rules(True)
        build('RM_UniversalPipe:37,36',1)
        alt=port('alternate_neighbour')
        require(alt['portId']>=0 and alt['portId']!=a['portId'] and alt['side']==[-1,0]
                and alt['contact']==[37,36] and alt['bodyBand']==alt['contactBand']==0,'valid alternate neighbour absent')
        # Add an invalid preferred east pipe: it must not displace the valid west pipe.
        call('jawa/destroy_batch',rects='40,36,2,2',categories='Building')
        build('RM_UniversalPipe:40,36',1)
        fallback=port('invalid_preferred_east_pipe')
        require(fallback['portId']==alt['portId'] and fallback['contact']==alt['contact'],'invalid preferred candidate displaced valid fallback')
        receipt['staged_rect']=rect()
        call('rimworld/frame_cell_rect',x=30,z=30,width=24,height=18,paddingCells=1)
        time.sleep(2)
        receipt['screenshot']=call('jawa/take_screenshot',fileName='WHITTLE_ReelInlet_'+time.strftime('%Y%m%dT%H%M%S'))
        receipt['assertions']='same-band 2x2 body/tank, later valid contact, full sheer refusal, rules-off, alternate neighbour, invalid preferred pipe fallback; Find equals forced hydraulic Port in every arm'
    finally:
        errors=[]
        receipt['restore']={}
        if saved:
            try:
                r=T.load_site(call,'calm',name=name,check=False)
                receipt['restore']['load']=r
                require(r['verified'],'finally snapshot reload failed')
                receipt['restore']['rect']=rect()
                require(receipt['restore']['rect']==receipt.get('before'),'snapshot rectangle differs after restoration')
            except Exception as e:
                errors.append(repr(e))
        try:
            set_rules(old)
            receipt['restore']['rules']=setting('get')['value']
            require(str(old).lower()==str(receipt['restore']['rules']).lower(),'rules restore differs')
        except Exception as e:
            errors.append(repr(e))
        receipt['restore']['status']='FAIL' if errors else 'PASS'
        require(not errors,'restoration failed: '+str(errors))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args()
    import validation_core as V
    import test_site_saves as T
    from game_paths import SAVES
    res=dict(script=__file__,started=time.time(),mode='live')
    try:
        run(V.Bridge(),T,SAVES,res,hashlib.sha256((HERE.parent/'Assemblies/RimMandrakeFlowWorks.dll').read_bytes()).hexdigest())
        res['status']='PASS'
    except Exception as e:
        res.update(status='FAIL',error=repr(e))
    finally:
        res['finished']=time.time();Path(a.out).write_text(json.dumps(res,indent=2,default=str),encoding='utf-8')
        print(res['status'],a.out,res.get('error',''),flush=True)
    return 0 if res['status']=='PASS' else 1
if __name__=='__main__':
    sys.exit(main())
