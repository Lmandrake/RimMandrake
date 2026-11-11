#!/usr/bin/env python3
"""Acceptance-driver fault injection plus selected production C# pit-room tests.
Fake game outcomes verify assertions/cleanup; they never prove game behavior.
"""
from copy import deepcopy
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import concept_scenes as C

class Bridge:
    def __init__(self, fault=None):
        self.fault = fault
        self.settings = {'superdeepRoomsEnabled': True, 'pitRelativeClimbEnabled': True}
        self.original = dict(self.settings)
        self.debug = {f:True for f in ('enableStoryteller', 'enableRandomMentalStates', 'enableRandomDiseases')}
        self.original_debug = dict(self.debug)
        self.pawns = {}
        self.hostile_ids = set()
        self.ready_workers = set()
        self.tick = 100
        self.beds = []
        self.depth = 0
        self.baseline = True
        self.loads = 0
        self.snapshot_calls = 0

    def snapshot(self):
        self.snapshot_calls += 1
        return {'snapshot': 'fake'}

    def reload(self):
        self.loads += 1
        self.baseline = True
        self.pawns.clear()
        self.hostile_ids.clear()
        self.ready_workers.clear()
        self.beds.clear()
        if self.fault == 'bad_snapshot' and self.loads > 1:
            self.baseline = False

    def ticks(self, n):
        assert all(v is False for v in self.debug.values()), 'isolated controls missing before tick advance'
        assert all(C.CG._thing_number(pid) in C.CG.FIXTURE_IDS for pid in self.hostile_ids), 'undeclared hostile fixture'
        self.tick += n
        for p in self.pawns.values():
            if self.fault == 'sleeps_after_day' and n == 2500:
                p['rest'] = str(max(0.0, float(p['rest'])-0.04))
            if p['prisoner'] == 'True' and self.fault == 'escape' and n == 2500:
                p['kept'] = 'False'

    def call(self, tool, **kw):
        if tool == 'jawa/debug_settings':
            if kw['action'] == 'list': return {'success':True,'fields':[{'name':k,'value':v} for k,v in self.debug.items()]}
            self.debug[kw['field']] = kw['value']
            return {'success':True,'valueAfter':self.debug[kw['field']]}
        if tool == 'jawa/static_call':
            m, a = kw['method'], kw.get('args', '')
            r = 'OK'
            if m == 'Identity':
                assert kw.get('args') == 'probe', 'Identity(string) needs one nonempty bridge argument'
                r = 'IDENTITY mvid=fake sha256=fake'
            elif m == 'Rect': r = 'RECT sha256='+('original' if self.baseline else 'staged')+' beds='+str(len(self.beds))
            elif m == 'State': r = 'STATE '+' '.join(k+'='+str(v) for k,v in self.pawns[a].items())
            elif m == 'ProofCaptureDown':
                r = 'VERDICT '+('Allowed' if self.settings['superdeepRoomsEnabled'] else 'SettingOff')
            elif m == 'Care':
                w, p, mode, start = a.split(';')
                job = {'bed':'none','feed':'FeedPatient','deliver':'DeliverFood','tend':'TendPatient'}[mode]
                if self.fault == 'no_feed': job = 'none'
                if start == 'start' and job != 'none':
                    if w in self.ready_workers:
                        self.pawns[p]['food'] = '0.9'
                        self.pawns[w]['job'] = job
                        self.ready_workers.discard(w)
                    else:
                        self.pawns[w]['job'] = 'Wait'  # accepted does not mean started
                r = 'CARE kind='+mode+' job='+job
                if start == 'start': r += ' ordered='+('False' if self.fault == 'no_order' else 'True')
            return {'success':True, 'result':r}
        if tool == 'jawa/mod_settings_field':
            f = kw['field']
            if kw['action'] == 'set':
                v = kw['value']
                self.settings[f] = v.lower() == 'true' if v.lower() in ('true','false') else v
            return {'success':True,'value':self.settings.get(f, False)}
        if tool == 'jawa/stop_job':
            assert kw['mode'] == 'stopall', 'unknown stop_job mode'
            self.ready_workers.add(kw['pawnId'])
            self.pawns[kw['pawnId']]['job'] = 'none'
        if tool == 'jawa/set_work_priority':
            assert kw['workType'] in ('Warden', 'Doctor', 'Patient', 'PatientBedRest'), 'unknown work type'
            if self.fault == 'incapable_worker' or (self.fault == 'first_incapable' and kw['pawnId'] == 'Pawn2'):
                return {'success': False, 'details': {'disabledWorkTypes': [kw['workType']]}}
            return {'success': True, 'readBack': 3}
        if tool == 'jawa/list_pawns': return {'success':True, 'pawns':[]}
        if tool == 'jawa/site_state': return {'ticksGame':self.tick}
        if tool == 'jawa/destroy_batch': self.baseline = False
        if tool == 'jawa/flowworks_excavation_drive': self.depth = kw['deepenLevels']
        if tool == 'jawa/flowworks_excavation_report':
            return {'success':True,'depth':self.depth,'fill':1 if self.fault == 'wet' else 0,'isExcavated':True}
        if tool == 'jawa/spawn_pawn':
            pid = 'Pawn'+str(len(self.pawns))
            if kw['faction'] == 'hostile': self.hostile_ids.add(pid)
            self.pawns[pid] = {'id':pid,'x':kw['x'],'z':kw['z'],'downed':'False','dead':'False',
                              'prisoner':'False','kept':'False','food':'0.1','rest':('0.1' if self.fault == 'sleepy_fixture' else '0.8'),'inBed':'False'}
            return {'success':True,'pawns':[{'id':pid}]}
        if tool == 'jawa/pawn_force_incapacitate':
            if kw.get('action') == 'vanish':
                self.pawns[kw['pawn']]['dead'] = 'True'
            else:
                self.pawns[kw['pawn']]['downed'] = 'True'
        if tool == 'jawa/pawn_need': self.pawns[kw['pawn']]['food'] = str(kw['level'])
        if tool == 'jawa/pawn_health': self.pawns[kw['pawn']]['downed'] = 'False'
        if tool == 'jawa/ordered_job':
            p = self.pawns[kw['targetAId']]
            enabled = self.settings['superdeepRoomsEnabled']
            capture = (enabled and self.fault != 'no_capture') or self.fault == 'off_captures'
            if kw['jobDef'] == 'Capture': capture = True; p['inBed'] = 'True'
            if not enabled and kw['jobDef'] == 'RM_CaptureDown' and self.fault == 'off_refuses':
                return {'success': False, 'accepted': True, 'requestedJobDef': 'RM_CaptureDown'}
            if not enabled and kw['jobDef'] == 'RM_CaptureDown' and self.fault == 'off_unattempted':
                return {'success': False, 'accepted': False, 'requestedJobDef': 'RM_CaptureDown'}
            if capture: p['prisoner'] = p['kept'] = 'True'
            if self.fault == 'remote_warp' and self.beds: p['x'] = 49; p['kept'] = 'False'
        if tool == 'jawa/build_batch': self.beds.append({'id':'bed'})
        if tool == 'jawa/ordered_job':
            return {'success': True, 'accepted': True, 'requestedJobDef': kw['jobDef']}
        if tool == 'jawa/list_things':
            if kw.get('defName') == 'MealSurvivalPack':
                return {'success':True,'things': [] if self.fault == 'no_supply' else [{'stackCount':30}]}
            return {'success':True,'things':self.beds}
        return {'success':True}


def check(fault=None, abort=False, occupied=False):
    B = Bridge(fault)
    fixture_baseline = set(C.CG.FIXTURE_IDS)
    rec = {}
    failed = False
    try:
        saved = {}
        def save_occupied():
            saved['pawns'] = deepcopy(B.pawns)
            return {'snapshot':'occupied fake'}
        def load_occupied():
            B.pawns = deepcopy(saved['pawns'])
            if fault == 'lost_occupied':
                for p in B.pawns.values(): p['kept'] = 'False'
        C.scene_hole_prison(B, B.snapshot, B.reload, rec, abort=abort,
                            save_occupied=save_occupied if occupied else None,
                            load_occupied=load_occupied if occupied else None)
    except (AssertionError, RuntimeError):
        failed = True
    assert failed == bool((fault and fault not in ('first_incapable', 'off_refuses', 'sleeps_after_day')) or abort), (fault, failed, rec)
    assert B.snapshot_calls == 1 and B.loads == 2, (fault, B.loads)
    assert all(B.settings[k] == v for k,v in B.original.items()), (fault, B.settings)
    assert not B.pawns, (fault, B.pawns)
    assert C.CG.FIXTURE_IDS == fixture_baseline, 'fixture declaration leaked across runs'
    assert B.debug == B.original_debug, 'debug settings leaked across runs'
    assert rec['restore']['status'] == ('FAIL' if fault == 'bad_snapshot' else 'PASS')
    print('ok', fault or ('injected_abort' if abort else 'complete_scene'))

def run_driver_checks():
    for f in (None, 'no_capture', 'off_captures', 'remote_warp', 'no_feed', 'escape', 'wet', 'bad_snapshot', 'incapable_worker', 'no_order', 'off_unattempted', 'no_supply',
              'first_incapable', 'off_refuses', 'sleeps_after_day', 'sleepy_fixture'):
        check(f)
    check(abort=True)
    check(occupied=True)
    check('lost_occupied', occupied=True)
    C.CG.declare_fixture('Pawn0')
    try:
        check()  # a pre-existing declaration with the same id belongs to its caller
    finally:
        C.CG.withdraw_fixture('Pawn0')


if __name__ == "__main__":
    run_driver_checks()
    # Also compile/run the actual Verse-free production logic, only these three cases.
    root = HERE.parents[3]
    subprocess.run([sys.executable, str(root/'src/RimMandrake/Utils/selftest_flowworks_stock.py'),
                    '--only', 'PitRoom_*'], check=True)
    print('PASS: fault controls, abort cleanup and selected C# pit-room cases')
