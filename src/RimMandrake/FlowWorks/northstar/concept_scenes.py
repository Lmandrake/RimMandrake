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
import clockgate as CG

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
    prior_debug = {}
    fixtures = []
    fixture_baseline = set(CG.FIXTURE_IDS)
    stops_begin = len(CG.BENIGN_STOPS)
    receipt['fixture_declarations'] = fixtures
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

    def quiet_controls():
        # The existing isolated-mechanism profile's debug flags; preserve their
        # pre-run values across reloads. No needs, damage or governor stop is bypassed.
        fields = ('enableStoryteller', 'enableRandomMentalStates', 'enableRandomDiseases')
        receipt['isolation_controls'] = list(fields)
        for name in fields:
            if name not in prior_debug:
                values = {x['name']: x['value'] for x in call('jawa/debug_settings', action='list').get('fields', [])}
                require(name in values, 'unreadable prior debug field '+name)
                prior_debug[name] = values[name]
            r = call('jawa/debug_settings', action='set', field=name, value=False)
            require(r.get('valueAfter') is False, 'quiet debug field did not stick: '+name)

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
        if faction == 'hostile':
            # Only the arrival of these exact staged subjects is expected.
            # Injury, death, a real raid and every other governor stop remain active.
            number = CG.declare_fixture(ids[0])
            if number not in fixture_baseline:
                fixtures.append(ids[0])
        return ids[0]

    def care(worker, pid, mode, start=False):
        if start:
            call('jawa/stop_job', pawnId=worker, mode='stopall')
        r = kv(sc('Care', ';'.join((worker, pid, mode, 'start' if start else 'ask'))))
        if start and r.get('job') != 'none':
            require(r.get('ordered') == 'True', 'care job was not accepted: '+str(r))
            require(state(worker).get('job') == r['job'], 'care job was queued rather than started: '+str(r))
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
        quiet_controls()
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
            call('jawa/flowworks_excavation_drive', x=x, z=z, deepenLevels=depth, setBodyWaterM=0.0)
        sc('RebuildAllMaps', typ=ROOMS)
        call('jawa/map_commit')
        # Read each cell's real D/F; no bed anywhere in the scene until the remote-bed phase.
        receipt['start_rect'] = sc('Rect', RECT)
        require(kv(receipt['start_rect'])['beds'] == '0', 'a hidden bed exists in the scene')
        receipt['depth'] = depth
        receipt['cells'] = [call('jawa/flowworks_excavation_report', x=x, z=z) for x, z in PIT]
        require(all(c.get('depth') == depth and c.get('waterDl') == 0 and c.get('isExcavated') is True
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
            receipt['occupied_load'] = load_occupied()
            quiet_controls()
            step(2500)
            receipt['occupied_reload'] = [state(p) for p in raiders]
            require(all(s['kept'] == 'True' for s in receipt['occupied_reload']),
                    'occupied save reload lost the bedless prison')
            require(all(care(w, p, 'bed')['job'] == 'none' for w,p in zip(wardens,raiders)),
                    'reload offers a remote bed transfer')
        # BROADEN (Opus): a prison must also work once its inmate can stand. If the
        # captured injuries have not healed in a day, heal ONE fixture for this
        # separate transition probe; do not count that as natural recovery.
        # RULED OUT: delivery path failure. The meal reached the pit in both
        # diagnostic arms; a rested inmate ate, while an exhausted inmate slept
        # beside it. Run this awake probe BEFORE the day, with no Rest refill.
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
        require(float(state(awake)['rest']) > 0.3, 'UNMEASURED SITE: upright-feeding subject is exhausted')
        job = care(wardens[0], awake, 'deliver', True)
        require(job['job'] == 'DeliverFood', 'awake prisoner gets no ordinary meal delivery')
        step(3000)
        s = state(awake)
        require(float(s['food']) > 0.3 and s['kept'] == 'True', 'awake prisoner failed to eat delivered meal')
        require(care(wardens[0], awake, 'bed')['job'] == 'none', 'awake prisoner gets remote bed transfer')
        receipt['awake_transition'].update({'after': s, 'workgiver': job})
        for w in wardens:
            call('jawa/set_draft', pawnId=w, drafted=False)
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
        receipt['restore']['debug'] = {}
        for name, value in prior_debug.items():
            try:
                r = call('jawa/debug_settings', action='set', field=name, value=value)
                receipt['restore']['debug'][name] = {'before': value, 'after': r.get('valueAfter')}
                require(r.get('valueAfter') is value, 'debug field not restored: '+name)
            except Exception as e:
                errors.append(repr(e))
        try:
            sc('RebuildAllMaps', typ=ROOMS)
        except Exception as e:
            errors.append(repr(e))
        receipt['governor_resumes'] = list(CG.BENIGN_STOPS[stops_begin:])
        for pid in fixtures:
            CG.withdraw_fixture(pid)
        receipt['restore']['status'] = 'FAIL' if errors else 'PASS'
        require(not errors, 'restore failed: '+str(errors))



# =====================================================================================================================
# Stage 3 scene entries (FlowWorks 0.1.0 Maturation Stage 3 "reconcile", 2026-11-14). One function per in-game test of
# design/concepts/FlowWorks/version/test_table.json, from the scene's start / action / expect / control in
# design/concepts/FlowWorks/scenes.json (sc_geyser_tub and sc_coating_wash from the two bars his card added 2026-11-14).
# Status: WRITTEN, IMPORT-CHECKED AND LINT-CHECKED (every bridge call literal and in the tool schema), NEVER RUN. They run
# in Stage 6:  python.exe concept_scenes.py --scene <scene_name> --out <json>   (bridge held; minimal list + FlowWorks,
# except scene_walk_moat_season, which is the full list). Stage 6 owns the coordinates (one dense prepared map) and the
# first-run harness repairs. A row reads PASS, FAIL (MOD), or UNMEASURED (HARNESS: a read came back without the field);
# a hook the mod does not have yet (wetting probe, toss-flame order, raider fetch, coating condition) is a FAIL by design:
# those scenes are red until their behaviour is built. UNVERIFIED argument shapes, for Stage 6's first run to settle:
# list_things / list_pawns / inspect_string `rect` strings, set_plants `ops`, set_terrain_batch `ops`, and the verbs after
# ';' passed to ProofCover, ProofDrainGate and ProofStageBasin (their read forms are documented in the C#; the verbs are not).
# =====================================================================================================================
EXC = 'RimMandrake.FlowWorks.RM_PromotionProofs'
NSP = 'RimMandrake.FlowWorks.RM_NorthstarProofs'
FLUIDID = 'RimMandrake.FlowWorks.RM_FluidIdentityProof'
WATER, TAR, FUEL, OIL = 'RM_Fluid_Water', 'RM_Fluid_Tar', 'RM_Fluid_Chemfuel', 'RM_Fluid_Oil'
O = (60, 60)  # scene origin on the prepared map; Stage 6 moves it to the dense map's free block


class _Stage:
    """The shared half of every Stage 3 scene: recorded calls, settings restored, real ticks, rows, restore in finally."""

    def __init__(self, B, receipt, name):
        self.B, self.r, self.prior = B, receipt, {}
        receipt.update({'scene': name, 'rows': [], 'calls': receipt.get('calls', [])})
        self.reload = None

    def again(self):
        """Back to the scene-begin snapshot for the control case (settings stay as poked; restored at the end)."""
        self.reload()

    # an order the game may refuse is a reading (the row decides), not a staging fault
    SOFT = ('jawa/order_pawn', 'jawa/flowworks_job_probe', 'jawa/ordered_job')

    def call(self, tool, **kw):
        r = self.B.call(tool, **kw)
        self.r['calls'].append({'tool': tool, 'args': kw, 'result': r})
        if isinstance(r, dict):
            require(tool in self.SOFT or r.get('success') is not False, '%s refused: %s' % (tool, r))
        return r

    def sc(self, typ, method, arg=''):
        r = self.B.call('jawa/static_call', type=typ, method=method, args=arg)
        self.r['calls'].append({'tool': 'jawa/static_call', 'args': [typ, method, arg], 'result': r})
        return str((r or {}).get('result', 'REFUSED: no result %s' % r))

    def setting(self, name, value, typ=SETTINGS):
        if (typ, name) not in self.prior:
            self.prior[(typ, name)] = self.B.call('jawa/mod_settings_field', typeName=typ, field=name, action='get').get('value')
        self.B.call('jawa/mod_settings_field', typeName=typ, field=name, action='set', value=str(value))

    def restore_settings(self):
        for (typ, name), v in self.prior.items():
            self.B.call('jawa/mod_settings_field', typeName=typ, field=name, action='set', value=str(v))

    def ticks(self, n):
        # governed chunks (jawa/safe_advance, many ticks a frame); step_game_ticks ran one tick a frame (Stage 6 visit 1)
        self.B.ticks(n)

    def pulse(self, n):
        self.B.call('jawa/flowworks_pulse', count=n, x=0, z=0, w=0, h=0, includeBodies=False)

    def dig(self, cells, levels, water_m=-1):
        for c in cells:
            self.call('jawa/flowworks_excavation_drive', x=c[0], z=c[1], deepenLevels=levels, setBodyWaterM=water_m)

    def fill(self, cells, metres, fluid):
        for c in cells:
            txt = self.sc(FLUIDID, 'ProofFillWithFluid', '%d,%d,%g,%s' % (c[0], c[1], metres, fluid))
            require(txt.startswith('FILLED'), 'fill %s with %s: %s' % (c, fluid, txt))

    def cells(self, cells):
        xs, zs = [c[0] for c in cells], [c[1] for c in cells]
        r = self.call('jawa/flowworks_excavation_rect', x=min(xs), z=min(zs), w=max(xs) - min(xs) + 1, h=max(zs) - min(zs) + 1)
        m = {(q['x'], q['z']): q for q in r.get('rows') or []}
        return [m.get(c, {}) for c in cells]

    def dl(self, cells):
        return [q.get('dl') for q in self.cells(cells)]

    def pawn(self, kind, at, faction):
        r = self.call('jawa/spawn_pawn', kindDef=kind, x=at[0], z=at[1], faction=faction, count=1, xenotype='Baseliner')
        ids = [p['id'] for p in r.get('pawns', [])]
        require(len(ids) == 1, 'spawn failed: %s' % r)
        return ids[0]

    def walk(self, pid, at, wait=1500):
        return self.call('jawa/order_pawn', pawnId=pid, x=at[0], z=at[1], waitTicks=wait, draft=True)

    def shot(self, tag, at, w=12, h=12):
        self.B.call('rimworld/screenshot_cell_rect', x=at[0], z=at[1], width=w, height=h, fileName='%s_%s' % (self.r['scene'], tag),
                    suppressMessage=True)

    def row(self, rid, ok, detail, unmeasured=False):
        self.r['rows'].append({'id': rid, 'status': 'UNMEASURED' if unmeasured else ('PASS' if ok else 'FAIL'),
                               'kind': 'HARNESS' if unmeasured else 'MOD', 'detail': str(detail)[:400]})

    def done(self):
        self.r['status'] = 'PASS' if self.r['rows'] and all(x['status'] == 'PASS' for x in self.r['rows']) else 'FAIL'
        return self.r


def _line(x, z, n, dx=1, dz=0):
    return [(x + i * dx, z + i * dz) for i in range(n)]


def _run(name, body):
    """Every scene: snapshot, body(stage), restore (settings, then the snapshot reload) even on an assertion."""
    def scene(B, snapshot, reload_snapshot, receipt):
        S = _Stage(B, receipt, name)
        S.reload = reload_snapshot
        snapshot()
        try:
            body(S)
        except AssertionError as e:
            S.row(name + '_staging', False, repr(e), unmeasured=True)
        finally:
            S.restore_settings()
            reload_snapshot()
        return S.done()
    scene.__name__ = name
    return scene


def _fill_front(S):
    a, b = _line(O[0], O[1], 12), _line(O[0], O[1] + 4, 12)
    S.dig(a + b, 4)                                            # D2 = four half-metre notches
    S.row('FF_start_dry', all(v in (0, None) for v in S.dl(a + b)) and None not in S.dl(a + b), S.dl(a + b))
    seen = []
    S.dig([(O[0] - 1, O[1]), (O[0] - 1, O[1] + 4)], 4)          # the head cell is dug too: a fill needs an excavated cell
    S.fill([(O[0] - 1, O[1])], 2.0, WATER); S.fill([(O[0] - 1, O[1] + 4)], 2.0, TAR)
    for _ in range(12):
        S.pulse(1); seen.append((S.dl(a), S.dl(b)))
    front = [sum(1 for v in w if v) for w, _ in seen], [sum(1 for v in t if v) for _, t in seen]
    S.row('FF_front_cell_by_cell', all(y - x <= 2 for x, y in zip(front[0], front[0][1:])) and front[0][-1] == 12, front[0])
    S.row('FF_tar_behind_water', all(t <= w for w, t in zip(*front)), front)
    banks = S.dl(_line(O[0], O[1] + 1, 12) + _line(O[0], O[1] + 3, 12))
    S.row('FF_banks_dry', all(not v for v in banks), banks)
    S.shot('front', O, 14, 6)


def _one_surface(S):
    canal = _line(O[0], O[1], 10)
    pit = [(O[0] + 10 + i, O[1] + j) for i in range(3) for j in range(-1, 2)]
    S.dig(canal, 2); S.dig(pit, 8)
    # Stage 6 visit 1: one head cell of 1.5 m drained whole into the 4 m pit and left the canal dry, so the canal and the
    # pit are filled at two different heights instead and must settle to ONE surface. ProofLevelSurface prints
    # "OK <bodies> worst <gap> m;x,z:squares:gap:min:max;..." (it never printed spread=/ok=, which the draft parsed).
    S.fill(canal, 0.8, WATER); S.fill(pit, 3.0, WATER)
    S.pulse(30); S.ticks(5000)                                 # two game hours
    lv = S.sc(NSP, 'ProofLevelSurface', '%d,%d,%d,%d' % (O[0], O[1] - 1, 13, 3))
    head = lv.split(';')[0].split()
    body = (lv.split(';') + ['', ''])[1].split(':')
    one = len(head) >= 4 and head[0] == 'OK' and head[1] == '1' and float(head[3]) <= 0.01
    S.row('ONE_level_every_cell', one and len(body) >= 2 and body[1].isdigit() and int(body[1]) >= len(canal) + len(pit), lv)
    S.call('jawa/spawn_batch', ops='RM_Sluice:%d,%d' % (O[0] + 5, O[1]))
    S.fill(canal[:4], 1.0, WATER)
    S.pulse(30)
    S.row('ONE_control_sluice_splits', len(set(S.dl(canal[:4]) + S.dl(canal[6:]))) > 1, (S.dl(canal[:4]), S.dl(canal[6:])))


def _source_pays(S):
    pond = [(O[0] + i, O[1] + j) for i in range(20) for j in range(10)]
    moat = _line(O[0], O[1] + 12, 60)
    before = S.sc(NSP, 'ProofReadout', '%d,%d' % (O[0] + 10, O[1] + 5))
    S.dig(moat, 4); S.pulse(60)
    after = S.sc(NSP, 'ProofReadout', '%d,%d' % (O[0] + 10, O[1] + 5))
    S.row('SRC_pond_drops', before != after, (before, after))
    S.call('jawa/spawn_batch', ops='RM_FlowSink:%d,%d' % (O[0] + 19, O[1] + 9))
    S.pulse(200)
    S.row('SRC_flow_stops_when_empty', all(not v for v in S.dl(pond[:20])), S.dl(pond[:20]))
    S.call('jawa/weather_set', weather='Rain', lockWeather=True)
    S.ticks(5 * 60000)
    S.row('SRC_refill_visible', any(S.dl(pond)), S.sc(NSP, 'ProofReadout', '%d,%d' % (O[0] + 10, O[1] + 5)))
    S.call('jawa/weather_set', unlock=True)
    lake = S.sc(NSP, 'ProofReadout', '%d,%d' % (O[0] + 70, O[1]))
    S.row('SRC_lake_reads_endless', 'ndless' in lake, lake)


def _pawn_height(S):
    pads = _line(O[0], O[1], 17)
    for i, c in enumerate(pads):
        S.dig([c], i)
    col = S.pawn('Colonist', (O[0] - 2, O[1]), 'player')
    got = []
    for i, c in enumerate(pads):
        S.walk(col, c, 400); got.append(kv(S.sc(EXC, 'ProofPawnSink', col)).get('sink'))
    S.row('PH_offset_follows_depth', all(g is not None for g in got) and [float(g) for g in got] == sorted(float(g) for g in got), got)
    S.fill(pads[1:], 2.0, WATER); S.walk(col, pads[-1], 1500)   # pads[0] is undug ground: a fill needs an excavated cell
    sw = S.sc(NSP, 'ProofReadout', '%d,%d' % pads[-1])
    S.row('PH_swims_and_tires_at_2m', 'swim' in sw.lower(), sw)
    S.walk(col, (O[0], O[1] - 3), 400)
    ctl = kv(S.sc(EXC, 'ProofPawnSink', col)).get('sink')
    S.row('PH_control_undug_no_offset', ctl is not None and abs(float(ctl)) < 1e-3, ctl)


def _hose_look(S):
    S.call('jawa/spawn_batch', ops='RM_LiquidPump:%d,%d' % O)
    S.call('jawa/spawn_batch', ops='RM_HoseReel:%d,%d' % (O[0] + 10, O[1]))
    on = S.sc(NSP, 'ProofPump', '%d,%d' % O)
    S.shot('flowing', O, 14, 6)
    S.row('HOSE_plump_when_flowing', 'running=True' in on, on)
    S.call('jawa/static_call', type=NSP, method='ProofPump', args='%d,%d;draw' % O)
    S.shot('stopped', O, 14, 6)
    off = S.sc(NSP, 'ProofPump', '%d,%d' % O)
    S.row('HOSE_flat_when_not', 'running=False' in off, off)


def _trench_cover(S):
    trench = _line(O[0], O[1], 6); pit = [(O[0] + 8 + i, O[1] + j) for i in range(2) for j in range(2)]
    S.dig(trench, 4); S.dig(pit, 8)
    col = S.pawn('Colonist', trench[2], 'player')
    S.call('jawa/fire_raid', points=400, dryRun=False, strategy='ImmediateAttack')
    S.ticks(2500)
    cov = S.sc(EXC, 'ProofCover', '%d,%d' % trench[2])
    S.row('TR_trench_pawn_covered', 'covered=True' in cov, cov)
    inpit = S.call('jawa/list_pawns', faction='hostile', rect='%d,%d,2,2' % pit[0])
    S.row('TR_no_raider_shelters_in_pit', not inpit.get('pawns'), inpit.get('pawns'))
    S.walk(col, (O[0], O[1] + 4), 300)
    S.row('TR_control_open_ground_no_cover', 'covered=True' not in S.sc(EXC, 'ProofCover', '%d,%d' % (O[0], O[1] + 4)), 'open ground')


def _ice(S):
    pond = [(O[0] + i, O[1] + j) for i in range(5) for j in range(5)]
    S.dig(pond, 2); S.fill(pond, 1.0, WATER)
    S.sc(NSP, 'ProofStageBasin', '%d,%d,5,5;freeze' % O)
    col = S.pawn('Colonist', (O[0] - 2, O[1]), 'player')
    r = S.call('jawa/flowworks_job_probe', pawnId=col, kind='dig', x=O[0], z=O[1], forced=True)
    S.ticks(5000)
    ice = S.call('jawa/list_things', defName='RM_CrushedIce', rect='%d,%d,7,7' % (O[0] - 1, O[1] - 1))
    S.row('ICE_cut_leaves_crushed_ice', bool(ice.get('things')), (r, ice.get('things')))
    S.ticks(30000)
    S.row('ICE_melts_back_into_pond', S.dl([O])[0] not in (0, None), S.dl([O]))


def _moat_raid(S):
    moat = [(O[0] + i, O[1]) for i in range(20)] + [(O[0] + i, O[1] + 1) for i in range(20)]
    S.dig(moat, 8); S.fill(moat, 2.0, WATER)
    S.call('jawa/spawn_batch', ops='RM_DrawbridgeGate:%d,%d' % (O[0] + 10, O[1]))
    S.call('jawa/spawn_batch', ops='RM_Sluice:%d,%d' % (O[0] + 20, O[1]))
    S.call('jawa/spawn_batch', ops='RM_LiquidTank:%d,%d' % (O[0] + 5, O[1] + 4))
    S.sc(NSP, 'ProofTank', '%d,%d;Store;RM_Liquid_Chemfuel;400' % (O[0] + 5, O[1] + 4))
    S.call('jawa/fire_raid', points=900, dryRun=False, strategy='ImmediateAttack')
    S.ticks(3000)
    swim = S.call('jawa/list_pawns', faction='hostile', rect='%d,%d,20,2' % O, includeHealth=True)
    S.row('MOAT_raiders_swim', bool(swim.get('pawns')), swim.get('pawns'))
    S.sc(NSP, 'ProofDrainGate', '%d,%d;open' % (O[0] + 20, O[1])); S.pulse(80)
    S.row('MOAT_drains_fast', all(not v for v in S.dl(moat)), S.dl(moat)[:8])
    held = [S.sc(NSP, 'ProofCaptureDown', p['id']) for p in (swim.get('pawns') or [])[:2]]
    S.row('MOAT_two_held_and_captured', len(held) == 2 and all('prisoner=True' in h for h in held), held)
    S.sc(NSP, 'ProofPump', '%d,%d;pour' % (O[0] + 5, O[1] + 3)); S.pulse(40)
    S.row('MOAT_chemfuel_pumped', any(S.dl(moat)), S.sc(NSP, 'ProofTank', '%d,%d' % (O[0] + 5, O[1] + 4)))
    _toss(S, moat[3], 'MOAT_moat_burns')
    S.again()                                                  # control: the drawbridge lowered, nobody swims
    S.dig(moat, 8); S.fill(moat, 2.0, WATER)
    S.call('jawa/spawn_batch', ops='RM_DrawbridgeGate:%d,%d' % (O[0] + 10, O[1]))
    S.call('jawa/fire_raid', points=900, dryRun=False, strategy='ImmediateAttack'); S.ticks(3000)
    S.row('MOAT_control_bridge_down_no_swim', 'swim' not in S.sc(NSP, 'ProofReadout', '%d,%d' % moat[10]).lower(), 'bridge down')


def _toss(S, target, rid, want_fire=True):
    """The toss-flame order (inv_toss_flame; no such order exists in the mod today, so the lit row is red)."""
    col = S.pawn('Colonist', (target[0], target[1] + 4), 'player')
    r = S.call('jawa/ordered_job', pawnId=col, jobDef='RM_TossFlame', targetAX=target[0], targetAZ=target[1])
    S.ticks(1200)
    fire = S.call('jawa/list_things', defName='Fire', rect='%d,%d,1,1' % target)
    S.row(rid, r.get('success') is not False and bool(fire.get('things')) == want_fire, (r, fire.get('things')))
    return col


def _toss_flame(S):
    fuel, water = _line(O[0], O[1], 8), _line(O[0], O[1] + 6, 8)
    S.dig(fuel + water, 4); S.fill(fuel, 1.0, FUEL); S.fill(water, 1.0, WATER)
    _toss(S, fuel[6], 'TOSS_picked_square_lights_first')
    _toss(S, water[6], 'TOSS_control_water_twin_stays_dark', want_fire=False)


def _wetting(S):
    canal, dry = _line(O[0], O[1], 12), _line(O[0], O[1] + 10, 12)
    S.call('jawa/set_terrain_batch', ops='%d,%d,14,16' % (O[0] - 1, O[1] - 3), terrainDef='Sand')
    S.dig(canal + dry, 4); S.fill(canal, 1.5, WATER)
    S.call('jawa/set_plants', ops='%d,%d,12,5;%d,%d,12,5' % (O[0], O[1] - 3, O[0], O[1] + 7), density=1.0, growth=0.1)
    S.ticks(5 * 60000)
    probe = [S.sc('RimMandrake.FlowWorks.RM_Wetting', 'ProbeWetness', '%d,%d' % (O[0] + 5, O[1] + d)) for d in (1, 2, 3)]
    S.row('WET_two_squares_then_none', 'wetted=True' in probe[0] and 'wetted=True' in probe[1] and 'wetted=False' in probe[2], probe)
    S.row('WET_control_dry_canal', 'wetted=False' in S.sc('RimMandrake.FlowWorks.RM_Wetting', 'ProbeWetness', '%d,%d' % (O[0] + 5, O[1] + 11)), 'dry twin')
    S.row('WET_never_standing_water', all(not v for v in S.dl(_line(O[0], O[1] + 1, 12))), S.dl(_line(O[0], O[1] + 1, 12)))


def _pit_trap(S, fall=True):
    pit = [(O[0] + i, O[1] + j) for i in range(3) for j in range(3)]
    S.dig(pit, 8)
    S.call('jawa/spawn_batch', ops=';'.join('RM_Spikes:%d,%d' % c for c in pit))
    if fall:
        S.sc(EXC, 'ProofCover', '%d,%d;cover' % pit[4])
    S.call('jawa/set_plants', ops='Plant_Grass:%d,%d,4,2' % (O[0] - 1, O[1] - 3), density=1.0, growth=1.0)
    S.call('jawa/fire_raid', points=700, dryRun=False, strategy='ImmediateAttack', spawnCenter='%d,%d' % (O[0] + 1, O[1] - 20))
    S.ticks(4000)
    return pit


def _fetch_fallen(S):
    pit = _pit_trap(S)
    fallen = S.call('jawa/list_pawns', faction='hostile', rect='%d,%d,3,3' % pit[0]).get('pawns') or []
    S.row('FETCH_two_fell', len(fallen) >= 2, fallen)
    lad = S.call('jawa/list_things', defName='RM_LadderPortable', rect='%d,%d,5,5' % (O[0] - 1, O[1] - 1))
    S.row('FETCH_ladder_into_pit', bool(lad.get('things')), lad.get('things'))
    return pit


def _fetch_fallen_scene(S):
    _fetch_fallen(S)
    S.again(); _pit_trap(S, fall=False)  # control: the cover left off, so no one falls
    lad = S.call('jawa/list_things', defName='RM_LadderPortable', rect='%d,%d,5,5' % (O[0] - 1, O[1] - 1))
    S.row('FETCH_control_none_fallen_no_ladder', not lad.get('things'), lad.get('things'))


def _pit_trap_raid(S):
    pit = _fetch_fallen(S)
    for p in (S.call('jawa/list_pawns', faction='hostile', rect='%d,%d,3,3' % pit[0]).get('pawns') or [])[:2]:
        S.row('PTR_fallen_become_prisoners', 'prisoner=True' in S.sc(NSP, 'ProofCaptureDown', p['id']), p['id'])
    S.again(); _pit_trap(S, fall=False)
    fell = S.call('jawa/list_pawns', faction='hostile', rect='%d,%d,3,3' % pit[0]).get('pawns') or []
    S.row('PTR_control_open_pit_no_one_falls', not fell, fell)


def _islands(S):
    span = _line(O[0], O[1], 16)
    S.dig(span, 8); S.fill(span, 2.0, WATER)
    S.call('jawa/spawn_batch', ops='RM_SuspensionBridge:%d,%d' % span[0])
    S.call('jawa/spawn_batch', ops='RM_DrawbridgeGate:%d,%d;RM_DrawbridgeGate:%d,%d' % (span[0] + span[-1]))
    S.call('jawa/fire_raid', points=900, dryRun=False, strategy='ImmediateAttack', spawnCenter='%d,%d' % span[8])
    S.ticks(5000)
    on = S.call('jawa/list_pawns', faction='hostile', rect='%d,%d,16,1' % O).get('pawns') or []
    gates = S.call('jawa/list_things', defName='RM_DrawbridgeGate', rect='%d,%d,17,1' % (O[0] - 1, O[1])).get('things') or []
    S.row('ISL_winch_destroyed_and_escape', len(gates) < 2 and not on, (len(gates), on))


def _walk(S):
    S.dig(_line(O[0] - 1, O[1], 21), 4); S.fill([(O[0] - 1, O[1])], 2.0, WATER); S.pulse(40)
    # Stage 6 visit 1: the draft compared 'stock' and 'cells', keys engine_state never returns, so None == None passed.
    keys = ('excavatedCellCount', 'superdeepCellCount', 'bodyCount', 'activeFluid')
    def digest():
        e = S.call('jawa/flowworks_engine_state')
        return tuple(e.get(k) for k in keys) + (S.sc(FLUIDID, 'ProofCensus').split('|')[0].strip(),)
    a = digest()
    S.setting('depthEngineEnabled', False); S.ticks(600); S.setting('depthEngineEnabled', True); S.ticks(600)
    b = digest()
    S.row('WALK_toggle_off_on_digest_matches', None not in a and a[0] and a == b, (a, b))


def _garden(S):
    # The canal wetting rows left 0.1.0 with the wetting bars (owner by card 2026-11-14, OWNER:1794721673433243094); the
    # garden keeps its field and pumped network. _wetting and scene_wetting stay for FlowWorks 0.2.0.
    S.call('jawa/set_plants', ops='Plant_Potato:%d,%d,12,5' % (O[0], O[1] - 3), density=1.0, growth=0.1)
    S.call('jawa/spawn_batch', ops='RM_LiquidDrill:%d,%d;RM_LiquidPump:%d,%d;RM_SprinklerHead:%d,%d;RM_LiquidTank:%d,%d;RM_PipeFaucet:%d,%d'
           % (O[0] + 14, O[1], O[0] + 15, O[1], O[0] + 14, O[1] - 3, O[0] + 16, O[1] + 2, O[0] + 17, O[1] + 2))
    S.ticks(60000)
    t = S.sc(NSP, 'ProofTank', '%d,%d' % (O[0] + 16, O[1] + 2))
    S.row('GARDEN_hose_fills_tank', 'units=0' not in t and 'REFUSED' not in t, t)


def _geyser_tub(S):
    gey = S.call('jawa/list_things', defName='SteamGeyser', rect='0,0,250,250', limit=1).get('things') or []
    require(gey, 'no SteamGeyser on the prepared map')
    c = (gey[0]['x'], gey[0]['z']); pit = [(c[0] + i, c[1] + j) for i in range(-1, 3) for j in range(-1, 3)]
    S.dig(pit, 8); S.fill(pit, 1.0, WATER); S.pulse(20)
    ins = S.call('jawa/inspect_string', rect='%d,%d,1,1' % c)
    S.row('TUB_reads_hot_tub', 'Hot tub' in str(ins) or 'Hot Tub' in str(ins), str(ins)[:200])
    col = S.pawn('Colonist', (c[0] + 4, c[1]), 'player'); S.ticks(30000)
    S.row('TUB_pawn_soaks_bonus', 'HotSpring' in str(S.call('jawa/pawn_need', pawn=col, action='list')), col)


def _coating_wash(S):
    """inv_liquid_coating, owed under RIMMANDRAKE_DESIGN_LIQUID_DIRT_AS_CONDITION_NOT_GRAPHICS: red until the condition exists."""
    oil, water = _line(O[0], O[1], 4), _line(O[0] + 6, O[1], 4)
    S.dig(oil + water, 2); S.fill(oil, 0.5, OIL); S.fill(water, 0.5, WATER)
    col = S.pawn('Colonist', (O[0] - 1, O[1]), 'player')
    S.walk(col, oil[-1], 600); S.walk(col, (O[0] + 5, O[1] + 2), 400)
    h = S.call('jawa/list_pawns', faction='player', rect='%d,%d,1,1' % (O[0] + 5, O[1] + 2), includeHealth=True)
    S.row('COAT_named_condition', 'Coated' in str(h) or 'coated' in str(h), str(h)[:200])
    S.walk(col, water[-1], 600)
    h2 = S.call('jawa/list_pawns', faction='player', rect='%d,%d,1,1' % water[-1], includeHealth=True)
    S.row('COAT_water_washes_it', 'oated' not in str(h2), str(h2)[:200])


scene_fill_front = _run('scene_fill_front', _fill_front)
scene_one_surface = _run('scene_one_surface', _one_surface)
scene_source_pays = _run('scene_source_pays', _source_pays)
scene_pawn_height = _run('scene_pawn_height', _pawn_height)
scene_hose_look = _run('scene_hose_look', _hose_look)
scene_trench_cover = _run('scene_trench_cover', _trench_cover)
scene_ice = _run('scene_ice', _ice)
scene_moat_raid = _run('scene_moat_raid', _moat_raid)
scene_toss_flame = _run('scene_toss_flame', _toss_flame)
scene_wetting = _run('scene_wetting', _wetting)
scene_fetch_fallen = _run('scene_fetch_fallen', _fetch_fallen_scene)
scene_islands = _run('scene_islands', _islands)
scene_walk_moat_season = _run('scene_walk_moat_season', _walk)
scene_pit_trap_raid = _run('scene_pit_trap_raid', _pit_trap_raid)
scene_garden = _run('scene_garden', _garden)
scene_geyser_tub = _run('scene_geyser_tub', _geyser_tub)
scene_coating_wash = _run('scene_coating_wash', _coating_wash)
STAGE3_SCENES = {f.__name__: f for f in (scene_fill_front, scene_one_surface, scene_source_pays, scene_pawn_height,
                 scene_hose_look, scene_trench_cover, scene_ice, scene_moat_raid, scene_toss_flame, scene_wetting,
                 scene_fetch_fallen, scene_islands, scene_walk_moat_season, scene_pit_trap_raid, scene_garden,
                 scene_geyser_tub, scene_coating_wash)}



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--absolute', action='store_true')
    ap.add_argument('--abort', action='store_true')
    ap.add_argument('--scene', default='scene_hole_prison', choices=['scene_hole_prison'] + sorted(STAGE3_SCENES))
    a = ap.parse_args()
    import validation_core as V
    import test_site_saves as T
    from game_paths import SAVES
    B = V.Bridge()
    res = {'script': __file__, 'started': time.time(), 'mode': 'live', 'calls': []}
    name = ('WHITTLE_HolePrison_Begin_' if a.scene == 'scene_hole_prison' else 'FW_%s_Begin_' % a.scene) + time.strftime('%Y%m%dT%H%M%S')
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
            r = T.load_site(B.call, 'calm', name=occupied, check=False, map_controls=('modal_broker',))
            require(r['verified'], 'occupied reload failed: '+str(r))
            return r
        if a.scene != 'scene_hole_prison':
            out = STAGE3_SCENES[a.scene](B, snapshot, reload_snapshot, res)
            require(out['status'] == 'PASS', 'rows not all PASS: %s' % [(x['id'], x['status']) for x in out['rows']])
            res['status'] = 'PASS'
            return 0
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
