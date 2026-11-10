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
        self.pawns = {}
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
        self.beds.clear()
        if self.fault == 'bad_snapshot' and self.loads > 1:
            self.baseline = False

    def ticks(self, n):
        self.tick += n
        for p in self.pawns.values():
            if p['prisoner'] == 'True' and self.fault == 'escape' and n == 2500:
                p['kept'] = 'False'

    def call(self, tool, **kw):
        if tool == 'jawa/static_call':
            m, a = kw['method'], kw.get('args', '')
            r = 'OK'
            if m == 'Identity': r = 'IDENTITY mvid=fake sha256=fake'
            elif m == 'Rect': r = 'RECT sha256='+('original' if self.baseline else 'staged')+' beds='+str(len(self.beds))
            elif m == 'State': r = 'STATE '+' '.join(k+'='+str(v) for k,v in self.pawns[a].items())
            elif m == 'ProofCaptureDown':
                r = 'VERDICT '+('Allowed' if self.settings['superdeepRoomsEnabled'] else 'SettingOff')
            elif m == 'Care':
                w, p, mode, start = a.split(';')
                job = {'bed':'none','feed':'FeedPatient','deliver':'DeliverFood','tend':'TendPatient'}[mode]
                if self.fault == 'no_feed': job = 'none'
                if start == 'start' and job != 'none': self.pawns[p]['food'] = '0.9'
                r = 'CARE kind='+mode+' job='+job
            return {'success':True, 'result':r}
        if tool == 'jawa/mod_settings_field':
            f = kw['field']
            if kw['action'] == 'set':
                v = kw['value']
                self.settings[f] = v.lower() == 'true' if v.lower() in ('true','false') else v
            return {'success':True,'value':self.settings.get(f, False)}
        if tool == 'jawa/list_pawns': return {'success':True, 'pawns':[]}
        if tool == 'jawa/site_state': return {'ticksGame':self.tick}
        if tool == 'jawa/destroy_batch': self.baseline = False
        if tool == 'jawa/flowworks_excavation_drive': self.depth = kw['deepenLevels']
        if tool == 'jawa/flowworks_excavation_report':
            return {'success':True,'depth':self.depth,'fill':1 if self.fault == 'wet' else 0,'isExcavated':True}
        if tool == 'jawa/spawn_pawn':
            pid = 'Pawn'+str(len(self.pawns))
            self.pawns[pid] = {'id':pid,'x':kw['x'],'z':kw['z'],'downed':'False','dead':'False',
                              'prisoner':'False','kept':'False','food':'0.1','rest':'0.8','inBed':'False'}
            return {'success':True,'pawns':[{'id':pid}]}
        if tool == 'jawa/pawn_force_incapacitate': self.pawns[kw['pawn']]['downed'] = 'True'
        if tool == 'jawa/pawn_need': self.pawns[kw['pawn']]['food'] = str(kw['level'])
        if tool == 'jawa/pawn_health': self.pawns[kw['pawn']]['downed'] = 'False'
        if tool == 'jawa/ordered_job':
            p = self.pawns[kw['targetAId']]
            enabled = self.settings['superdeepRoomsEnabled']
            capture = (enabled and self.fault != 'no_capture') or self.fault == 'off_captures'
            if kw['jobDef'] == 'Capture': capture = True; p['inBed'] = 'True'
            if capture: p['prisoner'] = p['kept'] = 'True'
            if self.fault == 'remote_warp' and self.beds: p['x'] = 49; p['kept'] = 'False'
        if tool == 'jawa/build_batch': self.beds.append({'id':'bed'})
        if tool == 'jawa/list_things': return {'success':True,'things':self.beds}
        return {'success':True}


def check(fault=None, abort=False, occupied=False):
    B = Bridge(fault)
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
    assert failed == bool(fault or abort), (fault, failed, rec)
    assert B.snapshot_calls == 1 and B.loads == 2, (fault, B.loads)
    assert all(B.settings[k] == v for k,v in B.original.items()), (fault, B.settings)
    assert not B.pawns, (fault, B.pawns)
    assert rec['restore']['status'] == ('FAIL' if fault == 'bad_snapshot' else 'PASS')
    print('ok', fault or ('injected_abort' if abort else 'complete_scene'))

for f in (None, 'no_capture', 'off_captures', 'remote_warp', 'no_feed', 'escape', 'wet', 'bad_snapshot'):
    check(f)
check(abort=True)
check(occupied=True)
check('lost_occupied', occupied=True)
# Also compile/run the actual Verse-free production logic, only these three cases.
root = HERE.parents[3]
subprocess.run([sys.executable, str(root/'src/RimMandrake/Utils/selftest_flowworks_stock.py'),
                '--only', 'PitRoom_*'], check=True)
print('PASS: fault controls, abort cleanup and selected C# pit-room cases')
