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
# ';' passed to ProofCover and ProofDrainGate (their read forms are documented in the C#; the verbs are not).
# =====================================================================================================================
EXC = 'RimMandrake.FlowWorks.RM_PromotionProofs'
NSP = 'RimMandrake.FlowWorks.RM_NorthstarProofs'
FLUIDID = 'RimMandrake.FlowWorks.RM_FluidIdentityProof'
HPROBE = 'RimMandrake.FlowWorks.Hose.HoseProbe'
WATER, TAR, FUEL, OIL = 'RM_Fluid_Water', 'RM_Fluid_Tar', 'RM_Fluid_Chemfuel', 'RM_Fluid_Oil'
O = (60, 60)  # scene origin on the prepared map; Stage 6 moves it to the dense map's free block


class _Stage:
    """The shared half of every Stage 3 scene: recorded calls, settings restored, real ticks, rows, restore in finally."""

    def __init__(self, B, receipt, name):
        self.B, self.r, self.prior = B, receipt, {}
        receipt.update({'scene': name, 'rows': [], 'calls': receipt.get('calls', [])})
        self.reload = None
        self.save_mid = self.load_mid = None   # a second, mid-way save (scene_walk_moat_season); main passes them

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

    def hp(self, cmd):
        """One HoseProbe verb (census | lay: | pump: | tank: ...), recorded; a reply that never came is {'success': False}."""
        r = self.B.probe_of(HPROBE, cmd, 20.0, 0.3)
        r = r if isinstance(r, dict) else {'success': False, 'raw': r}
        self.r['calls'].append({'tool': 'hose_probe', 'args': cmd, 'result': r})
        return r

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
    def scene(B, snapshot, reload_snapshot, receipt, save_mid=None, load_mid=None):
        S = _Stage(B, receipt, name)
        S.reload, S.save_mid, S.load_mid = reload_snapshot, save_mid, load_mid
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


# sc_hose_look, staged from proof_hose.py's realflow plot (scene 0, measured live): a 3-cell channel dug 2 and filled 1 m, the
# pump on its north bank, a charged battery, the reel north of the pump facing a tank 14 cells east, the hose laid to the
# tank's west neighbour. Visit 1 (2026-11-15) spawned a bare pump and reel side by side: no source, no power, no laid hose,
# so the pump never ran and "flat" passed on a hose that was never there (RIMMANDRAKE_REBUILD_FLOWWORKS_HOSE_SCENE_PUMP_HAD_
# NO_SOURCE). Every row reads the hose census (state, tintLiquid) and the far tank, and a read that cannot carry a verdict
# (no hose in the census, an unpowered pump in the flowing case) is UNMEASURED, never PASS.
HOSE_LIQUID = 'RM_Liquid_FreshWater'
HOSE_PLUMP_BOUND, HOSE_FLAT_BOUND, HOSE_CONTROL_WAIT = 300, 915, 600   # realflow: plump <= 300 ticks; flat <= 1.5 x 250 + 530
HOSE_CYCLE = 250


def _hose_plot(S, battery=True):
    import validation_core as V
    ox, oz = O
    P = {'channel': [(ox + 2 + k, oz + 6) for k in range(3)], 'pump': (ox + 3, oz + 7), 'battery': (ox + 6, oz + 6),
         'reel': (ox + 3, oz + 8), 'end': (ox + 16, oz + 9), 'tank': (ox + 17, oz + 9)}
    S.call('jawa/destroy_batch', rects='%d,%d,32,14' % (ox - 6, oz), categories='Building,Plant,Item,Filth')
    S.call('jawa/set_terrain_batch', ops='Soil:%d,%d,32,14' % (ox - 6, oz))
    S.call('jawa/set_roof_batch', ops='None:%d,%d,32,14' % (ox - 6, oz))
    S.dig(P['channel'], 2)
    S.dig(P['channel'], 0, water_m=1.0)
    ops = ['RM_LiquidPump:%d,%d' % P['pump'], V.reel_toward(P['reel'], P['end']), 'RM_LiquidTank:%d,%d' % P['tank']]
    ops += ['Battery:%d,%d' % P['battery']] if battery else []
    b = S.call('jawa/build_batch', ops=';'.join(ops), faction='player', wipeExisting=False)
    require(int(b.get('survived') or 0) >= len(ops), 'build_batch built less than asked: %s' % b)   # survived, never placed
    S.ticks(2)
    if battery:
        bid = ((S.call('jawa/list_things', defName='Battery', rect='%d,%d,1,2' % P['battery'], limit=2).get('things') or [{}])[0]).get('id')
        require(bid is not None, 'no battery at %s' % (P['battery'],))
        S.call('jawa/battery_set', thing=bid, mode='setPct', value=1.0)
    P['powered'] = _poll_ticks(S, lambda: S.hp('pump:%d,%d' % P['pump']).get('powered'), 400 if battery else 0)
    lay = S.hp('lay:%d,%d,%d,%d' % (P['reel'] + P['end']))
    require(lay.get('success') and lay.get('layOk'), 'the hose would not lay: %s' % lay)
    P['at_reel'] = lambda pos: V.reel_at(pos, P['reel'])
    return P


def _poll_ticks(S, fn, bound, step=10):
    """Ticks until fn() is truthy (None if never within bound)."""
    waited = 0
    while not fn():
        if waited >= bound:
            return None
        S.ticks(step)
        waited += step
    return waited


def _hose_of(S, P):
    for h in S.hp('census').get('hoses') or []:
        if P['at_reel'](h.get('reel')):
            return h
    return {}


def _tank_units(S, cell):
    r = S.hp('tank:%d,%d' % cell)
    return r.get('units') if r.get('success') else None


def _hose_look(S):
    P = _hose_plot(S)
    require(P['powered'] is not None, 'the pump never read powered with a charged battery beside it')
    u0 = _tank_units(S, P['tank'])
    plump = _poll_ticks(S, lambda: _hose_of(S, P).get('state') == 'Plump', HOSE_PLUMP_BOUND)
    h = _hose_of(S, P)
    # the far tank gains by the next pump cycle (250 ticks at the pump's own phase), not at the plump tick
    _poll_ticks(S, lambda: u0 is None or (_tank_units(S, P['tank']) or 0) > u0, HOSE_CYCLE + 10)
    u1 = _tank_units(S, P['tank'])
    S.shot('flowing', P['reel'], 18, 8)
    seen = bool(h.get('state')) and u0 is not None and u1 is not None
    S.row('HOSE_plump_when_flowing', seen and plump is not None and u1 > u0,
          {'plumpAfterTicks': plump, 'state': h.get('state'), 'tank': [u0, u1], 'netLink': h.get('netLink')}, unmeasured=not seen)
    S.row('HOSE_tinted_carried_liquid', h.get('tintLiquid') == HOSE_LIQUID, {'tintLiquid': h.get('tintLiquid'), 'want': HOSE_LIQUID},
          unmeasured=not h.get('state') or plump is None)
    cut = S.call('jawa/destroy_batch', rects='%d,%d,1,2' % P['battery'], categories='Building')
    require(int(cut.get('destroyed') or 0) >= 1, 'battery not destroyed: %s' % cut)
    flat = _poll_ticks(S, lambda: _hose_of(S, P).get('state') == 'Flat', HOSE_FLAT_BOUND)
    a = _tank_units(S, P['tank'])
    S.ticks(300)
    b = _tank_units(S, P['tank'])
    S.shot('stopped', P['reel'], 18, 8)
    S.row('HOSE_flat_when_not', flat is not None and a is not None and a == b,
          {'flatAfterCut': flat, 'bound': HOSE_FLAT_BOUND, 'tankAfterCut': [a, b], 'state': _hose_of(S, P).get('state')},
          unmeasured=plump is None or a is None)
    # control: the same plot with no battery -- a laid reel alone must not plump (rules out the look keyed to the lay)
    S.again()
    C = _hose_plot(S, battery=False)
    states = []
    for _ in range(HOSE_CONTROL_WAIT // 30):
        S.ticks(30)
        states.append(_hose_of(S, C).get('state'))
    S.shot('control_unpowered', C['reel'], 18, 8)
    S.row('HOSE_control_unpowered_stays_flat', all(x == 'Flat' for x in states),
          {'states': sorted(set(map(str, states))), 'pumpPowered': C['powered'] is not None},
          unmeasured=not states or None in states or C['powered'] is not None)


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


# RIMMANDRAKE_REBUILD_FLOWWORKS_ICE_SCENE_BASIN_NEVER_FROZE (visit 1, 2026-11-15): the draft passed '60,60,5,5;freeze' to
# ProofStageBasin, a dig-and-fill stager whose contract is x;z;w;h;levels;waterM;FluidDef, which refused it, so the pond never
# froze; its "cut" was flowworks_job_probe, which designates and orders nothing, so no cut ever happened; and
# ICE_melts_back_into_pond read the fill's own 20,000 dL and PASSED. Now the pond freezes the way vanilla freezes water
# (FreezeManager lays ThinIce on the temp grid; set_terrain_batch routes a temporary def to SetTempTerrain), read back square by
# square; the cut is designated and ordered (gravel_live.cut_once's idiom) and the cut square must still read ThinIce at the
# last poll before it lands; the melt is judged on the melt ledger (RM_IceMelter.ProofMeltLedger) once the site is above 0 C.
# The control is an unfrozen twin pond, cut first. No ColdSnap: it ramps over 12,000 ticks and the governor raises on a
# frostbitten colonist (a hurt with no pawn source); a site above 2 C may thaw the painted ice, which reads UNMEASURED, never PASS.
ICE_TEMP, CRUSHED, MELT_DL = 'ThinIce', 'RM_CrushedIce', 10000   # one notch melts to 1,000 L (ICE_YIELD_DECIDE_ONE_CUT_FOUR_NOTCHES)
MELTER = 'RimMandrake.FlowWorks.RM_IceMelter'
ICE_CUT_TICKS, ICE_MELT_TICKS = 6000, 40000                       # a pile melts after 10,000 ticks above 0 C, one at a time


def _ice_squares(S, x, z, w, h):
    """ThinIce squares in the rect from get_terrain_batch's ops text ('ThinIce:x,z[,w,h];...'); None when the read came back empty."""
    import re
    ops = S.call('jawa/get_terrain_batch', rects='%d,%d,%d,%d' % (x, z, w, h)).get('ops')
    if not ops:
        return None
    return sum(int(m.group(1) or 1) * int(m.group(2) or 1)
               for m in re.finditer(r'(?<![A-Za-z_])%s:-?\d+,-?\d+(?:,(\d+),(\d+))?' % ICE_TEMP, ops))


def _crushed_near(S, c, r=3):
    rows = S.call('jawa/list_things', defName=CRUSHED, rect='%d,%d,%d,%d' % (c[0] - r, c[1] - r, 2 * r + 1, 2 * r + 1)).get('things')
    return None if rows is None else sum(int(t.get('stackCount') or 1) for t in rows if t.get('def', CRUSHED) == CRUSHED)


def _melt_ledger(S):
    """spilled + into water + nearby, dL (the three places a thawed pile's water goes); None when unreadable."""
    try:
        return sum(int(v) for v in S.sc(MELTER, 'ProofMeltLedger').split(';')[:3])
    except ValueError:
        return None


def _ice_cut(S, pid, c, frozen):
    """Designate and order one cut at c; tick until its depth changes. -> (verdict_kind, detail): 'landed' | 'mod' (the mod's
    designator or work giver refused the square) | 'site' (a pawn-side gate, or the ice gone before the cut landed) | 'harness'."""
    d0 = S.cells([c])[0].get('d')
    S.call('jawa/designate_batch', action='add', designation='RM_DigCanal', rect='%d,%d,1,1' % c)
    pr = S.call('jawa/flowworks_job_probe', pawnId=pid, kind='dig', x=c[0], z=c[1])
    wg, pw = pr.get('workGiver') or {}, pr.get('pawn') or {}
    det = {'d0': d0, 'terrain': pr.get('terrain'), 'designator': pr.get('designator'), 'workGiver': wg}
    if not pr.get('success') or d0 is None:
        return 'harness', dict(det, why='job probe or depth read unavailable: %s' % str(pr.get('message') or pr)[:160])
    if pw.get('workTypeDisabled') or pw.get('missingCapacity') or pw.get('canReach') is False:
        return 'site', dict(det, why='the colonist cannot do the cut: %s' % pw)
    if not (pr.get('designator') or {}).get('accepted') or pr.get('designationPresent') is not True:
        return 'mod', dict(det, why='the dig designator refused the square: %s' % pr.get('designator'))
    if wg.get('hasJobOnCell') is not True or wg.get('jobDef') != 'RM_DigCanalJob':
        return 'mod', dict(det, why='the work giver hands no RM_DigCanalJob here (shouldSkip=%s failReason=%s)' % (
            wg.get('shouldSkip'), wg.get('failReason')))
    od = S.call('jawa/ordered_job', pawnId=pid, jobDef='RM_DigCanalJob', targetAX=c[0], targetAZ=c[1], waitTicks=0)
    if od.get('success') is False or od.get('accepted') is False:
        return 'harness', dict(det, why='ordered_job refused: %s' % str(od)[:160])
    iced, t = None, 0
    while t < ICE_CUT_TICKS:
        if frozen:
            iced = _ice_squares(S, c[0], c[1], 1, 1)
        S.ticks(250)
        t += 250
        d = S.cells([c])[0].get('d')
        if d not in (None, d0):
            det.update(d1=d, cutAt=t, iceAtLastPoll=iced)
            if frozen and not iced:
                return 'site', dict(det, why='the cut square no longer read ThinIce before the cut landed (%s)' % iced)
            return 'landed', det
    return 'harness', dict(det, why='the ordered cut did not land in %d ticks' % ICE_CUT_TICKS, iceAtLastPoll=iced)


def _ice(S):
    pond, twin = (O[0], O[1]), (O[0] + 12, O[1])                  # two 5x5 ponds, 7 squares of dry ground between
    for p in (pond, twin):
        sq = [(p[0] + i, p[1] + j) for i in range(5) for j in range(5)]
        S.dig(sq, 2); S.fill(sq, 1.0, WATER)
    S.setting('iceDigEnabled', True)
    S.setting('digRockWorkMultiplier', 1.0)                        # the rows judge the yield, not the cut's time
    cut, twin_cut = (pond[0], pond[1] + 2), (twin[0], twin[1] + 2)  # west-edge middles, reachable from the bank
    col = S.pawn('Colonist', (pond[0] - 2, pond[1] + 2), 'player')

    # control first, on the unfrozen twin: a cut through open water leaves no crushed ice
    n0 = _crushed_near(S, twin_cut)
    kind, det = _ice_cut(S, col, twin_cut, frozen=False)
    n1 = _crushed_near(S, twin_cut)
    S.row('ICE_control_unfrozen_cut_no_crushed_ice', kind == 'landed' and n1 == n0, dict(det, crushed=(n0, n1)),
          unmeasured=kind != 'landed' or None in (n0, n1))
    S.call('jawa/destroy_batch', rects='%d,%d,7,7' % (twin_cut[0] - 3, twin_cut[1] - 3), categories='Item')  # no pile of
    # the twin's may thaw into the melt ledger the frozen pond's row reads

    # the frozen pond (asserted ice), then the cut
    S.call('jawa/set_terrain_batch', ops='%s:%d,%d,5,5' % ((ICE_TEMP,) + pond))
    iced = _ice_squares(S, pond[0], pond[1], 5, 5)
    temp = S.call('jawa/cell_temperature', cell='%d,%d' % cut).get('temperature')
    if iced != 25:
        S.row('ICE_cut_leaves_crushed_ice', False, 'the pond did not read frozen: %s/25 ThinIce squares' % iced, unmeasured=True)
        S.row('ICE_melts_back_into_pond', False, 'no frozen pond, so no cut and no melt', unmeasured=True)
        return
    c0 = _crushed_near(S, cut)
    kind, det = _ice_cut(S, col, cut, frozen=True)
    c1 = _crushed_near(S, cut)
    made = (c1 - c0) if None not in (c0, c1) else None
    det.update(crushed=(c0, c1), siteTempC=temp)
    if kind in ('landed', 'mod'):
        S.row('ICE_cut_leaves_crushed_ice', kind == 'landed' and bool(made and made >= 1), det, unmeasured=made is None)
    else:
        S.row('ICE_cut_leaves_crushed_ice', False, det, unmeasured=True)
    if not made or made < 1:
        S.row('ICE_melts_back_into_pond', False, 'no crushed ice from the cut, so nothing to melt (%s)' % det.get('why', made),
              unmeasured=True)
        return

    # warm: every pile melts into the water its cut removed, and the world takes exactly that much
    lg0, t, left, warm = _melt_ledger(S), 0, c1, []
    while t < ICE_MELT_TICKS and left:
        S.ticks(2000)
        t += 2000
        left = _crushed_near(S, cut)
        warm.append(S.call('jawa/cell_temperature', cell='%d,%d' % cut).get('temperature'))
    lg1 = _melt_ledger(S)
    mdet = {'crushedLeft': left, 'ticks': t, 'ledger': (lg0, lg1), 'want': made * MELT_DL, 'tempsC': warm[-4:]}
    known = [w for w in warm if isinstance(w, (int, float))]
    if None in (lg0, lg1, left):
        S.row('ICE_melts_back_into_pond', False, dict(mdet, why='a melt-ledger or crushed-ice read came back empty'), unmeasured=True)
    elif left and (not known or max(known) <= 0):
        S.row('ICE_melts_back_into_pond', False, dict(mdet, why='the site never got above 0 C: no thaw to judge'), unmeasured=True)
    else:
        S.row('ICE_melts_back_into_pond', not left and lg1 - lg0 == made * MELT_DL, mdet)


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
    """The toss-flame order (RM_TossFlame.cs): the colonist walks to the rim and tosses. A lit canal or pond carries the
    liquid-fire engine's own flame, not a vanilla Fire, and chemfuel can burn out within the wait, so the row polls the
    engine's cell report (burning=True) and a vanilla Fire on the square every 60 ticks and keeps the first sight."""
    col = S.pawn('Colonist', (target[0], target[1] + 4), 'player')
    r = S.call('jawa/ordered_job', pawnId=col, jobDef='RM_TossFlame', targetAX=target[0], targetAZ=target[1])
    lit, seen = False, None
    for _ in range(20):
        S.ticks(60)
        seen = (S.sc('RimMandrake.FlowWorks.RM_LiquidFireProof', 'ProofCell', '%d,%d' % target),
                S.call('jawa/list_things', defName='Fire', rect='%d,%d,1,1' % target).get('things'))
        if 'burning=True' in seen[0] or seen[1]:
            lit = True
            break
    S.row(rid, r.get('success') is not False and lit == want_fire, (r, seen))
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


# RIMMANDRAKE_REBUILD_FLOWWORKS_FETCH_SCENE_RAID_NEVER_CAME (visit 1, 2026-11-15): the draft passed '61,61;cover' to
# ProofCover, a read-only x,z probe that refused it, so no cover was ever laid; its raid stopped the governor at tick 60 as an
# undeclared hostile_arrival and site_recover vanished every raider (no fallen, no ladder); and the control read "no ladder"
# off an empty map and PASSED. Now: a 1-wide trench across the passage (each lid rests on its two banks), lids built and
# read back covered, the scene's own raid run on a narrowed governor, and every row UNMEASURED when its event never happened.
TRAP_W = 9                                          # trench cells across the passage, x = O[0]-4 .. O[0]+4 at z = O[1]
TRAP_COVER = 'RM_PitCover_PlankLattice'             # gives way under 120 kg on the deck: about two raiders at once
TRAP_TREE = 'Plant_TreeOak'                         # wood the raiders could chop for a ladder (scenes.json: saplings beside it)
RAID_STOP_ON = 'clock_discontinuity,modal_stuck,colony_loss,cancel'   # a raid hurts, downs and kills by design
TRAP_POLL, TRAP_POLLS = 300, 40                     # 12,000 ticks: fall, chop, ladder


def _trap_cells():
    return _line(O[0] - TRAP_W // 2, O[1], TRAP_W)


def _cheb(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def _pit_trap(S, fall=True):
    """Stage the spiked trench (lidded when `fall`), trees beside it, two defenders across it, and fire a raid of about six
    at its south side. -> the trench cells. Staging that does not read back is an AssertionError (the scene's _staging row)."""
    pit = _trap_cells()
    S.dig(pit, 8)
    S.call('jawa/spawn_batch', ops=';'.join('RM_Spikes:%d,%d' % c for c in pit))
    if fall:
        S.call('jawa/build_batch', ops=';'.join('%s:%d,%d' % ((TRAP_COVER,) + c) for c in pit), faction='player',
               wipeExisting=False)
        lids = [S.sc(EXC, 'ProofCover', '%d,%d' % c) for c in pit]
        require(all('covered=True' in t for t in lids), 'the trench lids did not read back covered: %s' % lids[:3])
    S.call('jawa/set_plants', ops='%s:%d,%d,3,2' % (TRAP_TREE, O[0] + TRAP_W, O[1] - 3), density=1.0, growth=1.0)
    for dx in (-2, 2):
        S.pawn('Colonist', (O[0] + dx, O[1] + 10), 'player')
    S.call('jawa/fire_raid', points=700, dryRun=False, strategy='ImmediateAttack', spawnCenter='%d,%d' % (O[0], O[1] - 4))
    return pit


def _watch_trap(S, pit, until_ladder=True):
    """Run the raid in TRAP_POLL chunks on the narrowed governor; each poll reads every live raider's place and trap state
    (ProofTrap held=), and any portable ladder in or beside the trench. -> {reached, held, ladder, raiders, polls}.
    reached: a raider came within 2 squares of the trench (the event the rows need); held: raider ids the trench holds."""
    prior, S.B.stop_on = S.B.stop_on, RAID_STOP_ON
    seen = {'reached': False, 'held': set(), 'ladder': [], 'raiders': 0, 'polls': 0, 'last': []}
    rect = '%d,%d,%d,3' % (pit[0][0] - 1, pit[0][1] - 1, len(pit) + 2)
    try:
        for _ in range(TRAP_POLLS):
            S.ticks(TRAP_POLL)
            seen['polls'] += 1
            live = [p for p in S.call('jawa/list_pawns', faction='hostile').get('pawns') or []
                    if not p.get('dead') and p.get('x') is not None]
            seen['raiders'] = max(seen['raiders'], len(live))
            seen['last'] = [(p.get('id'), p.get('x'), p.get('z')) for p in live][:8]
            for p in live:
                if min(_cheb((p['x'], p['z']), c) for c in pit) <= 2:
                    seen['reached'] = True
                if (p['x'], p['z']) in pit and 'held=True' in S.sc(NSP, 'ProofTrap', str(p['id'])):
                    seen['held'].add(p['id'])
            lad = S.call('jawa/list_things', defName='RM_LadderPortable', rect=rect).get('things') or []
            if lad:
                seen['ladder'] = lad
                if until_ladder:
                    break
    finally:
        S.B.stop_on = prior
    if seen['held']:
        seen['reached'] = True
    return seen


def _fetch_rows(S, seen):
    no_raid = not seen['reached']
    why = '' if not no_raid else 'the raid never came within 2 squares of the trench (raiders seen %d, last %s); ' % (
        seen['raiders'], seen['last'])
    S.row('FETCH_two_fell', len(seen['held']) >= 2, why + 'held %s' % sorted(seen['held']), unmeasured=no_raid)
    S.row('FETCH_ladder_into_pit', bool(seen['ladder']),
          ('nobody fell, so there was no one to fetch; ' if not seen['held'] else '') + why + str(seen['ladder']),
          unmeasured=not seen['held'])


def _fetch_fallen(S):
    pit = _pit_trap(S)
    seen = _watch_trap(S, pit)
    _fetch_rows(S, seen)
    return pit, seen


def _fetch_fallen_scene(S):
    _fetch_fallen(S)
    S.again()
    pit = _pit_trap(S, fall=False)                  # control: no lid, so no one falls; the same raid must not ladder the pit
    seen = _watch_trap(S, pit, until_ladder=False)
    S.row('FETCH_control_none_fallen_no_ladder', not seen['ladder'] and not seen['held'],
          ('the raid never came within 2 squares of the trench (raiders seen %d); ' % seen['raiders'] if not seen['reached']
           else '') + 'held %s ladder %s' % (sorted(seen['held']), seen['ladder']), unmeasured=not seen['reached'])


def _pit_trap_raid(S):
    pit, seen = _fetch_fallen(S)
    for pid in sorted(seen['held'])[:2]:
        S.row('PTR_fallen_become_prisoners', 'prisoner=True' in S.sc(NSP, 'ProofCaptureDown', pid), pid)
    if not seen['held']:
        S.row('PTR_fallen_become_prisoners', False, 'nobody fell', unmeasured=True)
    S.again(); pit = _pit_trap(S, fall=False)
    seen = _watch_trap(S, pit, until_ladder=False)
    S.row('PTR_control_open_pit_no_one_falls', not seen['held'], sorted(seen['held']), unmeasured=not seen['reached'])


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


def _vacuous(v):
    """A read that cannot carry a verdict: nothing, a REFUSED reply, or every field empty/zero. Its row is UNMEASURED."""
    if v is None or (isinstance(v, str) and (not v.strip() or 'REFUSED' in v)):
        return True
    if isinstance(v, (tuple, list)):
        return not v or any(_vacuous(x) for x in v if isinstance(x, str) or x is None) or not any(v)
    return False


def _litres(readout):
    """'OK Hole 2 m · Water 1.00 m (2,000 L)' -> 2000.0; an 'OK Hole' line with no Water part -> 0.0; anything else None."""
    import re
    if not isinstance(readout, str) or not readout.startswith('OK Hole'):
        return None
    m = re.search(r'Water\s+[\d.]+\s*m\s*\(([\d,.]+)\s*L\)', readout)
    return float(m.group(1).replace(',', '')) if m else (None if 'Water' in readout else 0.0)


FW_MARKS = ('flowworks', 'rm_fluid', 'rm_mapcomponent_excavation', 'rm_liquid')   # a journal entry that names FlowWorks


def _walk(S):
    """sc_walk on his full list. The bar: state digests match across a mid-way reload (control: a pre-fill reload differs);
    the pond pays again after the reload and an off/on of the master switch; no leftovers; the log clean (FlowWorks lines).
    Stage 6 visit 1 (RIMMANDRAKE_FINISH_FLOWWORKS_WALK_SCENE_HALF_THE_BAR_UNASKED): the draft compared 'stock'/'cells', keys
    engine_state never returns (None == None passed); and depthEngineEnabled snaps at game load unless depthEngineLiveForTests
    is set, so its off/on never stopped anything. Every row below refuses a vacuous read (UNMEASURED, never PASS)."""
    import validation_core as V
    tap = V.tap_start(S.B)
    pond = [(O[0] - 4 + i, O[1] - 1 + j) for i in range(3) for j in range(3)]
    moat = _line(O[0] - 1, O[1], 21)
    moat1, moat2 = moat[:10], moat[10:]
    keys = ('excavatedCellCount', 'superdeepCellCount', 'bodyCount', 'activeFluid')

    def litres():
        return _litres(S.sc(NSP, 'ProofReadout', '%d,%d' % (O[0] - 3, O[1])))

    def digest():
        e = S.call('jawa/flowworks_engine_state')
        return tuple(e.get(k) for k in keys) + (S.sc(FLUIDID, 'ProofCensus').split('|')[0].strip(), litres())

    def pays(rid, p_before, cells):
        p_after, wet = litres(), S.dl(cells)
        bad = _vacuous((p_before,)) or p_after is None or None in wet
        S.row(rid, not bad and p_after < p_before and any(wet), (p_before, p_after, wet), unmeasured=bad)
        return p_after

    S.setting('depthEngineLiveForTests', True)        # the off/on below must reach the running engine, not the next load
    S.dig(pond, 4); S.fill(pond, 2.0, WATER)
    p0 = litres()
    S.dig(moat1, 4); S.pulse(40)
    pays('WALK_pond_pays', p0, moat1)

    a = digest()
    if S.save_mid is None:
        S.row('WALK_reload_digest_matches', False, 'no mid-way save hook passed to the scene', unmeasured=True)
    else:
        S.save_mid(); S.ticks(600); S.load_mid()
        b = digest()
        S.row('WALK_reload_digest_matches', a == b, (a, b), unmeasured=_vacuous(a) or _vacuous(b))
        S.again()                                      # the control: the scene-begin save, made before the fill
        c = digest()
        S.row('WALK_control_prefill_reload_differs', c != a, (c, a), unmeasured=_vacuous(a) or c[0] is None)
        S.load_mid()
        S.setting('depthEngineLiveForTests', True)     # a load does not reset a static, but say it again after one

    a2 = digest()
    S.setting('depthEngineEnabled', False); S.ticks(600); S.setting('depthEngineEnabled', True); S.ticks(600)
    b2 = digest()
    S.row('WALK_toggle_off_on_digest_matches', a2 == b2, (a2, b2), unmeasured=_vacuous(a2) or _vacuous(b2))

    # the switch took: off, a dry moat dug onto the wet one stays dry and the pond keeps its stock through two pulse intervals
    p2 = litres()
    S.setting('depthEngineEnabled', False)
    S.dig(moat2, 4); S.ticks(600)
    held, p_off = S.dl(moat2), litres()
    bad = None in held or _vacuous((p2,)) or p_off is None
    S.row('WALK_switch_off_holds_water', not bad and not any(held) and p_off == p2, (p2, p_off, held), unmeasured=bad)
    S.setting('depthEngineEnabled', True); S.ticks(600); S.pulse(40)
    pays('WALK_pond_pays_again', p2, moat2)

    # no leftovers: every wet cell carries its fluid, water is the only fluid, and the bodies are the ones before the switch
    e, census = S.call('jawa/flowworks_engine_state'), S.sc(FLUIDID, 'ProofCensus')
    import re
    m = re.search(r'unrecorded (\d+) \| fluids \[([^\]]*)\]', census)
    bad = m is None or e.get('bodyCount') is None or a2[2] is None
    S.row('WALK_no_leftovers', not bad and m.group(1) == '0' and m.group(2) == WATER and e.get('bodyCount') == a2[2],
          (census, e.get('bodyCount'), a2[2]), unmeasured=bad)

    # the log: no warning or error naming FlowWorks over the whole scene, on a journal proven live and read without a gap
    alive = V.log_alive(S.B, 'sc_walk').get('alive')
    ours = [str(x.get('Message', ''))[:160] for x in tap.since() if any(k in str(x.get('Message', '')).lower() for k in FW_MARKS)]
    S.row('WALK_log_clean', not ours, {'flowworks_lines': ours[:5], 'lost': tap.lost, 'alive': alive, 'gaps': tap.gaps[:3],
          'warn_plus_all_mods': len(tap.entries)}, unmeasured=bool(tap.lost) or not alive)


# RIMMANDRAKE_REBUILD_FLOWWORKS_GARDEN_SCENE_MACHINES_NEVER_PIPED (visit 1, 2026-11-15): the draft spawned drill, pump, head,
# tank and faucet side by side with no pipe between them (nothing could fill the tank), ran one 60,000-tick advance on a colony
# nobody fed (the governor stopped at tick 480 on "starving"), and read only the tank: it had no converter or still, so none
# of the five owed blind-challenge cases nor the planted faults CALLER_CONV_DROPS_CLIPPED, CALLER_SPR_SPRAYS_WITHOUT_PUMP and
# DEF_STILL_RATE_TENFOLD could turn a row red. Now: five separate nets, each in the layout a live walk proved (tank, one
# unbroken pipe run, the pump and every machine built OVER the pipe: sprinkler_live.py's docstring), and a drill pouring into
# its dug outlet (a drill writes the cell it faces, never a pipe); one 60,000-tick window in governed 2,500-tick chunks (one
# sprinkler pulse each) with the colonists fed between chunks; every row UNMEASURED when its read is vacuous.
#   W  garden: tank, pump, head over potatoes             -> GARDEN_head_draws_its_net (spr_net_draw)
#   P  the same head with no pump on its net              -> GARDEN_no_pump_no_spray (CALLER_SPR_SPRAYS_WITHOUT_PUMP)
#   F  tank, pipe, faucet; a thirsty colonist beside it   -> GARDEN_faucet_drinks_from_its_tank (bottle_jobs: the faucet half)
#   C  toxic tank, drip filter, fresh tank                -> GARDEN_filter_keeps_its_rate (CONVERTER_RATE_REMAINDER_EATEN_BY_
#                                                            THE_CAP, CALLER_CONV_DROPS_CLIPPED)
#   S  salt tank, sun-pan still, fresh tank, open sky     -> GARDEN_still_within_its_def_rate (DEF_STILL_RATE_TENFOLD)
#   D  drill, its dug outlet, a set subsurface yield      -> GARDEN_drill_pours_its_yield, GARDEN_drill_charges_what_landed
#   Y  walled 5x5 yard, 3 cm poured at its centre         -> GARDEN_walled_yard_lies_level (SHEET_DRY_ISLAND_UNDER_A_POOL)
# Not here: bottle fill/empty/wash jobs and material choice (the faucet drink is the only bottle_jobs half staged); the
# subsurface survey roll (the scene SETS the yield, so it proves the pour, not which maps hold what).
GARDEN_W = 60000                       # ticks: 240 rare ticks, the converter's two-batch margin (selftest_garden_scene.py)
GARDEN_CHUNK = 2500                    # one sprinkler pulse (sprinkler_live.PULSE); colonists fed between chunks
CONV_MULT = 4.1                        # converterRateMultiplier for the scene (shipped slider 0.1..5): 820 units a rare tick
                                       # for the filter, so 6,000-unit batches leave a remainder each time (at 1.0 they divide
                                       # exactly and a caller dropping the clipped income could not show)
FILTER = dict(per=4800 * 10 / 240.0, inp=6000, out=2000)    # RM_DripFilter, ToxicWater filter step 600 L -> 200 L
STILL = dict(per=6000 * 10 / 240.0, inp=4000, out=2000)     # RM_SunPanStill, SaltWater distill 400 L -> 200 L
SPR_UNITS_PER_CELL = 5                 # sprinkler_live.UNITS_PER_CELL
DRILL_PER_CYCLE = 0.3                  # drillUnitsPerCycle: part levels, so a whole-level charge would burn the rest
MACH = 'RimMandrake.FlowWorks.Machinery.RM_MachinerySettings'
SHEET, SHEET_SET = 'RimMandrake.FlowWorks.Sheet.RM_SheetProofs', 'RimMandrake.FlowWorks.Sheet.RM_SheetSettings'
FRESH, TOXIC, SALT = 'RM_Liquid_FreshWater', 'RM_Liquid_ToxicWater', 'RM_Liquid_SaltWater'


def _conv_batches(rare, per, inp, keep=True, a0=0.0):
    """Batches a converter with ample input and room runs in `rare` rare ticks: CompLiquidConverter.CompTickRare's budget
    (one candidate; CapAccrued, ClippedIncome, AccruedAfterPick). keep=False is the planted CALLER_CONV_DROPS_CLIPPED."""
    acc, n = a0, 0
    for _ in range(rare):
        acc += per
        cap = min(acc, per + inp if per > inp else inp)
        clipped = max(0.0, min(acc - cap, per))
        acc = cap
        k = int(acc // inp)
        if k > 0:
            acc -= k * inp
            acc += clipped if keep else 0.0
            n += k
    return n


def _conv_window(dt, c, mult):
    """[lo, hi] batches a healthy converter may run in dt ticks (one rare tick of phase either way; up to one budget
    accrued before the fill)."""
    per, r = c['per'] * mult, int(dt // 250)
    return _conv_batches(max(r - 1, 0), per, c['inp']), _conv_batches(r + 1, per, c['inp'], a0=per + 1)


def _num(txt, key):
    import re
    m = re.search(r'\b%s=(-?[\d.Ee+-]+)' % key, txt or '')
    return float(m.group(1)) if m else None


def _garden(S):
    ox, oz = O
    W, P, F, Cn, St = (ox, oz), (ox, oz + 6), (ox, oz + 12), (ox, oz + 18), (ox, oz + 24)
    D, Y = (ox + 16, oz), (ox + 16, oz + 10)
    S.call('jawa/destroy_batch', rects='%d,%d,30,32' % (ox - 4, oz - 6), categories='Building,Plant,Item,Filth')
    S.call('jawa/set_terrain_batch', ops='Soil:%d,%d,30,32' % (ox - 4, oz - 6))
    S.call('jawa/set_roof_batch', ops='None:%d,%d,30,32' % (ox - 4, oz - 6))
    S.call('jawa/weather_set', weather='Clear', lockWeather=True)     # the still needs sun; the reload drops the lock
    S.setting('converterRateMultiplier', CONV_MULT, typ=MACH)
    S.setting('drillUnitsPerCycle', DRILL_PER_CYCLE)
    S.setting('sheetOverflowEnabled', True, typ=SHEET_SET)

    def build(ops, **kw):
        return S.call('jawa/build_batch', ops=';'.join(ops), faction='player', wipeExisting=False, **kw)

    def pipe(at, n):
        return ['RM_UniversalPipe:%d,%d' % (at[0] + i, at[1]) for i in range(2, 2 + n)]

    build(['RM_LiquidTank:%d,%d' % W] + pipe(W, 5) + ['RM_LiquidTank:%d,%d' % P] + pipe(P, 4)
          + ['RM_LiquidTank:%d,%d' % F] + pipe(F, 4) + ['RM_LiquidTankTall:%d,%d' % Cn] + pipe(Cn, 5)
          + ['RM_LiquidTank:%d,%d' % (Cn[0] + 7, Cn[1])] + ['RM_LiquidTankTall:%d,%d' % St] + pipe(St, 6)
          + ['RM_LiquidTank:%d,%d' % (St[0] + 8, St[1])])
    build(['RM_LiquidPump:%d,%d' % (W[0] + 3, W[1]), 'RM_SprinklerHead:%d,%d' % (W[0] + 5, W[1]),
           'RM_SprinklerHead:%d,%d' % (P[0] + 5, P[1]), 'RM_PipeFaucet:%d,%d' % (F[0] + 5, F[1]),
           'RM_DripFilter:%d,%d' % (Cn[0] + 4, Cn[1]), 'RM_SunPanStill:%d,%d' % (St[0] + 3, St[1]),
           'PowerConduit:%d,%d' % (W[0] + 3, W[1] - 1), 'PowerConduit:%d,%d' % (W[0] + 3, W[1] - 2),
           'Battery:%d,%d,0' % (W[0] + 3, W[1] - 4), 'RM_LiquidDrill:%d,%d,0' % D,
           'PowerConduit:%d,%d' % (D[0] - 1, D[1]), 'Battery:%d,%d,0' % (D[0] - 2, D[1] - 1)])
    build(['Wall:%d,%d' % (Y[0] + i, Y[1] + j) for i in range(-1, 6) for j in range(-1, 6) if i in (-1, 5) or j in (-1, 5)],
          stuff='Steel')
    for b in ((W[0] + 3, W[1] - 4), (D[0] - 2, D[1] - 1)):
        S.call('jawa/gss_stage', ops='kind=gss_charge|x=%d|z=%d' % b)
    S.call('jawa/set_plants', ops='Plant_Potato:%d,%d,5,3' % (W[0] + 4, W[1] + 1), density=1.0, growth=0.1)

    def tank(at, liquid=None, units=None):
        """(units, ticksGame) through ProofTank (its read form sets Store, the mode every tank here runs in)."""
        arg = '%d,%d;Store' % at + ('' if liquid is None else ';%s;%d' % (liquid, units))
        r = S.B.call('jawa/static_call', type=NSP, method='ProofTank', args=arg) or {}
        S.r['calls'].append({'tool': 'jawa/static_call', 'args': [NSP, 'ProofTank', arg], 'result': r})
        txt = str(r.get('result', ''))
        u = _num(txt, 'units') if txt.startswith('TANK') else None
        return (int(u) if u is not None else None), r.get('ticksGame')

    def thing(defn, at):
        th = S.call('jawa/list_things', defName=defn, rect='%d,%d,1,1' % at, limit=2).get('things') or []
        return th[0].get('id') if th else None

    def inspect(tid):
        if tid is None:
            return None
        for t in S.call('jawa/inspect_string', thingIds=tid).get('things') or []:
            return ' | '.join(t.get('inspect') or [])
        return None

    ids = {k: thing(d, at) for k, d, at in (('headW', 'RM_SprinklerHead', (W[0] + 5, W[1])),
                                           ('headP', 'RM_SprinklerHead', (P[0] + 5, P[1])),
                                           ('pump', 'RM_LiquidPump', (W[0] + 3, W[1])),
                                           ('faucet', 'RM_PipeFaucet', (F[0] + 5, F[1])),
                                           ('filter', 'RM_DripFilter', (Cn[0] + 4, Cn[1])),
                                           ('still', 'RM_SunPanStill', (St[0] + 3, St[1])), ('drill', 'RM_LiquidDrill', D))}
    missing = sorted(k for k, v in ids.items() if not v)
    require(not missing, 'not built: %s' % missing)
    drill = S.sc(NSP, 'ProofDrill', '%d,%d;%s;200' % (D[0], D[1], FRESH))
    require(drill.startswith('DRILL'), 'drill yield: %s' % drill)
    outlet = tuple(int(v) for v in drill.split('outlet=')[1].split()[0].split(','))
    S.dig([outlet], 8)
    S.ticks(250)                                   # sprinkler_live.COLD_WAIT: the pump's power switches on first

    fill = {'W': tank(W, FRESH, 100000), 'P': tank(P, FRESH, 100000), 'F': tank(F, FRESH, 100000),
            'C': tank(Cn, TOXIC, 250000), 'S': tank(St, SALT, 250000)}
    require(all(v[0] for v in fill.values()), 'a tank would not fill: %s' % fill)
    spill = S.sc(SHEET, 'ProofSheetSpill', '%d,%d;15000;Pump' % (Y[0] + 2, Y[1] + 2))
    drinker = S.pawn('Colonist', (F[0] + 5, F[1] + 1), 'player')
    S.call('jawa/pawn_need', pawn=drinker, action='need', need='RM_Thirst', level=0.05)
    d0 = S.sc(NSP, 'ProofDrill', '%d,%d' % D)

    def feed():
        for p in S.call('jawa/list_pawns', faction='player').get('pawns') or []:
            needs = dict((x.get('need'), x.get('level')) for x in
                         (S.B.call('jawa/pawn_need', pawn=p['id'], action='list') or {}).get('needs') or [])
            if needs.get('Food', 1.0) < 0.5:
                S.B.call('jawa/pawn_need', pawn=p['id'], action='need', need='Food', level=1.0)
            if p['id'] != drinker and needs.get('RM_Thirst', 1.0) < 0.3:
                S.B.call('jawa/pawn_need', pawn=p['id'], action='need', need='RM_Thirst', level=1.0)

    log = []                                       # one entry a chunk: tank units, drill read, yard read, head lines
    stop = None
    for k in range(GARDEN_W // GARDEN_CHUNK):
        feed()
        try:
            S.ticks(GARDEN_CHUNK)
        except Exception as e:                     # noqa: BLE001 - a GovernorStop: the window is broken, rows say so
            stop = repr(e)[:300]
            break
        log.append({'t': {n: tank(at) for n, at in (('W', W), ('P', P), ('F', F), ('C', Cn), ('C2', (Cn[0] + 7, Cn[1])),
                                                      ('S', St), ('S2', (St[0] + 8, St[1])))},
                    'drill': S.sc(NSP, 'ProofDrill', '%d,%d' % D),
                    'yard': S.sc(SHEET, 'ProofSheetRect', '%d;%d;5;5' % Y),
                    'headW': inspect(ids['headW']), 'headP': inspect(ids['headP'])})
    S.r['garden_log'] = log
    why = ('the clock stopped: %s; ' % stop) if stop else ''
    _garden_rows(S, fill, log, d0, spill, why, full=stop is None)


def _garden_rows(S, fill, log, d0, spill, why, full):
    import re
    u = lambda e, n: (e['t'][n][0] if e and e['t'].get(n) else None)            # noqa: E731
    tk = lambda e, n: (e['t'][n][1] if e and e['t'].get(n) else None)           # noqa: E731
    last = log[-1] if log else None

    # W: one pulse a chunk; chunk 0 holds the cold pulse, so chunks 1 -> 2 are one clean pulse
    if len(log) >= 3 and None not in (u(log[1], 'W'), u(log[2], 'W')):
        m = re.search(r'(\d+) cells', log[2]['headW'] or '')
        drop, cells = u(log[1], 'W') - u(log[2], 'W'), (int(m.group(1)) if m else None)
        S.row('GARDEN_head_draws_its_net', cells is not None and drop == cells * SPR_UNITS_PER_CELL
              and 'Spraying' in (log[2]['headW'] or ''), {'drop': drop, 'cells': cells, 'head': log[2]['headW']},
              unmeasured=cells is None or drop == 0)
    else:
        S.row('GARDEN_head_draws_its_net', False, why + 'fewer than three chunk reads', unmeasured=True)
    sprayed = len(log) >= 3 and None not in (u(log[1], 'W'), u(log[2], 'W')) and u(log[1], 'W') > u(log[2], 'W')

    # P: the same head with no pump on its net never sprays (and only means something when W's head did)
    p_end = u(last, 'P')
    S.row('GARDEN_no_pump_no_spray', p_end == fill['P'][0] and (last['headP'] or '').startswith('No pressure'),
          why + str({'filled': fill['P'][0], 'end': p_end, 'head': last and last['headP'], 'pumpedHeadSprayed': sprayed}),
          unmeasured=p_end is None or not sprayed or not full)

    # F: the faucet's tank is drawn by the thirsty colonist (no other fixture on its net)
    f_end = u(last, 'F')
    S.row('GARDEN_faucet_drinks_from_its_tank', f_end is not None and f_end < fill['F'][0],
          why + str({'filled': fill['F'][0], 'end': f_end}), unmeasured=f_end is None or not full)

    # C: input drawn in whole batches, the output made to match, the count inside the healthy window
    c_end, c2_end = u(last, 'C'), u(last, 'C2')
    if None in (c_end, c2_end, tk(last, 'C'), fill['C'][1]) or not full:
        S.row('GARDEN_filter_keeps_its_rate', False, why + 'unreadable %s' % [c_end, c2_end], unmeasured=True)
    else:
        took, dt = fill['C'][0] - c_end, tk(last, 'C') - fill['C'][1]
        lo, hi = _conv_window(dt, FILTER, CONV_MULT)
        n = took / float(FILTER['inp'])
        S.row('GARDEN_filter_keeps_its_rate', n == int(n) and lo <= n <= hi and c2_end == int(n) * FILTER['out'],
              {'batches': n, 'window': [lo, hi], 'made': c2_end, 'ticks': dt}, unmeasured=took == 0)

    # S: no chunk draws more than the def's rate could at full sun; it must have run at all
    drops, bad = [], []
    for a, b in zip([{'t': {'S': fill['S']}}] + log, log):
        if None in (u(a, 'S'), u(b, 'S'), tk(a, 'S'), tk(b, 'S')):
            bad.append('unreadable'); continue
        dt, d = tk(b, 'S') - tk(a, 'S'), u(a, 'S') - u(b, 'S')
        cap = (int(((dt // 250) + 1) * STILL['per'] * CONV_MULT + STILL['inp']) // STILL['inp']) * STILL['inp']
        drops.append(d)
        if d > cap:
            bad.append('chunk drew %d over %d ticks, the def allows %d' % (d, dt, cap))
    made = u(last, 'S2')
    S.row('GARDEN_still_within_its_def_rate', not bad and made == sum(drops) // STILL['inp'] * STILL['out'],
          why + str({'drops': drops, 'bad': bad[:3], 'made': made}), unmeasured=not drops or not sum(drops) or 'unreadable' in bad)

    # D: the drill pours, and the reserve it spent is what landed plus what it still holds
    reads = [d0] + [e['drill'] for e in log]
    r0 = _num(d0, 'reserve')
    pick = next((x for x in reads[1:] if (_num(x, 'outletUnits') or 0) > 0), None)
    S.row('GARDEN_drill_pours_its_yield', pick is not None, why + str(reads[-1])[:200],
          unmeasured=not log or r0 is None)
    if pick is None or r0 is None:
        S.row('GARDEN_drill_charges_what_landed', False, why + 'nothing landed: %s' % str(reads[-1])[:200], unmeasured=True)
    else:
        # deltas from the baseline read: the drill may already have poured during the staging ticks
        spent = r0 - _num(pick, 'reserve')
        landed = _num(pick, 'outletUnits') - (_num(d0, 'outletUnits') or 0.0)
        pend = _num(pick, 'pending')
        gain = pend - (_num(d0, 'pending') or 0.0)
        S.row('GARDEN_drill_charges_what_landed', abs(spent - landed - gain) <= 0.02 + 0.01 * spent and pend >= -1e-4,
              {'spent': spent, 'landed': landed, 'pendingGain': gain, 'base': d0[:200], 'read': pick[:200]},
              unmeasured=spent <= 0)

    # Y: the walled yard's 3 cm lies level over all 25 squares (no dry island); the latest read still holding half of it
    took = _num(spill, 'accepted') if str(spill).startswith('SPILL') else None
    good = [e['yard'] for e in log if took and (_num(e['yard'], 'dl') or 0) >= took / 2]
    y = good[-1] if good else (log[-1]['yard'] if log else None)
    dl, wet, mx = _num(y, 'dl'), _num(y, 'wet'), _num(y, 'maxDl')
    S.row('GARDEN_walled_yard_lies_level', bool(good) and wet == 25 and mx <= dl / wet + 2,
          why + str({'spill': spill[:80], 'read': y}), unmeasured=not good)


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
    coated = 'Coated' in str(h) or 'coated' in str(h)
    S.row('COAT_named_condition', coated, str(h)[:200])
    S.walk(col, water[-1], 600)
    h2 = S.call('jawa/list_pawns', faction='player', rect='%d,%d,1,1' % water[-1], includeHealth=True)
    # RIMMANDRAKE_BUILD_FLOWWORKS_COATING_WASH_PASSED_ON_NOTHING (visit 1 passed this with no coat on the pawn): washing
    # passes only a coat seen before the water, and only on a read that found the pawn
    found = "'pawns': [{" in str(h2) or '"pawns": [{' in str(h2)
    S.row('COAT_water_washes_it', coated and found and 'oated' not in str(h2),
          ('no coat before the water: nothing to wash; ' if not coated else '') + str(h2)[:200])


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
            out = STAGE3_SCENES[a.scene](B, snapshot, reload_snapshot, res, save_mid=save_occupied, load_mid=load_occupied)
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
