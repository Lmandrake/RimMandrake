#!/usr/bin/env python3
"""Bedless prison acceptance. Load an existing disposable calm save: NEVER worldgen.

python.exe <this clone>/src/RimMandrake/FlowWorks/northstar/concept_scenes.py --out <json>

A whole-game scene-begin save is the snapshot: reload it in finally, then compare
terrain/underterrain/roof, exact liquid and things in the scene rectangle. Settings
are statics, so separately read every changed value and restore the prior value.
D4 is the historical absolute-rule pit; the second run uses the shipped relative
geometry and its 3 m minimum. Neither depth/height rule is relaxed in production.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
for p in (ROOT / 'src/RimMandrake/Utils', ROOT / 'src/RimMandrake/Utils/modcheck'):
    sys.path.insert(0, str(p))
PROOF = 'RimMandrake.FlowWorks.RM_PitPrisonProof'
ROOMS = 'RimMandrake.FlowWorks.RM_PitRooms'
SETTINGS = 'RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings'
RECT = '30,30,24,18'
PIT = [(38, z) for z in range(35, 41)]


def kv(s):
    return dict(x.split('=', 1) for x in str(s).split() if '=' in x)


def require(ok, why):
    if not ok:
        raise AssertionError(why)


def scene_hole_prison(B, snapshot, reload_snapshot, receipt, *, relative=True, abort=False,
                      save_occupied=None, load_occupied=None, expected_sha256=None):
    """Run with an injected bridge/save transport; receipts retain every raw readout.

    Capture jobs use the player job, care jobs come from registered vanilla work
    givers. Only initial hunger is written. Every subsequent food gain is ingestion.
    The day uses real ticks, never time_set_ticks. Finally runs even on an assertion.
    """
    prior = {}
    calls = receipt.setdefault('calls', [])

    def call(tool, allow_refusal=False, **kw):
        r = B.call(tool, **kw)
        calls.append({'tool': tool, 'args': kw, 'result': r})
        if isinstance(r, dict):
            require(allow_refusal or r.get('success') is not False, '%s refused: %s' % (tool, r))
        return r

    def sc(method, arg='', typ=PROOF):
        r = call('jawa/static_call', type=typ, method=method, args=arg)
        require('result' in r, 'no static result: %s' % r)
        return str(r['result'])

    def setting(name, value):
        if name not in prior:
            r = call('jawa/mod_settings_field', typeName=SETTINGS, field=name, action='get')
            require('value' in r, 'unreadable prior setting '+name)
            prior[name] = r['value']
        call('jawa/mod_settings_field', typeName=SETTINGS, field=name, action='set', value=str(value))
        got = call('jawa/mod_settings_field', typeName=SETTINGS, field=name, action='get')['value']
        require(str(got).lower() == str(value).lower(), 'setting did not stick: '+name)

    def state(pid):
        return kv(sc('State', pid))

    def step(n):
        before = clock()
        B.ticks(n)
        after = clock()
        require(after-before == n, 'real tick delta %s != %s' % (after-before, n))

    def clock():
        r = call('jawa/site_state')
        require(r.get('ticksGame') is not None, 'site_state has no tick clock')
        return int(r['ticksGame'])

    def spawn(kind, at, faction):
        r = call('jawa/spawn_pawn', kindDef=kind, x=at[0], z=at[1], faction=faction, count=1,
                 xenotype='Baseliner')
        ids = [p['id'] for p in r.get('pawns', [])]
        require(len(ids) == 1, 'spawn failed: %s' % r)
        return ids[0]

    def care(worker, pid, mode, start=False):
        r = kv(sc('Care', ';'.join((worker, pid, mode, 'start' if start else 'ask'))))
        if start and r.get('job') != 'none':
            require(r.get('ordered') == 'True', 'care job was not accepted: '+str(r))
        return r

    receipt['relative'] = relative
    # static_call treats an empty args string as ZERO parameters, not one empty string.
    receipt['identity'] = sc('Identity', 'probe')
    if expected_sha256 is not None:
        require(kv(receipt['identity']).get('sha256') == expected_sha256, 'loaded DLL differs from this clone')
        receipt['expected_sha256'] = expected_sha256
    saved = False
    try:
        receipt['snapshot'] = snapshot()
        saved = True
        reload_snapshot()
        receipt['before'] = sc('Rect', RECT)
        # Every map/setting change follows the snapshot. A failure anywhere restores it.
        for name, value in [('superdeepRoomsEnabled', True), ('captureDownEnabled', True),
                            ('wardenFromLipEnabled', True), ('superdeepCaptureEnabled', True),
                            ('pitRelativeClimbEnabled', relative), ('maxDigDepth', 8),
                            ('rainFillsExcavationsEnabled', False)]:
            setting(name, value)
        call('jawa/destroy_batch', rects=RECT, categories='All')
        sc('ProofResetRect', '30;30;24;18', 'RimMandrake.FlowWorks.RM_NorthstarProofs')
        call('jawa/set_terrain_batch', ops='Soil:'+RECT)
        depth = 6 if relative else 4
        for x, z in PIT:
            call('jawa/flowworks_excavation_drive', x=x, z=z, deepenLevels=depth, setFill=0)
        sc('RebuildAllMaps', typ=ROOMS)
        call('jawa/map_commit')
        # Read each cell's real D/F; no bed anywhere in the scene until the remote-bed phase.
        receipt['start_rect'] = sc('Rect', RECT)
        require(kv(receipt['start_rect'])['beds'] == '0', 'a hidden bed exists in the scene')
        receipt['depth'] = depth
        receipt['cells'] = [call('jawa/flowworks_excavation_report', x=x, z=z) for x, z in PIT]
        require(all(c.get('depth') == depth and c.get('fill') == 0 and c.get('isExcavated') is True
                    for c in receipt['cells']), 'pit is not dug and drained at the asserted depth')
        original_pawns = [p['id'] for p in call('jawa/list_pawns', limit=1000)['pawns']]
        raiders = [spawn('Pirate', PIT[i], 'hostile') for i in (1, 4)]
        # SITE: generated backstories can disable Warden/Doctor. Prove capability
        # before accepting a fixture, without rewriting a pawn's life history.
        receipt['worker_candidates'] = []
        wardens = []
        for z in (36, 39):
            for _ in range(6):
                w = spawn('Colonist', (35, z), 'player')
                call('jawa/set_draft', pawnId=w, drafted=True)
                checks = []
                for wt in ('Warden', 'Doctor', 'Patient', 'PatientBedRest'):
                    r = call('jawa/set_work_priority', allow_refusal=True,
                             pawnId=w, workType=wt, priority=1)
                    require(r.get('success') is True or
                            'disabledWorkTypes' in (r.get('details') or {}),
                            'work capability probe failed: '+str(r))
                    checks.append({'workType': wt, 'result': r})
                receipt['worker_candidates'].append({'pawn': w, 'checks': checks})
                if all(c['result'].get('success') is True and
                       int(c['result'].get('readBack', 0)) > 0 for c in checks):
                    wardens.append(w)
                    break
                call('jawa/pawn_force_incapacitate', pawn=w, action='vanish')
            else:
                raise AssertionError('UNMEASURED SITE: no capable warden/doctor in six generated candidates')
        for p in original_pawns:
            call('jawa/pawn_force_incapacitate', pawn=p, action='vanish')
        for w in wardens:
            call('jawa/set_draft', pawnId=w, drafted=True)
            for wt in ('Warden', 'Doctor', 'Patient', 'PatientBedRest'):
                call('jawa/set_work_priority', pawnId=w, workType=wt, priority=1)
        for p in raiders:
            call('jawa/pawn_gear', pawn=p, action='clear')
            call('jawa/pawn_force_incapacitate', pawn=p, action='downed', allowBleedingWounds=False)
            require(state(p)['downed'] == 'True', 'raider not downed')
            call('jawa/pawn_need', pawn=p, action='need', need='Food', level=0.1)
        # Ready-to-eat food outside the hole, selected by ordinary work givers.
        call('jawa/spawn_batch', ops=';'.join('MealSurvivalPack:34,%d,10' % z for z in (34, 35, 36)))
        receipt['food_supply'] = call('jawa/list_things', defName='MealSurvivalPack', rect=RECT, limit=1000)
        require(sum(int(t.get('stackCount', 0)) for t in receipt['food_supply'].get('things', [])) >= 24,
                'UNMEASURED SITE: insufficient read-back meal supply')
        receipt['starting'] = [state(p) for p in raiders]
        receipt['disabled'] = []
        setting('superdeepRoomsEnabled', False)
        sc('RebuildAllMaps', typ=ROOMS)
        for w, p in zip(wardens, raiders):
            v = sc('ProofCaptureDown', p, 'RimMandrake.FlowWorks.RM_NorthstarProofs')
            require(v.startswith('VERDICT SettingOff'), 'bedless OFF accepted: '+v)
            order = call('jawa/ordered_job', allow_refusal=True, pawnId=w, jobDef='RM_CaptureDown', targetAId=p,
                         targetBX=37, targetBZ=int(state(p)['z']))
            require(order.get('accepted') is True and order.get('requestedJobDef') == 'RM_CaptureDown',
                    'OFF control never attempted the requested capture: '+str(order))
        step(300)
        receipt['disabled'] = [state(p) for p in raiders]
        require(all(s['prisoner'] == 'False' for s in receipt['disabled']), 'OFF job captured a raider')
        setting('superdeepRoomsEnabled', True)
        sc('RebuildAllMaps', typ=ROOMS)
        # First capture: zero beds. Second: remote bed exists, so it cannot mask a relocation.
        for i, (w, p) in enumerate(zip(wardens, raiders)):
            if i:
                walls = [(x, z) for x in range(47, 52) for z in range(37, 42)
                         if x in (47, 51) or z in (37, 41)]
                ops = ';'.join(('Door' if (x, z) == (47, 39) else 'Wall')+':%d,%d' % (x, z)
                               for x, z in walls)
                call('jawa/build_batch', ops=ops+';Bed:49,39,0', stuff='WoodLog', faction='player')
                beds = call('jawa/list_things', defName='Bed', rect=RECT, limit=20)['things']
                require(len(beds) == 1, 'remote bed census differs')
                call('jawa/set_bed_owner_type', thing=beds[0]['id'], ownerType='Prisoner')
                sc('RebuildAllMaps', typ=ROOMS)
            verdict = sc('ProofCaptureDown', p, 'RimMandrake.FlowWorks.RM_NorthstarProofs')
            require(verdict.startswith('VERDICT Allowed'), 'ON capture refused: '+verdict)
            call('jawa/ordered_job', pawnId=w, jobDef='RM_CaptureDown', targetAId=p,
                 targetBX=37, targetBZ=int(state(p)['z']))
            step(900)
            s = state(p)
            require(s['prisoner'] == 'True' and s['kept'] == 'True', 'capture did not keep pawn in pit: '+str(s))
            require((int(state(w)['x']), int(state(w)['z'])) not in PIT, 'captor entered pit')
        receipt['captured'] = [state(p) for p in raiders]
        if abort:
            raise RuntimeError('injected abort after capture, before care')
        receipt['feeding'] = []
        for w, p in zip(wardens, raiders):
            # An available remote bed must not induce an ordinary warden transfer.
            require(care(w, p, 'bed')['job'] == 'none', 'warden wants to carry pit prisoner out')
            s0 = state(p)
            mode = 'feed' if s0['downed'] == 'True' else 'deliver'
            job = care(w, p, mode, True)
            require(job['job'] in ('FeedPatient', 'DeliverFood'), 'ordinary food work giver refused: '+str(job))
            step(2400)
            s1 = state(p)
            require(float(s1['food']) > float(s0['food']) + 0.2, 'no ingestion after ordinary feeding')
            receipt['feeding'].append({'before': s0, 'workgiver': job, 'after': s1, 'worker': state(w)})
        receipt['tending'] = []
        for w, p in zip(wardens, raiders):
            s0 = state(p)
            if s0['downed'] == 'True' and int(s0.get('tendable', 0)) > 0:
                job = care(w, p, 'tend', True)
                require(job['job'] == 'TendPatient', 'ordinary doctor refuses bedless tending')
                step(3000)
                s1 = state(p)
                require(int(s1['tended']) > int(s0['tended']), 'no wound tended by doctor')
                receipt['tending'].append({'before': s0, 'after': s1, 'workgiver': job})
        for w in wardens:
            call('jawa/set_draft', pawnId=w, drafted=False)
        # BROADEN (Opus): recomputed room/guest state after a save while occupied.
        if save_occupied is not None:
            receipt['occupied_save'] = save_occupied()
            load_occupied()
            step(2500)
            receipt['occupied_reload'] = [state(p) for p in raiders]
            require(all(s['kept'] == 'True' for s in receipt['occupied_reload']),
                    'occupied save reload lost the bedless prison')
            require(all(care(w, p, 'bed')['job'] == 'none' for w,p in zip(wardens,raiders)),
                    'reload offers a remote bed transfer')
        # Real day of normal work. Observe at intervals, no need refills or healing.
        start = clock()
        receipt['day'] = []
        for _ in range(24):
            step(2500)
            states = [state(p) for p in raiders]
            for s in states:
                require(s['kept'] == 'True' and s['dead'] == 'False', 'prisoner escaped or died: '+str(s))
                require((int(s['x']), int(s['z'])) in PIT, 'prisoner moved out of hole')
                require(float(s['food']) > 0, 'prisoner starved')
            receipt['day'].append({'tick': clock(), 'prisoners': states})
        receipt['day_ticks'] = clock()-start
        # BROADEN (Opus): a prison must also work once its inmate can stand. If the
        # captured injuries have not healed in a day, heal ONE fixture for this
        # separate transition probe; do not count that as natural recovery.
        awake = raiders[0]
        receipt['awake_transition'] = {'before': state(awake), 'fixture_healed': False}
        if state(awake)['downed'] == 'True':
            call('jawa/pawn_health', pawn=awake, action='healAll', confirmDestructive=True)
            receipt['awake_transition']['fixture_healed'] = True
        # Hungry again ONCE at the start of this distinct self-feeding probe.
        for w in wardens:
            call('jawa/set_draft', pawnId=w, drafted=True)
        for x,z in PIT:
            call('jawa/destroy_batch', rects='%d,%d,1,1' % (x,z), categories='Item')
        call('jawa/pawn_need', pawn=awake, action='need', need='Food', level=0.1)
        require(state(awake)['downed'] == 'False', 'awake probe never stood up')
        job = care(wardens[0], awake, 'deliver', True)
        require(job['job'] == 'DeliverFood', 'awake prisoner gets no ordinary meal delivery')
        step(3000)
        s = state(awake)
        require(float(s['food']) > 0.3 and s['kept'] == 'True', 'awake prisoner failed to eat delivered meal')
        require(care(wardens[0], awake, 'bed')['job'] == 'none', 'awake prisoner gets remote bed transfer')
        receipt['awake_transition'].update({'after': s, 'workgiver': job})
        for w in wardens:
            call('jawa/set_draft', pawnId=w, drafted=False)
        require(receipt['day_ticks'] >= 60000, 'less than one day simulated')
        # Ordinary bed prison still functions with pit rooms OFF (remote ground bed).
        setting('superdeepRoomsEnabled', False)
        sc('RebuildAllMaps', typ=ROOMS)
        ordinary = spawn('Pirate', (46, 39), 'hostile')
        call('jawa/pawn_gear', pawn=ordinary, action='clear')
        call('jawa/pawn_force_incapacitate', pawn=ordinary, action='downed', allowBleedingWounds=False)
        call('jawa/ordered_job', pawnId=wardens[0], jobDef='Capture', targetAId=ordinary,
             targetBId=beds[0]['id'])
        step(2400)
        receipt['ordinary_off'] = state(ordinary)
        require(receipt['ordinary_off']['prisoner'] == 'True' and receipt['ordinary_off']['inBed'] == 'True',
                'ordinary bed capture broken with pit rooms OFF')
        receipt['behavior'] = 'PASS'
    finally:
        receipt['restore'] = {'settings': {}, 'errors': []}
        errors = receipt['restore']['errors']
        if saved:
            try:
                reload_snapshot()
                receipt['restore']['rect'] = sc('Rect', RECT)
                require(receipt['restore']['rect'] == receipt.get('before'),
                        'snapshot terrain/liquid/things differ after reload')
            except Exception as e:
                errors.append(repr(e))
        # A failed reload/fingerprint must NEVER skip the remaining static restores.
        for name, value in prior.items():
            try:
                call('jawa/mod_settings_field', typeName=SETTINGS, field=name, action='set', value=str(value))
                got = call('jawa/mod_settings_field', typeName=SETTINGS, field=name, action='get')['value']
                receipt['restore']['settings'][name] = {'before': value, 'after': got}
                require(str(got).lower() == str(value).lower(), 'setting not restored: '+name)
            except Exception as e:
                errors.append(repr(e))
        try:
            sc('RebuildAllMaps', typ=ROOMS)
        except Exception as e:
            errors.append(repr(e))
        receipt['restore']['status'] = 'FAIL' if errors else 'PASS'
        require(not errors, 'restore failed: '+str(errors))



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--absolute', action='store_true')
    ap.add_argument('--abort', action='store_true')
    a = ap.parse_args()
    import validation_core as V
    import test_site_saves as T
    from game_paths import SAVES
    B = V.Bridge()
    res = {'script': __file__, 'started': time.time(), 'mode': 'live', 'calls': []}
    name = 'WHITTLE_HolePrison_Begin_' + time.strftime('%Y%m%dT%H%M%S')
    try:
        loaded = T.load_site(B.call, 'calm')
        res['site'] = loaded
        require(loaded['verified'], 'disposable calm site failed to load: '+str(loaded))
        # A guarded save verifies a new file appeared and no old slot changed.
        def snapshot():
            return T.save_site(B.call, name, SAVES)
        def reload_snapshot():
            r = T.load_site(B.call, 'calm', name=name, check=False)
            require(r['verified'], 'snapshot reload failed: '+str(r))
        occupied = name + '_Occupied'
        def save_occupied():
            return T.save_site(B.call, occupied, SAVES)
        def load_occupied():
            r = T.load_site(B.call, 'calm', name=occupied, check=False)
            require(r['verified'], 'occupied reload failed: '+str(r))
        scene_hole_prison(B, snapshot, reload_snapshot, res, relative=not a.absolute, abort=a.abort,
                          save_occupied=save_occupied, load_occupied=load_occupied,
                          expected_sha256=hashlib.sha256((HERE.parent/'Assemblies/RimMandrakeFlowWorks.dll').read_bytes()).hexdigest())
        res['status'] = 'PASS'
    except Exception as e:
        res['status'], res['error'] = 'FAIL', repr(e)
    finally:
        res['finished'] = time.time()
        Path(a.out).write_text(json.dumps(res, indent=2, default=str), encoding='utf-8')
        print(res['status'], a.out, res.get('error', ''), flush=True)
    return 0 if res['status'] == 'PASS' else 1

if __name__ == '__main__':
    sys.exit(main())
