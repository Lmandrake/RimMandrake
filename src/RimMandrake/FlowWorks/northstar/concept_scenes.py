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
PRISON_HOLD_TICKS, PRISON_HOLD_STEP = 5000, 2500    # the hold after capture, feeding and the awake meal; read each step


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
    The hold uses real ticks, never time_set_ticks. Finally runs even on an assertion.
    The hold is PRISON_HOLD_TICKS, not a day (RIMMANDRAKE_SHRINK_FLOWWORKS_SCENES_HUNG_BRIDGE_RAN_27_TIMES, table.md
    section 1: a day adds only other ways to spoil it); each read asks held (RM_SuperdeepTrap.IsHeld: no way out of
    the hole), and the ground-bed prisoner of the last phase is its foil (held False).
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
        # The hold: normal work, observed at intervals, no need refills or healing; every read asks for the way out.
        start = clock()
        receipt['day'] = []
        for _ in range(PRISON_HOLD_TICKS // PRISON_HOLD_STEP):
            step(PRISON_HOLD_STEP)
            states = [state(p) for p in raiders]
            for s in states:
                require(s['kept'] == 'True' and s['dead'] == 'False', 'prisoner escaped or died: '+str(s))
                require((int(s['x']), int(s['z'])) in PIT, 'prisoner moved out of hole')
                require(s.get('held') == 'True', 'the hole does not hold the prisoner (an escape route): '+str(s))
                require(float(s['food']) > 0, 'prisoner starved')
            receipt['day'].append({'tick': clock(), 'prisoners': states})
        receipt['day_ticks'] = clock()-start
        require(receipt['day_ticks'] >= PRISON_HOLD_TICKS, 'the hold was cut short')
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
        require(receipt['ordinary_off'].get('held') == 'False',
                'the held read calls a prisoner in a ground bed held: it cannot see a way out (foil)')
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


# sc_source_pays. Visit 1 (2026-11-15) read every row on 'OK -': the draft assumed a natural pond and an edge lake the calm
# site does not have, never dug the pond, dug its moat two rows short of it, and passed SRC_flow_stops_when_empty on twenty
# undug zeros (RIMMANDRAKE_REBUILD_FLOWWORKS_SOURCE_PAYS_SCENE_POND_NEVER_THERE). Now the pond is dug and filled brim-full
# (a 20 x 10 basin: a 0.5 m shelf ring of 40 squares round a 2 m core, one surface; the litres are asserted), a dry 3 m moat
# joined to its east side draws it, a sink at tap 0 is the control, an unlimited sink empties it, locked rain refills it
# (read three times: some, not instant, rising). The bar (tree.json source_pays_and_refills, no_full_source_after_draw): the
# pond's litres AND its wet-square count fall, an emptied pond stops paying, rain refills it with visible progress, an
# edge body reads Endless and never drops. The calm site has no limitless body: that row reads UNMEASURED with its reason
# (the read is owed on the river site), never a faked endless source. A vacuous read (REFUSED, all-zero, an event that never
# happened: no draw, no rain) is UNMEASURED, never PASS. Offline half: selftest_source_pays_scene.py.
SRC_MAPCTL = 'RimMandrake.FlowWorks.MapControls.RM_MapControls'
SRC_CORE_LV, SRC_SHELF_LV, SRC_MOAT_LV, SRC_MOAT_N = 4, 1, 6, 60      # notches (0.5 m): core 2 m, shelf 0.5 m, moat 3 m
SRC_LAKE_PROBES = ((105, 135), (100, 130), (38, 5))   # river site cells that read Endless (visit_1 sc_river__endless_read)
# The bound on following the film to 0 L. Danger: a sink whose draw never ends (an endless pond, a creeping film) holds the
# bridge forever. Evidence (visit_2/evidence/exp/source_pays_long.json): under the wet line the sink drew 2.98 notches in 50
# pulses with ~17 notches of film left (53 L at the probe, 160 core squares), so a draw that falls with the film needs about
# ln(17 / 0.0002) / (2.98 / 50 / 17) ~ 3,200 pulses to the last dL. Past the bound the row reads UNMEASURED, never PASS.
SRC_FILM_PULSES = 4000


def _src_wet(dls, wet_dl):
    """How many squares stand wetter than wet_dl; None when the vector cannot carry a verdict (absent or all zero)."""
    return None if _vacuous(tuple(dls)) or any(v is None for v in dls) else sum(1 for v in dls if v > wet_dl)


def _src_drained(S, tid):
    """The sink's own drained total from Report(); None when the report or its line is missing."""
    import re
    rep = S.sc(SRC_MAPCTL, 'Report')
    m = re.search(r'sink %s\b[^\n]*?drained=([\d.]+)' % re.escape(tid), rep) if tid else None
    return float(m.group(1)) if m else None


def _src_sink(S, at, rate):
    """Place an RM_FlowSink (rate < 0 = unlimited); its ThingID, or None with the reply when the game refused."""
    rep = S.sc(SRC_MAPCTL, 'PlaceSink', '%d,%d|any|%g' % (at[0], at[1], rate))
    parts = rep.split()
    return (parts[2] if rep.startswith('OK sink ') and len(parts) > 2 else None), rep


def _src_rain(S):
    r = S.call('jawa/weather_get')
    return ((r or {}).get('weather') or {}).get('rainRate')


def _src_lake(S):
    """SRC_lake_reads_endless: only on a map with a limitless body; the calm site has none, so it reads UNMEASURED."""
    r = S.call('jawa/flowworks_pulse', count=1, x=0, z=0, w=0, h=0, includeBodies=True)
    pulses = (r or {}).get('pulses') or []
    bodies = (pulses[-1].get('bodies') if pulses else None)
    if bodies is None:
        return S.row('SRC_lake_reads_endless', False, 'no body census came back: %s' % str(r)[:200], unmeasured=True)
    endless = [b for b in bodies if b.get('limitless')]
    if not endless:
        return S.row('SRC_lake_reads_endless', False, 'this map has no limitless body (%d bodies, none limitless): the calm site '
                     'has no edge lake or river, so the Endless read is owed on the river site (visit_1/evidence/'
                     'sc_river__endless_read.txt); never faked' % len(bodies), unmeasured=True)
    reads = [(c, S.sc(NSP, 'ProofReadout', '%d,%d' % c)) for c in SRC_LAKE_PROBES]
    hit = next((c for c, t in reads if 'ndless' in t), None)
    if hit is None:
        return S.row('SRC_lake_reads_endless', False, ('limitless bodies %s but no probe cell reads Endless' %
                                                       [b.get('id') for b in endless], reads), unmeasured=True)
    stock0 = {b.get('id'): b.get('stock') for b in endless}
    moat = _line(hit[0] + 1, hit[1], 10)
    S.dig(moat, 2)
    r = S.call('jawa/flowworks_pulse', count=60, x=0, z=0, w=0, h=0, includeBodies=True)
    pulses = (r or {}).get('pulses') or []
    stock1 = {b.get('id'): b.get('stock') for b in (pulses[-1].get('bodies') or [] if pulses else [])}
    took = S.dl(moat)
    if _vacuous(tuple(took)):
        return S.row('SRC_lake_reads_endless', False, ('the moat beside the Endless body took nothing: no draw to judge', took),
                     unmeasured=True)
    S.row('SRC_lake_reads_endless', all(stock1.get(k) is not None and stock1[k] >= v for k, v in stock0.items()),
          (hit, stock0, stock1, sum(took)))


def _src_lake_site(S):
    """SRC_lake_reads_endless needs an edge body, which the calm site has not: read it on the scene's own map when that map
    has a limitless body, else on the river site (test_site_saves 'river', RM_TestSite_river_v3, built on the fw_gss_sitting
    tier), loaded here; the scene's finally reloads its calm snapshot after. HARNESS (visit 4, 2026-11-21): the row read
    UNMEASURED on every run since visit 1 because nothing ever took it to the river site. A river site that does not load
    verified is UNMEASURED (SITE), never a pass."""
    r = S.call('jawa/flowworks_pulse', count=1, x=0, z=0, w=0, h=0, includeBodies=True)
    pulses = (r or {}).get('pulses') or []
    bodies = pulses[-1].get('bodies') if pulses else None
    if bodies is not None and any(b.get('limitless') for b in bodies):
        return _src_lake(S)
    import test_site_saves as T
    loaded = T.load_site(S.B.call, 'river')
    S.r['lake_site'] = {k: loaded.get(k) for k in ('site', 'save', 'verified', 'problems')}
    if not loaded.get('verified'):
        return S.row('SRC_lake_reads_endless', False, 'the river site did not load verified (it is built on the fw_gss_sitting '
                     'tier): %s' % str(loaded.get('problems'))[:240], unmeasured=True)
    return _src_lake(S)


def _src_pond(S):
    """The pond every source scene stages: a 20 x 10 basin dug and filled brim-full (a 0.5 m shelf ring round a 2 m core,
    one surface), clear weather locked so no rain falls while draws are read. -> P: the cells, the probe read and the
    full pond's readings (full litres, its squares' dL, the wet line, the wet-square count)."""
    import types
    P = types.SimpleNamespace()
    P.core = [(O[0] + i, O[1] + j) for i in range(20) for j in range(1, 9)]
    P.shelf = [(O[0] + i, O[1] + j) for i in range(20) for j in (0, 9)]
    P.pond = P.shelf + P.core
    P.probe = (O[0] + 10, O[1] + 5)
    P.moat = _line(O[0] + 20, O[1] + 5, SRC_MOAT_N)        # joined to the core square (O+19, O+5)
    P.sink_at = (O[0] - 1, O[1] + 5)                       # undug, beside the core square (O, O+5): the sink reaches it
    P.read = lambda: _litres(S.sc(NSP, 'ProofReadout', '%d,%d' % P.probe))
    S.call('jawa/weather_set', weather='Clear', lockWeather=True)   # no rain while the draws are read
    S.dig(P.shelf, SRC_SHELF_LV); S.dig(P.core, SRC_CORE_LV)
    S.fill(P.shelf, SRC_SHELF_LV * 0.5, WATER); S.fill(P.core, SRC_CORE_LV * 0.5, WATER)
    S.pulse(5)
    P.full, P.d0 = P.read(), S.dl(P.pond)
    require(P.full is None or P.full > 0, 'the filled pond reads no water at %s: %s' % (P.probe, P.full))
    P.wet_dl = ((max(v for v in P.d0 if v is not None) / (SRC_CORE_LV * 10.0))
                if not _vacuous(tuple(P.d0)) and None not in P.d0 else 0)
    P.wet0 = _src_wet(P.d0, P.wet_dl)
    P.blind = P.wet0 is None                               # the filled pond's own squares read empty: the rect is blind
    return P


def _src_draw_rows(S, P):
    """SRC_pond_drops, SRC_shore_recedes (a dry 3 m moat joined to the pond draws it: litres AND wet squares fall) and
    SRC_control_tap_zero (a sink at tap 0 takes nothing). -> the litres after the moat's draw."""
    full, wet_dl, wet0, read = P.full, P.wet_dl, P.wet0, P.read
    S.dig(P.moat, SRC_MOAT_LV); S.pulse(200)
    drawn, d1, took = read(), S.dl(P.pond), S.dl(P.moat)
    wet1 = _src_wet(d1, wet_dl)
    paid = not _vacuous(tuple(took)) and None not in took
    if full is None or drawn is None or P.blind:
        S.row('SRC_pond_drops', False, ('the readout carried no litres or the pond squares read empty', full, drawn, P.d0[:4]),
              unmeasured=True)
    else:
        S.row('SRC_pond_drops', paid and drawn < full, ('litres', full, drawn, 'moat took', sum(v or 0 for v in took)))
    if wet0 is None or wet1 is None:
        S.row('SRC_shore_recedes', False, ('the wet-square vector was empty or all zero', P.d0[:4], d1[:4]), unmeasured=True)
    else:   # the bar's no_full_source_after_draw: fewer wet squares after the draw than before, not just a smaller number
        S.row('SRC_shore_recedes', paid and wet1 < wet0, ('wet squares', wet0, wet1))
    tid, rep = _src_sink(S, P.sink_at, 0)
    if tid is None:
        S.row('SRC_control_tap_zero', False, ('the tap-0 sink was not placed', rep), unmeasured=True)
    else:
        S.pulse(60)
        held, dz = read(), _src_drained(S, tid)
        if held is None or dz is None or drawn is None:
            S.row('SRC_control_tap_zero', False, ('no litres or no drained total', drawn, held, dz), unmeasured=True)
        else:   # scenes.json control: the Sink tap set to zero -> the pond does not drop beyond the moat's take
            S.row('SRC_control_tap_zero', dz == 0 and held >= drawn * 0.98, ('litres', drawn, held, 'drained', dz))
        S.sc(SRC_MAPCTL, 'Remove', tid)
    return drawn


def _src_empty_rows(S, P):
    """SRC_flow_stops_when_empty: an unlimited sink draws the pond to its wet line, then follows the film to 0 L and 0 dL;
    PASS only on a pond at 0 L and 0 dL whose drained total then stands still."""
    read, wet_dl, pond, blind = P.read, P.wet_dl, P.pond, P.blind
    tid, rep = _src_sink(S, P.sink_at, -1)
    if tid is None:
        S.row('SRC_flow_stops_when_empty', False, ('the unlimited sink was not placed', rep), unmeasured=True)
        return
    # Draw to the wet line first, followed while the sink still drains (visit 3, 2026-11-21: after a flat 500 pulses the
    # pond held 208 L and the sink was still drawing, 502.6 -> 514.3, so the row read a pond not yet empty as one that
    # never stops: HARNESS). Same bound as the film follow: a pond not dry by then never empties (FAIL, the endless_pond case).
    wet_pulses = 0
    while wet_pulses < SRC_FILM_PULSES:
        before = _src_drained(S, tid)
        S.pulse(100); wet_pulses += 100
        if all(v is not None and v <= wet_dl for v in S.dl(pond)) or before is None or _src_drained(S, tid) == before:
            break
    dry = all(v is not None and v <= wet_dl for v in S.dl(pond))
    # His ruling POND_PUMP_FIX_LAST_DROP_COUNTS ('ponds pump to last dL'): under the wet line the sink still draws the
    # film, slowly, so the draw is followed to 0 L and 0 dL, not stopped at the wet line
    # (RIMMANDRAKE_REPIN_SOURCE_PAYS_FILM_IS_NOT_A_LEAK). A chunk that draws nothing ends the follow (stuck film).
    film = 0
    while dry and film < SRC_FILM_PULSES:
        left = read()
        if left is None or (left <= 0 and not any(S.dl(pond))):
            break
        before = _src_drained(S, tid)
        S.pulse(100); film += 100
        if before is None or _src_drained(S, tid) == before:
            break
    dr1, dp = _src_drained(S, tid), S.dl(pond)
    S.pulse(50)
    dr2, empty = _src_drained(S, tid), read()
    why = ('pond dry', dry, 'drained', dr1, dr2, 'litres', empty, 'max dL', max(dp) if None not in dp else dp,
           'film pulses', film, 'wet-line pulses', wet_pulses)
    if dr1 is None or dr2 is None or not dr1 > 0 or blind or empty is None or None in dp:
        S.row('SRC_flow_stops_when_empty', False, ('no drained total, no litres, the sink drained nothing (the draw never '
                                                   'happened) or the pond squares read empty when full', rep, why, blind),
              unmeasured=True)
    elif dry and (empty > 0 or any(dp)) and dr2 > dr1 and film >= SRC_FILM_PULSES:
        S.row('SRC_flow_stops_when_empty', False, ('the film was still draining after %d pulses: the last dL was not '
                                                   'reached in the bound' % film,) + why, unmeasured=True)
    else:   # PASS only on a pond at 0 L and 0 dL whose drained total then stands still
        S.row('SRC_flow_stops_when_empty', dry and empty == 0 and not any(dp) and dr2 == dr1, why)
    rm = S.sc(SRC_MAPCTL, 'Remove', tid)
    require(rm.startswith('OK removed'), 'the sink would not come off before the rain: %s' % rm)


def _src_refill_long(S, P):
    """sc_source_pays' rain: 14,000 ticks of locked rain on the emptied pond, read three times (some, not instant, rising)."""
    read, full = P.read, P.full
    S.call('jawa/weather_set', unlock=True)
    S.call('jawa/weather_set', weather='Rain', lockWeather=True)
    start = read()
    S.ticks(4000)
    rain, s1 = _src_rain(S), read()
    S.ticks(5000); s2 = read()
    S.ticks(5000); s3 = read()
    S.call('jawa/weather_set', unlock=True)
    series = (start, s1, s2, s3)
    if not rain:
        S.row('SRC_refill_visible', False, ('no rain fell (rainRate %s): the refill was never asked' % rain, series),
              unmeasured=True)
    elif None in series or full is None:
        S.row('SRC_refill_visible', False, ('the readout carried no litres', series), unmeasured=True)
    else:   # some water came back, not all at once (false_pass: refill is instant), and it kept rising
        S.row('SRC_refill_visible', s3 > start and s1 < full and s1 <= s2 <= s3 and s3 > s1, ('litres', series, 'full', full))


def _source_pays(S):
    """sc_source_pays, the composite (his look; it decides no bar since the split, RIMMANDRAKE_SHRINK_FLOWWORKS_SCENES_
    HUNG_BRIDGE_RAN_27_TIMES): sc_source_draws, the empty-pond follow, sc_source_refills' long form and sc_lake_endless
    on one run."""
    P = _src_pond(S)
    _src_draw_rows(S, P)
    _src_empty_rows(S, P)
    _src_refill_long(S, P)
    _src_lake_site(S)


# sc_source_pays split in three (RIMMANDRAKE_SHRINK_FLOWWORKS_SCENES_HUNG_BRIDGE_RAN_27_TIMES, design/specs/2026-11-24-
# oversized-scenes/table.md section 1: about eight claims, two mod lists, up to 8,000 pulses and 14,000 ticks; 13 runs, 10 not
# passed). sc_source_draws: one draw and the tap-0 control. sc_source_refills: rain on an emptied pond, two reads 1,000 ticks
# apart once the rain reaches it. sc_lake_endless: the edge body on the river site (its own tier, fw_gss_sitting).
SRC_RAIN_STEP = 500       # ticks between reads, before the first water and while waiting for the next rise
# The bound on waiting for the rain to reach the pond. Danger: a pond the rain never reaches holds the bridge forever.
# Measured need: visit 12 (2026-11-24, sc_source_pays_20261124T231728) read the emptied pond 0 L 4,000 ticks into locked
# rain and 2,327 L at 9,000; this is ten times 9,000. Past it the row reads FAIL (the rain fell, the pond never refilled).
# The same bound holds the wait for the next rise after the first water: rain lands in lumps more than 1,000 ticks apart
# (live 2026-11-25, bundle_shrink_20261125: 0 L until 4,500 ticks, then 1,250 L, and 1,250 L again 1,000 ticks later).
SRC_RAIN_ONSET_MAX = 90000


def _source_draws(S):
    """sc_source_draws: a moat drawing a full pond lowers its litres and pulls its shore back; a sink at tap 0 takes
    nothing (the control: no hidden draw). The emptied pond's stop is decided offline (T_STOCK, PY_PUMP_DRAW_CONSERVES)."""
    P = _src_pond(S)
    _src_draw_rows(S, P)
    S.call('jawa/weather_set', unlock=True)


def _src_brim(hole_txt, wet_txt):
    """The brim litres of the probe cell: the hole's depth (from its empty readout 'OK Hole 2 m') times the readout's own
    litres per metre (from a wet readout 'Water 0.40 m (800 L)'); None when either line cannot say."""
    import re
    h = re.match(r'OK Hole ([\d.]+) m', str(hole_txt or ''))
    w = re.search(r'Water\s+([\d.]+)\s*m\s*\(([\d,.]+)\s*L\)', str(wet_txt or ''))
    if not h or not w or float(w.group(1)) <= 0:
        return None
    return float(h.group(1)) * float(w.group(2).replace(',', '')) / float(w.group(1))


def _source_refills(S):
    """sc_source_refills: rain refills an emptied pond with visible progress. The pond is dug and left empty, rain is
    locked on, and once the probe first reads water it reads more again later (the next lump of rain), and the first read
    is below the hole's brim (false pass: the refill is instant)."""
    core = [(O[0] + i, O[1] + j) for i in range(20) for j in range(1, 9)]
    shelf = [(O[0] + i, O[1] + j) for i in range(20) for j in (0, 9)]
    probe = '%d,%d' % (O[0] + 10, O[1] + 5)
    S.call('jawa/weather_set', weather='Clear', lockWeather=True)
    S.dig(shelf, SRC_SHELF_LV); S.dig(core, SRC_CORE_LV)
    S.pulse(2)
    hole = S.sc(NSP, 'ProofReadout', probe)
    start = _litres(hole)
    S.call('jawa/weather_set', unlock=True)
    S.call('jawa/weather_set', weather='Rain', lockWeather=True)
    waited, first_txt, first = 0, None, None
    while waited < SRC_RAIN_ONSET_MAX:
        S.ticks(SRC_RAIN_STEP); waited += SRC_RAIN_STEP
        first_txt = S.sc(NSP, 'ProofReadout', probe)
        first = _litres(first_txt)
        if first is None or first > 0:
            break
    rain = _src_rain(S)
    rose, second = 0, first
    while first and rose < SRC_RAIN_ONSET_MAX:
        S.ticks(SRC_RAIN_STEP); rose += SRC_RAIN_STEP
        second = _litres(S.sc(NSP, 'ProofReadout', probe))
        if second is None or second != first:
            break
    S.call('jawa/weather_set', unlock=True)
    brim = _src_brim(hole, first_txt)
    why = {'litres': (start, first, second), 'brim': brim, 'onset_ticks': waited, 'rise_ticks': rose, 'rainRate': rain,
           'hole': hole[:60]}
    if not rain:
        S.row('SRC_refill_visible', False, ('no rain fell: the refill was never asked', why), unmeasured=True)
    elif start != 0:
        S.row('SRC_refill_visible', False, ('the dug pond did not read empty before the rain', why), unmeasured=True)
    elif first == 0:
        S.row('SRC_refill_visible', False, ('the rain fell for %d ticks and the pond never refilled' % waited, why))
    elif None in (first, second, brim):
        S.row('SRC_refill_visible', False, ('the readout carried no litres or no depth', why), unmeasured=True)
    else:   # some water came back, not all at once, and it kept rising
        S.row('SRC_refill_visible', 0 < first < brim and second > first, why)


# sc_pawn_height. Visit 1 (2026-11-15) dug each pad ONE row tall, so the shipped lip clamp (pitSinkClampEnabled, on) held the
# colonist at sink 0 on every pad: its feet sat on the south lip (RM_PitDrawMath.ClampSinkToLip, room 0), and 17 zeros PASSED
# because a flat vector is sorted. The swim row read ProofReadout (a cell readout, no swim state) on a staircase whose water
# had run to the deep end, and the control read the pawn still down in the flooded pit (RIMMANDRAKE_REBUILD_FLOWWORKS_PAWN_
# HEIGHT_SCENE_ZEROS_PASSED). Now each pad is a PH_ROWS-tall column walked on its north row (room PH_ROWS - 1 cells: the
# shipped clamp never binds, no setting is poked), every read is checked against the pad it claims, the swim is a separate
# 4 m pool held at 2 m and read by RM_Swim.ProofSwim (deepCell, exhaustion), and a vacuous read is UNMEASURED, never PASS.
# RIMMANDRAKE_SHRINK_FLOWWORKS_SCENES_HUNG_BRIDGE_RAN_27_TIMES (table.md section 1: 46 orders of one cell each, 11 runs and 5
# not passed, 351 s in visit 12): ONE order over five pads (D0..D4) and ONE order back, the sink read every tick. Walls on the
# rows beside the pad block keep the path on the pads (a path round them would never descend). The mod draws a walking pawn's
# sink between the two cells of its step (RM_Patch_PitDepthDrawOffset.SinkOf), so on a line that deepens cell by cell the
# sink rises with time: the lowest read on each depth on the way out and the highest on the way back are that depth's sink.
PH_PADS, PH_ROWS, PH_WAIT, PH_SWIM_M, PH_SWIM_TICKS = 5, 3, 400, 2.0, 1500
PH_STEP = 1             # the offset is read every tick of both orders
PH_SETTLE = 60          # ticks standing at the end of an order before its still read (the tween catches up)
PH_AGREE = 0.01         # m: the way-out and way-back reads of one depth agree within this (one tick of a step's tween)
# The bound on one order. Danger: a pawn that never arrives (a refused path, a stuck pawn) holds the bridge forever.
# Measured need: none yet for one order over seven cells; a colonist crosses a cell in about 13 ticks, so a leg needs about
# 100; ten times that. Past it the row reads UNMEASURED (the pad was never reached), never PASS.
PH_LEG_TICKS = 1000


def _ph_read(S, pid):
    """ProofPawnSink as a dict (cell as an (x, z) tuple, sink/drawDz as floats); None for a reply that cannot carry a verdict."""
    txt = S.sc(EXC, 'ProofPawnSink', pid)
    d = kv(txt)
    if not txt.startswith('SINK ') or d.get('id') != pid:
        return None
    try:
        return {'cell': tuple(int(v) for v in d['cell'].split(',')), 'depth': int(d['depth']), 'sink': float(d['sink']),
                'drawDz': float(d['drawDz']), 'enabled': d.get('enabled'), 'moving': d.get('moving')}
    except (KeyError, ValueError):
        return None


def _ph_walk(S, pid, cells, miss=None):
    """Walk pid to each cell in turn; the read there, or None when it did not arrive or the read is vacuous. Each None's
    target and actual read go on `miss` when given, so a row can say where the pawn really stood."""
    out = []
    for c in cells:
        S.walk(pid, c, PH_WAIT)
        r = _ph_read(S, pid)
        ok = r and r['cell'] == tuple(c)
        out.append(r if ok else None)
        if not ok and miss is not None:
            miss.append({'to': tuple(c), 'read': r})
    return out


def _ph_swim(S, pid, pool):
    """(ProofSwim kv, raw) for pid wherever it is in the pool; (None, why) when it is not there or the read is not its own."""
    r = _ph_read(S, pid)
    if not r or r['cell'] not in pool:
        return None, 'not in the pool: %s' % ((r and r['cell']),)
    txt = S.sc(SWIMP, 'ProofSwim', '%d,%d' % r['cell'])
    return (kv(txt) if txt.startswith('SWIM ' + pid + ' ') else None), txt


def _ph_leg(S, pid, to):
    """One order to `to`, the sink read every tick until the pawn stands there, then PH_SETTLE ticks still. -> (the reads
    of the walk (None for a vacuous read), the still read at the end or None when it never arrived)."""
    S.call('jawa/order_pawn', pawnId=pid, x=to[0], z=to[1], waitTicks=0, draft=True)
    reads, t = [], 0
    while t < PH_LEG_TICKS:
        S.ticks(PH_STEP); t += PH_STEP
        r = _ph_read(S, pid)
        reads.append(r)
        if r and r['cell'] == tuple(to) and r.get('moving') != 'True':
            S.ticks(PH_SETTLE)
            end = _ph_read(S, pid)
            return reads, (end if end and end['cell'] == tuple(to) else None)
    return reads, None


def _ph_by_depth(reads, pick):
    """{depth: pick(sinks read standing on that depth)} over the reads that carry a verdict."""
    out = {}
    for r in reads:
        if r is not None:
            out.setdefault(r['depth'], []).append(r['sink'])
    return {d: pick(v) for d, v in out.items()}


def _ph_monotone(reads, up):
    v = [r['sink'] for r in reads if r is not None]
    return all((b >= a - 1e-4) if up else (b <= a + 1e-4) for a, b in zip(v, v[1:]))


def _pawn_height(S):
    x0, z0 = O
    walk_z = z0 + PH_ROWS - 1
    start, far = (x0 - 2, walk_z), (x0 + PH_PADS - 1, walk_z)
    # The calm site's Drago tree stands at (64,57) (probed 2026-11-20): clear plants and items off the whole staging block.
    cleared = S.call('jawa/destroy_batch', rects='%d,%d,%d,%d' % (x0 - 3, z0 - 1, PH_PADS + 4, PH_ROWS + 2),
                     categories='Plant,Item')
    for i in range(PH_PADS):
        S.dig([(x0 + i, z0 + j) for j in range(PH_ROWS)], i)       # pad i: D=i half-metre levels (D0 is undug ground)
    # walls on the row north of the pads and the row south of them, from behind the start to past the far pad
    S.call('jawa/build_batch', ops=';'.join('Wall:%d,%d' % (x, z) for x in range(x0 - 3, x0 + PH_PADS + 1)
                                           for z in (z0 - 1, z0 + PH_ROWS)), stuff='Steel', faction='player',
           wipeExisting=False)
    col = S.pawn('Colonist', start, 'player')
    S.call('jawa/set_draft', pawnId=col, drafted=True)             # drafted: it stands where it was put until ordered
    S.ticks(PH_SETTLE)
    still0 = _ph_read(S, col)
    out, end_far = _ph_leg(S, col, far)
    back, end_home = _ph_leg(S, col, start)
    lo_out = _ph_by_depth(out, min)
    hi_back = _ph_by_depth(back, max)
    depths = list(range(PH_PADS))
    detail = {'out': [None if r is None else (r['cell'][0] - x0, r['depth'], r['sink']) for r in out],
              'back': [None if r is None else (r['cell'][0] - x0, r['depth'], r['sink']) for r in back],
              'lowest_out': lo_out, 'highest_back': hi_back, 'end_far': end_far and end_far['sink'],
              'end_home': end_home and end_home['sink']}
    seen = [r for r in out + back if r is not None]
    unreached = end_far is None or end_home is None or any(d not in lo_out or d not in hi_back for d in depths)
    flat = bool(seen) and all(abs(r['sink']) < 1e-3 for r in seen)
    ok = (not unreached and _ph_monotone(out, True) and _ph_monotone(back, False)
          and abs(lo_out[0]) < 1e-3 and lo_out[1] > 1e-3
          and all(lo_out[d + 1] > lo_out[d] + 1e-3 and hi_back[d + 1] > hi_back[d] + 1e-3 for d in depths[:-1])
          and all(abs(lo_out[d] - hi_back[d]) <= PH_AGREE for d in depths)
          and abs(end_far['sink'] - hi_back[PH_PADS - 1]) <= PH_AGREE and abs(end_home['sink']) < 1e-3
          and all(abs(r['drawDz'] + r['sink']) < 0.05 for r in (end_far, end_home)))
    if unreached:
        detail['unreached'] = 'the pawn did not stand on every pad both ways, or an order never arrived'
    if flat:
        detail['why'] = 'every sink read 0: the instrument has not shown it can see a sink'
    S.row('PH_offset_follows_depth', ok, detail, unmeasured=unreached or flat)

    # the control: the same orders cross two undug cells before the pads (x0 - 2, x0 - 1) and end on one; a sink applied
    # by the walking step, not the cell's depth, shows there. No swim on undug ground.
    ground = [r for r in out + back if r is not None and r['cell'][0] < x0]
    sw = S.sc(SWIMP, 'ProofSwim', '%d,%d' % start)
    dry = kv(sw).get('deepCell') == 'False' if sw.startswith('SWIM ' + col + ' ') else None
    S.row('PH_control_undug_no_offset', bool(ground) and all(abs(r['sink']) < 1e-3 and r['depth'] == 0 for r in ground)
          and bool(still0) and abs(still0['sink']) < 1e-3 and bool(dry),
          {'ground_sinks': [r['sink'] for r in ground], 'still0': still0 and still0['sink'], 'swim': sw,
           'cleared': {k: cleared.get(k) for k in ('success', 'destroyed')} if isinstance(cleared, dict) else cleared},
          unmeasured=not ground or dry is None or flat or not seen or still0 is None)

    pool = [(x0 + 4 + i, z0 + PH_ROWS + 3 + j) for i in range(3) for j in range(3)]
    S.dig(pool, 8)                                                     # 4 m: room for 2 m of water and nothing to stand on
    S.fill(pool, PH_SWIM_M, WATER)
    S.pulse(5)
    lv = S.sc(NSP, 'ProofReadout', '%d,%d' % pool[4])
    import re
    m = re.search(r'Water\s+([\d.]+)\s*m', lv)
    water = float(m.group(1)) if m else None
    swimmer = S.pawn('Colonist', pool[4], 'player')
    k0, t0 = _ph_swim(S, swimmer, pool)
    S.ticks(PH_SWIM_TICKS)
    k1, t1 = _ph_swim(S, swimmer, pool)
    try:
        e0, e1 = float(k0['exhaustion']), float(k1['exhaustion'])
    except (TypeError, KeyError, ValueError):
        e0 = e1 = None
    swam = bool(k0 and k1) and k0.get('deepCell') == 'True' and k1.get('deepCell') == 'True'
    S.row('PH_swims_and_tires_at_2m', swam and e1 > e0 if e0 is not None else False,
          {'water': water, 'readout': lv, 'before': t0, 'after': t1},
          unmeasured=water is None or abs(water - PH_SWIM_M) > 0.2 or e0 is None)


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


# RIMMANDRAKE_REBUILD_FLOWWORKS_TRENCH_SCENE_READ_LID_PROOF (visit 1, 2026-11-15): the draft read ProofCover, the pit-LID
# probe (covered=True is a lid over a pit), so TR_trench_pawn_covered FAILED on a mod whose combat cover trench_cover_proof.py
# read PASS the same day, and TR_no_raider_shelters_in_pit PASSED on an empty 2x2 rect while all 11 raiders stood elsewhere.
# Now cover is combat cover, read the way trench_cover_proof.py reads it (RM_TrenchCover.ProofTrenchCover "target;shooter",
# its parse / trench_bar / near_verdict / hit_falls_verdict / dug_to): square-on from a player gunner 10 squares off, against
# a twin colonist on open ground with its own gunner at the same offset. Then the scene fires a raid placed south of the
# trench and the cage pit beside it, runs every tick of it on RAID_STOP_ON (the moat and pit-trap waiver) and watches where
# raiders stand. A REFUSED read, a read with no shot (hitNoTrench <= 0.05: the all-zero vector) or a raid that never came
# within TR_NEAR squares of the trench or pit reads UNMEASURED, never PASS.
#   trench: x O0..O0+10 at z O1, 2 notches (1 m, trench_bar's wall); target (O0+5, O1), gunner (O0+5, O1+10)
#   pit: x O0+12..+13, z O1..O1+1, 8 notches (4 m: a cage); open-ground twin (O0+18, O1), gunner (O0+18, O1+10)
#   raid: placed at (O0+6, O1-14), ImmediateAttack on the colonists north of the line
TR_LEN, TR_NOTCHES, TR_PIT_NOTCHES = 11, 2, 8
TR_SHOOTER = 'Mercenary_Gunner'                          # trench_cover_proof.SHOOTER_KIND: a ranged player pawn, nobody fights
TR_SETTINGS = (('trenchCoverEnabled', True), ('trenchCoverStrength', 1.0), ('trenchCoverCap', 0.9))
TR_RAID_POINTS, TR_RAID_AT = 400, (O[0] + 6, O[1] - 14)
# 6,000 ticks at most; 1,800 more once a raider is at the line. 60-tick polls: a pawn at vanilla's 4.6 squares/s covers
# under 5 squares a poll, so it cannot cross the 7-square band TR_NEAR makes unread; at 300 ticks (23 squares a poll) visit
# 2's raid ran past the trench unseen ("never came within 3 squares", its raiders 12-90 squares north of it at the end).
TR_POLL, TR_POLLS, TR_NEAR, TR_AFTER = 60, 100, 3, 30
# RIMMANDRAKE_STAGE_FLOWWORKS_PIT_TRAP_RAID_NONE_FELL: the raid worker chose the faction, so each run met a different raid
# (live game b 2026-11-21: PirateYttakin and TribeSavageImpid walked in, PirateWaster was refused, Empire and
# OutlanderRoughPig sent 0 pawns to the controls). Every scene raid now names its faction: the world's hostile humanlike
# factions in a fixed order (Pirate kinds first, as _isl_hostile_faction picks; this calm site's world holds no base
# 'Pirate'), the first that sends pawns, walking in at the scene's own spawn centre (EdgeWalkIn keeps a valid spawnCenter;
# its pawns land within 8 squares). The faction used goes on S.r['raidFaction'] and so into the scene record.
RAID_ARRIVAL = 'EdgeWalkIn'


def _raid_factions(S):
    """The world's hostile humanlike faction defs, Pirate kinds first, each group sorted (spawn_pawn's refusal of '?')."""
    probe = S.B.call('jawa/spawn_pawn', _answer=True, kindDef='Colonist', x=0, z=0, faction='?', count=1) or {}
    avail = (probe.get('details') or {}).get('available') or []
    hostile = sorted({f.get('def') for f in avail if f.get('hostile') and f.get('def')
                      and f.get('def') not in ('Entities', 'Mechanoid', 'Insect')})
    return [f for f in hostile if str(f).startswith('Pirate')] + [f for f in hostile if not str(f).startswith('Pirate')]


def _fire_raid(S, points, at):
    """One scene raid: a named hostile faction, ImmediateAttack, walking in around `at`. Nobody sent is a staging fault."""
    tried = []
    for fac in _raid_factions(S):
        kw = dict(points=points, dryRun=False, faction=fac, strategy='ImmediateAttack', arrivalMode=RAID_ARRIVAL,
                  spawnCenter='%d,%d' % tuple(at))
        r = S.B.call('jawa/fire_raid', _answer=True, **kw) or {}
        S.r['calls'].append({'tool': 'jawa/fire_raid', 'args': kw, 'result': r})
        n = r.get('pawnsArrivedTotal')
        tried.append((fac, r.get('success'), n))
        if r.get('success') and r.get('executed') is not False and (n is None or n > 0):
            S.r['raidFaction'] = {'faction': fac, 'arrived': n, 'tried': tried}
            return r
    require(False, 'no hostile faction sent a raid: %s' % tried)


def _tc():
    """trench_cover_proof.py's pure readers: one cover bar for both drivers."""
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    import trench_cover_proof
    return trench_cover_proof


def _tr_dig(S, TC, cells, n):
    """Dig and read the depth back (success alone is no dig: trench_cover_proof.dug_to)."""
    bad = [c for c in cells if not TC.dug_to(S.call('jawa/flowworks_excavation_drive', x=c[0], z=c[1], deepenLevels=n,
                                                    setBodyWaterM=-1) or {}, n)]
    require(not bad, 'excavation_drive did not reach %d notches at %s' % (n, bad[:4]))


def _tr_read(S, TC, tid, sid):
    """One ProofTrenchCover read -> (kv | None, reply). None: no TRENCH reply (REFUSED), no trench field, or no shot to cover
    (hitNoTrench missing or <= 0.05, the all-zero vector): a read no row may judge."""
    txt = S.sc(TC.PROOF_TYPE, 'ProofTrenchCover', '%s;%s' % (tid, sid))
    d = TC.parse(txt) if txt.startswith('TRENCH') else {}
    h0 = TC.num(d, 'hitNoTrench')
    return (d if h0 is not None and h0 > 0.05 and TC.num(d, 'trench') is not None else None), txt


def _tr_watch(S, trench, pit):
    """The raid in TR_POLL chunks (the caller narrowed the governor): where every live hostile stands each poll.
    -> {reached, inPit {id: cell}, inTrench, raiders, polls, last}; reached: one came within TR_NEAR of the trench or pit."""
    near = list(trench) + list(pit)
    seen = {'reached': False, 'inPit': {}, 'inTrench': set(), 'raiders': 0, 'polls': 0, 'last': []}
    at_line = None
    for _ in range(TR_POLLS):
        S.ticks(TR_POLL)
        seen['polls'] += 1
        live = [p for p in S.call('jawa/list_pawns', faction='hostile').get('pawns') or []
                if not p.get('dead') and p.get('x') is not None]
        seen['raiders'] = max(seen['raiders'], len(live))
        seen['last'] = [(p.get('id'), p.get('x'), p.get('z')) for p in live][:8]
        for p in live:
            at = (p['x'], p['z'])
            if min(_cheb(at, c) for c in near) <= TR_NEAR:
                seen['reached'] = True
            if at in pit:
                seen['inPit'][p.get('id')] = at
            if at in trench:
                seen['inTrench'].add(p.get('id'))
        if seen['reached']:
            at_line = seen['polls'] if at_line is None else at_line
            if seen['polls'] - at_line >= TR_AFTER:
                break
    if seen['inPit']:
        seen['reached'] = True
    return seen


def _trench_cover(S, raid=True):
    """sc_trench_cover. raid False (sc_trench_cover_pawns, the cheaper test: owner, 2026-11-23, no raid in a test unless the mod's
    own function is about raiders) stops after the two placed shooters' cover reads; only the shelter row asks for raiders."""
    TC = _tc()
    for k, v in TR_SETTINGS:
        S.setting(k, v)
    trench = _line(O[0], O[1], TR_LEN)
    pit = [(O[0] + 12 + i, O[1] + j) for i in range(2) for j in range(2)]
    _tr_dig(S, TC, trench, TR_NOTCHES)
    _tr_dig(S, TC, pit, TR_PIT_NOTCHES)
    S.ticks(TC.SETTLE)
    tgt, twin = (O[0] + 5, O[1]), (O[0] + 18, O[1])
    col, gun = S.pawn('Colonist', tgt, 'player'), S.pawn(TR_SHOOTER, (tgt[0], tgt[1] + 10), 'player')
    ctl, cgun = S.pawn('Colonist', twin, 'player'), S.pawn(TR_SHOOTER, (twin[0], twin[1] + 10), 'player')
    d, txt = _tr_read(S, TC, col, gun)
    bar = TC.trench_bar((d or {}).get('size'))
    bar_from = 'size=%s' % (d or {}).get('size') if bar is not None else 'size unread: adult bar 0.441'
    bar = 0.441 if bar is None else bar
    S.row('TR_trench_pawn_covered', d is not None and TC.near_verdict(d, 'trench', bar, 0.02) == 'PASS',
          {'bar': round(bar, 3), 'barFrom': bar_from, 'reply': txt}, unmeasured=d is None)
    S.row('TR_trench_hit_falls', d is not None and TC.hit_falls_verdict(d, bar) == 'PASS',
          {'bar': round(bar, 3), 'hit': (d or {}).get('hit'), 'hitNoTrench': (d or {}).get('hitNoTrench'), 'reply': txt},
          unmeasured=d is None)
    S.shot('trench_cover', (O[0], O[1] - 3), 20, 14)
    c, ctxt = _tr_read(S, TC, ctl, cgun)
    S.row('TR_control_open_ground_no_cover', c is not None and TC.near_verdict(c, 'trench', 0.0, 1e-3) == 'PASS',
          {'reply': ctxt}, unmeasured=c is None)
    if not raid:
        return
    _fire_raid(S, TR_RAID_POINTS, TR_RAID_AT)
    prior, S.B.stop_on = S.B.stop_on, RAID_STOP_ON  # the raid this scene fired is waived for every tick of it
    try:
        seen = _tr_watch(S, trench, pit)
    finally:
        S.B.stop_on = prior
    S.row('TR_no_raider_shelters_in_pit', not seen['inPit'],
          {'inPit': seen['inPit'], 'inTrench': sorted(seen['inTrench']), 'raidersSeen': seen['raiders'], 'polls': seen['polls'],
           'last': seen['last']} if seen['reached'] else
          'the raid never came within %d squares of the trench or pit (raiders seen %d, last %s)' % (
              TR_NEAR, seen['raiders'], seen['last']), unmeasured=not seen['reached'])


# RIMMANDRAKE_REBUILD_FLOWWORKS_ICE_SCENE_BASIN_NEVER_FROZE (visit 1, 2026-11-15): the draft passed '60,60,5,5;freeze' to
# ProofStageBasin, a dig-and-fill stager whose contract is x;z;w;h;levels;waterM;FluidDef, which refused it, so the pond never
# froze; its "cut" was flowworks_job_probe, which designates and orders nothing, so no cut ever happened; and
# ICE_melts_back_into_pond read the fill's own 20,000 dL and PASSED. Now the pond freezes the way vanilla freezes water
# (FreezeManager lays ThinIce on the temp grid; set_terrain_batch routes a temporary def to SetTempTerrain), read back square by
# square; the cut is designated and ordered (gravel_live.cut_once's idiom) and the cut square must still read ThinIce at the
# last poll before it lands; the melt is judged on the melt ledger (RM_IceMelter.ProofMeltLedger) once the site is above 0 C.
# The control is an unfrozen twin pond, cut first.
# RIMMANDRAKE_STAGE_FLOWWORKS_ICE_CUT_SHOVEL_KEEP_FROZEN (visit 2, 2026-11-20): no cut ever landed. The colonist had no shovel
# (SHOVELS_BUILD_NO_DIGGING_BARE_HANDED: no job, designation kept); the probe re-ran the designator on the square the scene had
# just designated and read its 'Already being dug.' as a refusal; the cut costs WorkToCut(3) = 9,600 work x digLabourMultiplier
# 4.0 (shipped) = 38,400 work, about 22,600 ticks at mining speed 1 (1.7 work a tick), against a 6,000-tick wait; and the 13.9 C
# calm site melts painted ThinIce within that wait (iceAtLastPoll 0). Now: a shovel in the pack, Mining 10, a parka (the cold
# below must not frostbite the colonist: the governor raises on a hurt with no pawn source), labour 0.25 (the rows judge the
# yield, not the cut's time), the designator read BEFORE the scene designates, and the frozen pond is cut under ColdSnap +
# DeepFreeze (sheet_overflow_proof's cold) once the cut square reads below 0 C; the conditions end before the melt is judged.
# Both ponds sit on staged Soil (the ground read before is in the rows): a slumping original ground (sand, mud) makes the
# work giver delete a deepening order on a dug square (RM_DigSpoil.DigRefusal, PIT_DIG_FIX_SAND_SLIDES_BACK_IN).
ICE_TEMP, CRUSHED, MELT_DL = 'ThinIce', 'RM_CrushedIce', 10000   # one notch melts to 1,000 L (ICE_YIELD_DECIDE_ONE_CUT_FOUR_NOTCHES)
MELTER = 'RimMandrake.FlowWorks.RM_IceMelter'
ICE_COLD = ('ColdSnap', 'DeepFreeze')   # sheet_overflow_proof COLD: measured 7.5 -> -2.4 C in 4,500 ticks (r5K, 2026-11-01)
ICE_COLD_TICKS = 20000   # 13.9 C at that ~1.4 C per 500 ticks is ~5,000 ticks to 0 C; four times that before UNMEASURED
ICE_CUT_TICKS = 6000     # 9,600 x 0.25 = 2,400 work; Mining 10 (speed ~1.2) x 1.7 work a tick is ~1,200 ticks; five times that
ICE_WARM_TICKS = 20000   # after the cold ends, the same budget back above 0 C
MELT_TICKS_PER_UNIT = 10000   # RM_CrushedIce.xml: a stack melts one crushed ice per 4 hours (10,000 ticks) above 0 C
ICE_LABOUR = 0.25        # RM_DigDepthMath.MinLabourMultiplier, as droid_dig_live stages it
ICE_GROUND = 'Soil'


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


def _soft(S, tool, **kw):
    """One recorded bridge call whose refusal is a reading (the caller decides), never a staging raise."""
    r = S.B.call(tool, **kw)
    S.r['calls'].append({'tool': tool, 'args': kw, 'result': r})
    return r if isinstance(r, dict) else {'success': False, 'raw': r}


def _why(det, why, **more):
    """The row's reason and its newest readings first: S.row keeps 400 characters of the detail."""
    out = dict(why=why, **more)
    out.update((k, v) for k, v in det.items() if k not in out)
    return out


def _below_zero(t):
    """sheet_overflow_proof.below_zero: strictly below 0 C on the kernel's 1/16 C grid (D10); None is not below anything."""
    return isinstance(t, (int, float)) and int(t * 16) < 0


def _ice_cut(S, pid, c, frozen):
    """Designate and order one cut at c; tick until its depth changes. -> (verdict_kind, detail): 'landed' | 'mod' (the mod's
    designator or work giver refused the square) | 'site' (a pawn-side gate, or the ice gone before the cut landed) | 'harness'.
    The designator is read on the square BEFORE the scene designates it: read after, it answers 'Already being dug.' about the
    scene's own order (visit 2)."""
    d0 = S.cells([c])[0].get('d')
    pre = S.call('jawa/flowworks_job_probe', pawnId=pid, kind='dig', x=c[0], z=c[1])
    S.call('jawa/designate_batch', action='add', designation='RM_DigCanal', rect='%d,%d,1,1' % c)
    pr = S.call('jawa/flowworks_job_probe', pawnId=pid, kind='dig', x=c[0], z=c[1])
    wg, pw, dz = pr.get('workGiver') or {}, pr.get('pawn') or {}, pre.get('designator') or {}
    det = {'d0': d0, 'terrain': pr.get('terrain'), 'designator': dz, 'workGiver': wg}
    if not pre.get('success') or not pr.get('success') or d0 is None:
        return 'harness', _why(det, 'job probe or depth read unavailable: %s' % str(pr.get('message') or pr)[:160])
    if pw.get('workTypeDisabled') or pw.get('missingCapacity') or pw.get('canReach') is False:
        return 'site', _why(det, 'the colonist cannot do the cut: %s' % pw)
    if not dz.get('accepted'):
        return 'mod', _why(det, 'the dig designator refused the square: %s' % dz)
    if wg.get('hasJobOnCell') is not True or wg.get('jobDef') != 'RM_DigCanalJob':
        return 'mod', _why(det, 'the work giver hands no RM_DigCanalJob here (shouldSkip=%s failReason=%s deleted=%s)' % (
            wg.get('shouldSkip'), wg.get('failReason'), wg.get('designationDeletedByWorkGiver')))
    od = S.call('jawa/ordered_job', pawnId=pid, jobDef='RM_DigCanalJob', targetAX=c[0], targetAZ=c[1], waitTicks=0)
    if od.get('success') is False or od.get('accepted') is False:
        return 'harness', _why(det, 'ordered_job refused: %s' % str(od)[:160])
    iced, t, temps = None, 0, []
    while t < ICE_CUT_TICKS:
        if frozen:
            iced = _ice_squares(S, c[0], c[1], 1, 1)
            temps.append(S.call('jawa/cell_temperature', cell='%d,%d' % c).get('temperature'))
        S.ticks(250)
        t += 250
        d = S.cells([c])[0].get('d')
        if d not in (None, d0):
            det.update(d1=d, cutAt=t, iceAtLastPoll=iced, cutTempsC=temps[-3:])
            if frozen and not iced:
                return 'site', _why(det, 'the cut square no longer read ThinIce before the cut landed (%s)' % iced)
            return 'landed', det
    return 'harness', _why(det, 'the ordered cut did not land in %d ticks' % ICE_CUT_TICKS, iceAtLastPoll=iced,
                           cutTempsC=temps[-3:])


ICE_CUTTER_TRIES = 5          # spawns tried for a cutter whose Mining is not disabled
ICE_ROWS = ('ICE_control_unfrozen_cut_no_crushed_ice', 'ICE_cut_leaves_crushed_ice', 'ICE_melts_back_into_pond')


def _ice(S):
    import shovel_stage
    pond, twin = (O[0], O[1]), (O[0] + 12, O[1])                  # two 5x5 ponds, 7 squares of dry ground between
    ground = {}
    for p in (pond, twin):
        ground[p] = S.call('jawa/get_terrain_batch', rects='%d,%d,5,5' % p).get('ops')
        S.call('jawa/set_terrain_batch', ops='%s:%d,%d,5,5' % ((ICE_GROUND,) + p))
        sq = [(p[0] + i, p[1] + j) for i in range(5) for j in range(5)]
        S.dig(sq, 2); S.fill(sq, 1.0, WATER)
    S.setting('iceDigEnabled', True)
    S.setting('digRockWorkMultiplier', 1.0)                        # the rows judge the yield, not the cut's time
    S.setting('digLabourMultiplier', ICE_LABOUR)
    cut, twin_cut = (pond[0], pond[1] + 2), (twin[0], twin[1] + 2)  # west-edge middles, reachable from the bank
    # a backstory can disable Mining outright (live ArchSmall 2026-11-23, visit 9: set_pawn_skill refused, "TOTALLY DISABLED";
    # the suspension bridge proof's repair b1cc65afe2): such a colonist leaves the map and another is spawned
    for k in range(ICE_CUTTER_TRIES):
        col = S.pawn('Colonist', (pond[0] - 2, pond[1] + 2), 'player')
        sk = _soft(S, 'jawa/set_pawn_skill', pawn=col, skill='Mining', level=10)
        if sk.get('success') is not False:
            break
        if k + 1 < ICE_CUTTER_TRIES:
            S.call('jawa/pawn_force_incapacitate', pawn=col, action='vanish')
    staged = [shovel_stage.give_shovel(lambda tool, **kw: _soft(S, tool, **kw), col)]
    staged.append((sk.get('success') is not False, 'Mining 10: %s' % str(sk)[:120]))
    pk = _soft(S, 'jawa/pawn_gear', pawn=col, action='wear', **{'def': 'Apparel_Parka'})
    staged.append((pk.get('success') is not False, 'parka: %s' % str(pk)[:120]))
    if not all(ok for ok, _ in staged):
        for rid in ICE_ROWS:
            S.row(rid, False, 'the cutter was not staged: %s' % [w for ok, w in staged if not ok], unmeasured=True)
        return

    # control first, on the unfrozen twin: a cut through open water leaves no crushed ice
    n0 = _crushed_near(S, twin_cut)
    kind, det = _ice_cut(S, col, twin_cut, frozen=False)
    n1 = _crushed_near(S, twin_cut)
    S.row(ICE_ROWS[0], kind == 'landed' and n1 == n0, _why(det, det.get('why', kind), crushed=(n0, n1),
                                                          groundBefore=str(ground[twin])[:60]),
          unmeasured=kind not in ('landed', 'mod') or (kind == 'landed' and None in (n0, n1)))   # a refusal is the mod's
    S.call('jawa/destroy_batch', rects='%d,%d,7,7' % (twin_cut[0] - 3, twin_cut[1] - 3), categories='Item')  # no pile of
    # the twin's may thaw into the melt ledger the frozen pond's row reads

    # the cold, then the frozen pond (asserted ice), then the cut while the conditions still hold
    gcs = [_soft(S, 'jawa/game_condition', action='start', condition=n, durationTicks=ICE_COLD_TICKS + ICE_CUT_TICKS)
           for n in ICE_COLD]
    try:
        temps, t = [], 0
        while t < ICE_COLD_TICKS:
            temps.append(S.call('jawa/cell_temperature', cell='%d,%d' % cut).get('temperature'))
            if _below_zero(temps[-1]):
                break
            S.ticks(500)
            t += 500
        cold = {'conditions': [g.get('success') for g in gcs], 'cooledTicks': t, 'tempsC': temps[-3:]}
        if not _below_zero(temps[-1]):
            S.row(ICE_ROWS[1], False, _why(cold, 'the cut square never read below 0 C'), unmeasured=True)
            S.row(ICE_ROWS[2], False, 'no frozen pond, so no cut and no melt', unmeasured=True)
            return
        S.call('jawa/set_terrain_batch', ops='%s:%d,%d,5,5' % ((ICE_TEMP,) + pond))
        iced = _ice_squares(S, pond[0], pond[1], 5, 5)
        if iced != 25:
            S.row(ICE_ROWS[1], False, _why(cold, 'the pond did not read frozen: %s/25 ThinIce squares' % iced),
                  unmeasured=True)
            S.row(ICE_ROWS[2], False, 'no frozen pond, so no cut and no melt', unmeasured=True)
            return
        c0 = _crushed_near(S, cut)
        kind, det = _ice_cut(S, col, cut, frozen=True)
        c1 = _crushed_near(S, cut)
    finally:
        for n in ICE_COLD:
            _soft(S, 'jawa/game_condition', action='end', condition=n)
    made = (c1 - c0) if None not in (c0, c1) else None
    det = _why(det, det.get('why', kind), crushed=(c0, c1), cold=cold, groundBefore=str(ground[pond])[:60])
    if kind in ('landed', 'mod'):
        S.row(ICE_ROWS[1], kind == 'landed' and bool(made and made >= 1), det, unmeasured=made is None)
    else:
        S.row(ICE_ROWS[1], False, det, unmeasured=True)
    if not made or made < 1:
        S.row(ICE_ROWS[2], False, 'no crushed ice from the cut, so nothing to melt (%s)' % det.get('why', made), unmeasured=True)
        return

    # warm: back above 0 C, then every pile melts into the water its cut removed, and the world takes exactly that much
    lg0, t, warm = _melt_ledger(S), 0, []
    while t < ICE_WARM_TICKS:
        warm.append(S.call('jawa/cell_temperature', cell='%d,%d' % cut).get('temperature'))
        if isinstance(warm[-1], (int, float)) and warm[-1] > 0:
            break
        S.ticks(500)
        t += 500
    t_warm, left, budget = t, c1, made * MELT_TICKS_PER_UNIT + 2000   # one poll step past the last unit's melt
    while t - t_warm < budget and left:
        S.ticks(2000)
        t += 2000
        left = _crushed_near(S, cut)
        warm.append(S.call('jawa/cell_temperature', cell='%d,%d' % cut).get('temperature'))
    lg1 = _melt_ledger(S)
    mdet = {'crushedLeft': left, 'ticks': t, 'warmAfterTicks': t_warm, 'budget': budget, 'ledger': (lg0, lg1),
            'want': made * MELT_DL, 'tempsC': warm[-4:]}
    known = [w for w in warm if isinstance(w, (int, float))]
    if None in (lg0, lg1, left):
        S.row(ICE_ROWS[2], False, _why(mdet, 'a melt-ledger or crushed-ice read came back empty'), unmeasured=True)
    elif left and (not known or max(known) <= 0):
        S.row(ICE_ROWS[2], False, _why(mdet, 'the site never got above 0 C: no thaw to judge'), unmeasured=True)
    else:
        S.row(ICE_ROWS[2], not left and lg1 - lg0 == made * MELT_DL, mdet)


# RIMMANDRAKE_REBUILD_FLOWWORKS_MOAT_SCENE_PASSED_ON_REFUSED (visit 1, 2026-11-15): the draft dug a 20-square ditch anyone
# walks round, fired an unplaced map-edge raid (refused once: no Pirate faction in the world), spawned a bare drawbridge gate
# and a sluice beyond the ditch's end, "opened" it with ProofDrainGate (a read of the edge-sink gate: no verb), staged 400
# tank units (one pump level is 10,000) with no pump and no power, and read the tank with a one-part arg ProofTank refuses,
# so MOAT_chemfuel_pumped PASSED on "REFUSED: arg must be ...". Now the moat is a closed ring round the colony plot, the
# leaf is a real drawbridge (ProofMakeDrawbridge, read back, raised by ProofDevSet), the sluice is a player-built flow door
# lifted with RM_FlowDoorRules.ProofSetGate onto a drain pit deep enough to take the whole moat, six melee raiders stand on
# the south bank under an assault lord (the governor narrowed for them), swimming is RM_Swim.ProofSwim's deepCell and
# exhaustion, the capture is the RM_CaptureDown order from the lip, and the chemfuel is a powered pump pouring a Dump
# tank's two levels into the drained moat, read on the moat's own cells. Each row needs its event: no raider read, no
# swimmer, nothing drained, no chemfuel cell reads UNMEASURED, never PASS.
#   ring: 16 x 16 at O, four squares wide, dug 4 m, 3 m of water (a metre of wall above it); plot 8 x 8 inside, x/z +4..+11
#   leaf: x O0+8 from z O1-1 (raider bank) to O1+4 (colony bank; winch at O1+5, in the plot); sluice (O0+16, O1+7)
#   drain pit x +17..+23, z +4..+10, 20 m; in the plot: pump (O0+4, O1+7) beside the moat, tank (2x2) at (O0+5, O1+7),
#   battery (O0+6, O1+9); raiders z O1-6
# RIMMANDRAKE_TRACE_FLOWWORKS_MOAT_SWIMMERS_ONLY_IN_THE_CONTROL (Test Pilot sitting 2026-11-21, game b): the ring was dug 8
# notches and filled 2 m, so 2 m of wall stood above the water. The mod judges a dug swim square at its water surface
# (RM_MapComponent_Excavation.ClimbDepthAt), a half-full pit keeps its wall, and no raider could reach the colony: all six
# took AttackMelee, then Wait, on their spawn squares (RM_WallReach.ProofReachPair canReach: 2.0 m False, 2.5 m False,
# 3.0 m True, 4.0 m True; at 4.0 m all six swam and tired). Staging reads every square's depth and water back. The moat is
# over 3 m deep: a drained 2 m moat held the raiders (IsHeld) but ProofCaptureDown read NotHeld, because a pit room holds a
# person only from pitRoomMinDepthMetres (3 m) down (RM_PitRooms.HoldsBySize). RM_Swim adds exhaustion every 250 ticks, so a
# read at the first swim is 0.000: the swimmers are read on through the drain. The control ran its whole 3,000 ticks; once the
# colonist was down the raiders smashed the winch and the leaf's anchors from the deck, the leaf fell and two swam (2026-11-19,
# tick 1445). The control now ends at the crossing and counts a swimmer only while the leaf reads lowered.
# RIMMANDRAKE_DECIDE_MOAT_RAID_BAR_TEXT_SAYS_D4_SCENE_NEEDS_SIX (2026-11-23; map: design/concepts/FlowWorks/version/moat_geometry/):
# the ring was 2 wide, brim-full 3 m, and drained by bare flow pulses: 2,000 ticks of draining in no game time, the raiders
# frozen in the water. Played in game time a brim-full moat holds nobody until its level fell 1 m (4 pulses, 1,000 ticks) and a
# raider swims 2 squares in about 130, so two were held in 0-2 raids of 100. Now the water stands a metre below the rim, the most
# a person climbs: raiders swim in and out, and the first fall of the level holds whoever is in the water. Four squares is the
# longest timber leaf and the widest ring whose every square is within capture reach of the inner rim. The moat drains in game
# time while the raid goes on. At 3 m exactly the raiders can enter; one decilitre less and they cannot (staging reads it).
MOAT_PLOT, MOAT_W, MOAT_DEEP, MOAT_WATER_M = 8, 4, 8, 3.0
MOAT_N = MOAT_PLOT + 2 * MOAT_W
MOAT_PIT_DEEP = 40                                   # 16 m below the moat floor x 49 squares holds the ring's 192 x 3 m
MOAT_KIND, MOAT_RAIDERS = 'Mercenary_Slasher', 6     # melee: they must cross to reach the colonist
MOAT_POLL, MOAT_POLLS = 60, 50                       # 3,000 ticks a watch
MOAT_DRAIN_TICKS, MOAT_CAPTURE_TICKS = 6000, 900     # a drain that never ends holds the bridge for ever; the kernel twin says 2,000
MOAT_TANK_UNITS = 20000                              # two pump levels (RM_PumpMath.TankUnitsPerLevel = 10,000)
SWIMP = 'RimMandrake.FlowWorks.Swimming.RM_Swim'
SWIMSET = 'RimMandrake.FlowWorks.Swimming.RM_SwimSettings'
DOORS = 'RimMandrake.FlowWorks.RM_FlowDoorRules'
WALLREACH = 'RimMandrake.FlowWorks.RM_WallReach'


def _moat_geom():
    x0, z0 = O
    W, n = MOAT_W, MOAT_N
    ring = [(x0 + i, z0 + j) for i in range(n) for j in range(n) if i < W or i >= n - W or j < W or j >= n - W]
    return {'ring': ring, 'leaf': ((x0 + W + 4, z0 - 1), (x0 + W + 4, z0 + W)), 'deck': (x0 + W + 4, z0),
            'winch': (x0 + W + 4, z0 + W + 1), 'sluice': (x0 + n, z0 + W + 3),
            'pit': [(x0 + n + 1 + i, z0 + W + j) for i in range(7) for j in range(7)],
            'pump': (x0 + W, z0 + W + 3), 'tank': (x0 + W + 1, z0 + W + 3), 'battery': (x0 + W + 2, z0 + W + 5),
            'col': (x0 + W + 5, z0 + W + 4), 'raiders_at': [(x0 + W + 1 + k, z0 - 6) for k in range(MOAT_RAIDERS)]}


def _moat_send(S, G, spots):
    """Raiders of the moat raid at these spots, under an assault lord."""
    new = []
    for at in spots:
        r = S.call('jawa/spawn_pawn', kindDef=MOAT_KIND, x=at[0], z=at[1], faction=G['faction'], count=1)
        pid = ((r.get('pawns') or [{}])[0]).get('id')
        require(pid, 'raider not spawned at %s: %s' % (at, r))
        new.append(pid)
    S.call('jawa/lord_assault_spawn', pawns=','.join(new), sappers=False)
    G['raiders'] += new


def _moat_stage(S, raised=True, raiders=True):
    """raiders False (sc_moat_walkers) stages the same map and spawns no hostile. Ring, drain pit, shut sluice, drawbridge (raised or lowered, read back), the west-bank pump plant, one colonist in the
    plot and six raiders on the south bank under an assault lord; over the LOWERED leaf they come one at a time (the first now,
    the rest in G['later'], sent by _moat_watch as each one before has crossed): a raider on the deck costs the one behind him
    175 in vanilla's path (PathFinderJob.Cost_Blocked), a swim square beside him 60, so six at once swim round each other, which
    the control does not ask about (version/moat_geometry/control_crowd.py). -> the staged state."""
    G = _moat_geom()
    for k in ('deepSwimEnabled',):
        S.setting(k, True, typ=SWIMSET)
    for k in ('captureDownEnabled', 'superdeepRoomsEnabled', 'liquidPumpEnabled', 'tossFlameOrderEnabled'):
        S.setting(k, True)
    S.dig(G['ring'] + [G['sluice']], MOAT_DEEP)
    S.dig(G['pit'], MOAT_PIT_DEEP)
    b = S.call('jawa/build_batch', ops='RM_Sluice:%d,%d' % G['sluice'], stuff='WoodLog', faction='player', wipeExisting=False)
    require(int(b.get('survived') or 0) >= 1, 'the sluice was not built: %s' % b)
    shut = S.sc(DOORS, 'ProofSetGate', 'current|%d,%d|false' % G['sluice'])
    require('lifted=False' in shut, 'the sluice does not read lowered: %s' % shut)
    S.fill(G['ring'], MOAT_WATER_M, WATER)
    # site: with more than a metre of wall above its water a moat is a pit no raider enters (the 2026-11-21 sitting); read
    # every square's depth and water back
    q = S.cells(G['ring'])
    off = [(c, r.get('d'), r.get('dl')) for c, r in zip(G['ring'], q)
           if r.get('d') != MOAT_DEEP or (r.get('dl') or 0) < round(MOAT_WATER_M * 20000)]
    require(not off, 'the moat is not dug %s notches with %s m of water (more than 1 m of wall above the water: raiders cannot '
            'enter it): %s' % (MOAT_DEEP, MOAT_WATER_M, off[:4]))
    pit = [(c, r.get('d')) for c, r in zip(G['pit'], S.cells(G['pit'])) if r.get('d') != MOAT_PIT_DEEP]
    require(not pit, 'the drain pit is not dug %s notches: %s' % (MOAT_PIT_DEEP, pit[:4]))
    txt = S.sc(DPROOF, 'ProofMakeDrawbridge', '%d,%d;%d,%d;timber;B;winch' % (G['leaf'][0] + G['leaf'][1]))
    d = kv(txt)
    require(d.get('ok') == 'True' and d.get('leaves') == '1', 'the drawbridge was not built as one leaf: %s' % txt)
    require(d.get('winchAt') == '%d,%d' % G['winch'], 'the winch is not in the plot at %s: %s' % (G['winch'], txt))
    leaf = _moat_leaf(S, G)
    require(leaf.get('progress') == '0' and leaf.get('winch') == 'True', 'the drawbridge does not read lowered: %s' % leaf)
    if raised:
        txt = S.sc(DPROOF, 'ProofDevSet', '%d,%d;raise;instant' % G['deck'])
        require(kv(txt).get('target') == 'raised' and kv(txt).get('progress', '0') != '0', 'the leaf did not go up: %s' % txt)
    # site: the plot keeps its grass (live ArchSmall 2026-11-23, visit 9: grass on the tank and battery squares refused the
    # build_batch, wipeExisting=False, and the scene read UNMEASURED)
    S.call('jawa/destroy_batch', rects='%d,%d,%d,%d' % (O[0] + MOAT_W, O[1] + MOAT_W, MOAT_PLOT, MOAT_PLOT),
           categories='Plant,Item,Filth')
    ops = ['RM_LiquidPump:%d,%d' % G['pump'], 'RM_LiquidTank:%d,%d' % G['tank'], 'Battery:%d,%d' % G['battery']]
    b = S.call('jawa/build_batch', ops=';'.join(ops), faction='player', wipeExisting=False)
    require(int(b.get('survived') or 0) >= len(ops), 'build_batch built less than asked: %s' % b)
    tank = S.sc(NSP, 'ProofTank', '%d,%d;Dump;RM_Liquid_Chemfuel;%d' % (G['tank'] + (MOAT_TANK_UNITS,)))
    require(tank.startswith('TANK') and kv(tank).get('units') == str(MOAT_TANK_UNITS), 'the tank was not staged: %s' % tank)
    S.ticks(2)
    bid = ((S.call('jawa/list_things', defName='Battery', rect='%d,%d,1,2' % G['battery'], limit=2).get('things') or [{}])[0]).get('id')
    require(bid is not None, 'no battery at %s' % (G['battery'],))
    S.call('jawa/battery_set', thing=bid, mode='setPct', value=1.0)
    G['colonist'] = S.pawn('Colonist', G['col'], 'player')
    G['later'], G['raiders'] = [], []
    if not raiders:
        return G
    G['faction'] = _isl_hostile_faction(S)
    first = len(G['raiders_at']) if raised else 1
    _moat_send(S, G, G['raiders_at'][:first])
    G['later'] = list(G['raiders_at'][first:])
    return G


def _moat_leaf(S, G):
    txt = S.sc(DPROOF, 'ProofLeaf', '%d,%d' % G['deck'])
    d = kv(txt)
    require('winch' in d and 'progress' in d, 'leaf unreadable: %s' % txt)
    return d


def _moat_live(S, G):
    """Our raiders alive on the map: [(id, x, z)]."""
    mine = set(G['raiders'])
    return [(p['id'], p['x'], p['z']) for p in S.call('jawa/list_pawns', faction='hostile').get('pawns') or []
            if p.get('id') in mine and not p.get('dead') and p.get('x') is not None]


def _moat_read(S, G, seen):
    """One read of every live raider of ours into `seen`. -> how many are in a swim square of the ring now."""
    ring, live, now = set(G['ring']), _moat_live(S, G), 0
    seen['last'] = live
    for pid, x, z in live:
        if O[0] <= x < O[0] + MOAT_N and O[1] <= z < O[1] + MOAT_N:
            seen['reached'].add(pid)
            if (x, z) not in ring:
                seen['crossed'].add(pid)
        txt = S.sc(SWIMP, 'ProofSwim', '%d,%d' % (x, z))
        if not txt.startswith('SWIM ' + pid + ' '):
            seen['refused'] += 1
            continue
        seen['read'].add(pid)
        d = kv(txt)
        wet = d.get('deepCell') == 'True' and (x, z) in ring
        now += wet
        if wet or pid in seen['swam']:       # exhaustion outlasts the swim: a swimmer is read again once ashore
            try:
                ex = float(d.get('exhaustion'))
            except (TypeError, ValueError):
                ex = None                    # a swim square with no exhaustion field: swum, tiredness unread
            had = seen['swam'].get(pid)
            seen['swam'][pid] = ex if had is None else (had if ex is None else max(had, ex))
    return now


def _moat_watch(S, G, polls=MOAT_POLLS, until_swimmers=2, until_crossed=0):
    """MOAT_POLL chunks (the caller narrowed the governor). Each poll reads RM_Swim.ProofSwim under every live raider of ours: who read
    deepCell=True (a swim square) and the most exhaustion each reached; who stood inside the ring's outer box (got there);
    who stood in the plot (crossed). The watch ends once until_swimmers are in the water at once. until_crossed (the
    bridge-down control): the leaf is read each poll, the watch ends once that many have crossed, and it ends unjudged the
    moment the leaf no longer reads lowered ('leafDown' False), since a raider on a deck that fell swims for a reason the
    control does not ask about."""
    seen = {'polls': 0, 'read': set(), 'swam': {}, 'reached': set(), 'crossed': set(), 'last': [], 'refused': 0, 'leafDown': None}
    for _ in range(polls):
        S.ticks(MOAT_POLL)
        seen['polls'] += 1
        if until_crossed:
            leaf = kv(S.sc(DPROOF, 'ProofLeaf', '%d,%d' % G['deck']))
            seen['leafDown'] = leaf.get('progress') == '0' and leaf.get('target') == 'lowered'
            if not seen['leafDown']:
                break
        now = _moat_read(S, G, seen)
        if until_swimmers and now >= until_swimmers:
            break
        if until_crossed:
            S.r.setdefault('moatControlTrace', []).append(_raid_trace_line(S, G, seen['polls']))
            if len(seen['crossed']) >= until_crossed:
                break
            if G.get('later') and set(G['raiders']) <= seen['crossed']:      # the deck is free: the next one comes
                _moat_send(S, G, [G['later'].pop(0)])
    return seen


def _raid_trace_line(S, G, poll):
    """One poll of the bridge-down control: each raider and the colonist as id@x,z:job (a swimmer names who stood where)."""
    mine = set(G['raiders']) | {G['colonist']}
    return 'poll %d ' % poll + ' '.join('%s@%s,%s:%s' % (p['id'], p.get('x'), p.get('z'), p.get('job')) for p in
                                        (S.B.call('jawa/site_state') or {}).get('pawns') or [] if p.get('id') in mine)


def _moat_in_ring(S, G):
    """Our live raiders standing on ring squares: [(id, (x, z), ProofCaptureDown's verdict)]."""
    ring = set(G['ring'])
    return [(pid, (x, z), S.sc(NSP, 'ProofCaptureDown', pid)) for pid, x, z in _moat_live(S, G) if (x, z) in ring]


def _moat_drain(S, G, seen):
    """The sluice is open and the raid goes on, in game ticks (never bare flow pulses: they drain in no game time and the
    raiders stand still). Swim reads go on into `seen`. The moment the moat holds a raider, the raiders it did not catch
    leave the map (the pit-trap idiom) and so does the colonist they came for; ends when every ring square reads dry."""
    d = {'heldAfterTicks': None, 'dryAfterTicks': None, 'dl': None, 'gone': [], 'bait': None, 'trace': []}
    for k in range(1, MOAT_DRAIN_TICKS // MOAT_POLL + 1):
        S.ticks(MOAT_POLL)
        _moat_read(S, G, seen)
        # visit 9 (2026-11-23, run T161018): a raider read held=True stood on the plot 1,200 ticks later, the water under 1 m and
        # the wall over 3 m, and cut a warden; no read said how he got out. Each poll now keeps every raider's square and job.
        d['trace'].append(_capture_trace_line(S, [{'warden': r, 'pawn': r} for r in G['raiders']]))
        if d['heldAfterTicks'] is None:
            inside = _moat_in_ring(S, G)
            if any('held=True' in v for _, _, v in inside):
                d['heldAfterTicks'] = k * MOAT_POLL
                d['gone'] = _raid_driven_off(S, {i[0] for i in inside})
                d['bait'] = _moat_bait_off(S, G)
        if k % 4 == 0:                          # a flow pulse is 250 ticks: the level is read about once a pulse
            d['dl'] = S.dl(G['ring'])
            if None not in d['dl'] and not any(d['dl']):
                d['dryAfterTicks'] = k * MOAT_POLL
                break
    return d


def _moat_bait_off(S, G):
    """The colonist the raid came for leaves the map, so no held raider has him to fight. -> what he was doing, or None."""
    bait = next((q for q in S.call('jawa/site_state').get('pawns') or [] if q.get('id') == G['colonist']), None)
    if bait:
        S.call('jawa/pawn_force_incapacitate', pawn=G['colonist'], action='vanish')
    return bait and (bait.get('job') or 'no job')


def _moat_lip(G, at):
    """An undug square of the plot or the bank beside the raider at `at` (the warden's stand), nearest first."""
    dug = set(G['ring']) | set(G['pit']) | {G['sluice']}
    near = [(at[0] + dx, at[1] + dz) for dx in (-1, 0, 1) for dz in (-1, 0, 1) if (dx, dz) != (0, 0)]
    near = [c for c in near if c not in dug] + [(at[0] + dx, at[1] + dz) for dx in (-2, 2) for dz in (-2, 0, 2)
                                               if (at[0] + dx, at[1] + dz) not in dug]
    return near[0] if near else None


def _capture_trace_line(S, caught):
    """One poll of a capture window, one short string: the tick, then each warden and captive as id@x,z:job>target.
    A stalled capture names its own cause from this (who stopped doing what, when). Read past the receipt (S.B.call):
    a 30-tick trace recorded call by call would be most of the evidence file."""
    r = S.B.call('jawa/site_state') or {}
    ids = {c['warden'] for c in caught} | {c['pawn'] for c in caught}
    out = []
    for p in r.get('pawns') or []:
        if p.get('id') in ids:
            t = p.get('targetA') or {}
            out.append('%s@%s,%s:%s>%s' % (p['id'], p.get('x'), p.get('z'), p.get('job'),
                                         t.get('id') or t.get('thingId') or ('%s,%s' % (t.get('x'), t.get('z')) if t else '-')))
    seen = {s.split('@')[0] for s in out}
    return 't=%s %s%s' % ((r.get('state') or {}).get('tick'), ' '.join(sorted(out)),
                         ''.join(' %s:gone' % i for i in sorted(ids - seen)))


def _hits_on(S, pid):
    """Who hurt pawn pid, from the bridge's damage recorder: ['tick instigator damageDef', ...] (the last 12)."""
    r = S.B.call('jawa/damage_log', thingId=str(pid), limit=12) or {}
    if not r.get('success'):
        return 'damage recorder refused: %s' % str(r)[:80]
    return ['%s %s %s' % (e.get('tick'), e.get('instigatorId') or 'no instigator', e.get('damageDef')) for e in r.get('events') or []]


def _rim_stabs(hits_by_warden, raiders):
    """The hits a held raider landed on each warden: {warden: ['tick instigator damageDef', ...]}. A warden's own punches
    (the recorder lists a pawn's events as instigator too) and a recorder that refused (a string) are not stabs."""
    return {w: [h for h in hits if len(h.split()) >= 2 and h.split()[1] in raiders] if isinstance(hits, list) else []
            for w, hits in hits_by_warden.items()}


def _moat_plot_lip(at):
    """The plot square nearest the raider at `at` (the undug square inside the ring)."""
    plot = [(O[0] + MOAT_W + i, O[1] + MOAT_W + j) for i in range(MOAT_PLOT) for j in range(MOAT_PLOT)]
    return min(plot, key=lambda c: (c[0] - at[0]) ** 2 + (c[1] - at[1]) ** 2)


# ── anti-guessing notes: the moat capture (test pilot sitting 2026-11-23, RIMMANDRAKE_HOLD_FLOWWORKS_PIT_PRISONERS_THREE_CAPTURE_FAULTS)
# CAUSE (measured, fixed 1c053b325bc5): (a) a held raider on a moat square that no rim square the warden can walk to touches
#   (the outer column of this 2-wide ring, seen from the plot) made the warden wait at the nearest rim square until
#   CaptureRepathLimit x CaptureRepathPauseTicks ran out (about 330 ticks), then the job ended with no prisoner and no message:
#   the "prisoner flag backslides" and "held raider read free" readings. (b) any held raider that is not pinned stabbed any
#   colonist on a rim square and walked the moat floor to reach one: the downed wardens. The check for (a) is the C# case
#   PitCapture_takes_from_the_rim_without_touching; for (b) the row MOAT_rim_wardens_not_stabbed and PitRoomReach_*.
# RULED OUT: a third raider's hit ends the warden's capture job. A stab (with stun spores) landed 90 ticks into the hold and
#   the capture still finished at 180 ticks.
# RULED OUT: the first finished capture ends the others (the pit becoming a prison). Two captures 60 ticks apart both finished.
# RULED OUT: a raider on the outer column alone stalls it. An awake raider walks in to attack, is pinned and taken; the stall
#   needs him to stay out of touch past the repath budget (downed, dormant for 330 ticks after the drive-off, or busy).
# RULED OUT: a new-build regression on 6b52871479. The failing runs differ from the passing ones only in where the held
#   raiders stood when the order was given.
# HARNESS traps met: a row's detail is cut short in the evidence file, so the trace lives in S.r['moatCaptureTrace']; raiders
#   sit in job Wait for about 330 ticks after the free ones are driven off, and Wait still auto-attacks the 8 squares around;
#   jawa/damage_log keeps events across a save reload within one game session (same ids, earlier ticks); a .cs file that is
#   not on the csproj Compile list builds clean and never reaches the game (read jawa/harmony_patches, type RimWorld.Pawn_MeleeVerbs).
# NOT this fault, filed apart: MOAT_raiders_swim misses a crossing that falls between two 250-tick exhaustion checks
#   (RIMMANDRAKE_FIX_FLOWWORKS_MOAT_SWIM_ROW_MISSES_SHORT_CROSSING); a swimmer beside the lowered leaf
#   (RIMMANDRAKE_TRACE_FLOWWORKS_MOAT_SWIMMER_PAST_LOWERED_LEAF_AGAIN: every swim is on the column next to the 1-wide deck).
def _moat_raid(S):
    G = _moat_stage(S, raised=True)                 # its raiders spawn after its last tick
    prior, S.B.stop_on = S.B.stop_on, RAID_STOP_ON  # a raid hurts, downs and kills by design: narrowed for every tick of it
    try:
        _moat_rows(S, G)
    finally:
        S.B.stop_on = prior


def _moat_rows(S, G):
    w = _moat_watch(S, G)
    reach = S.sc(WALLREACH, 'ProofReachPair', '%s;%d,%d' % ((G['raiders'][0].replace('Human', ''),) + G['col'])) if not w['swam'] else '-'
    early = [i for i in _moat_in_ring(S, G) if 'held=True' in i[2]]
    require(not early, 'a raider reads held before the sluice opened (the moat holds on its own): %s' % early[:2])
    # open the sluice onto the dry pit while they swim: every ring square must read dry within MOAT_DRAIN_TICKS
    up = S.sc(DOORS, 'ProofSetGate', 'current|%d,%d|true' % G['sluice'])
    require('lifted=True' in up, 'the sluice did not lift: %s' % up)
    drain = _moat_drain(S, G, w)
    S.r['moatDrainTrace'] = drain['trace']
    dry_at, dl = drain['dryAfterTicks'], drain['dl']
    swimmers = sorted(w['swam'])
    tired = [p for p in swimmers if (w['swam'][p] or 0) > 0]
    S.row('MOAT_raiders_swim', bool(tired),
          {'swimmers': swimmers, 'exhaustion': w['swam'], 'polls': w['polls'], 'read': sorted(w['read']), 'last': w['last'],
           'reachWhenNobodySwam': reach},
          unmeasured=not w['read'] or (bool(swimmers) and all(w['swam'][p] is None for p in swimmers)))
    S.row('MOAT_drains_fast', dry_at is not None, {'dryAfterTicks': dry_at, 'heldAfterTicks': drain['heldAfterTicks'],
                                                   'bound': MOAT_DRAIN_TICKS,
                                                   'wetSquares': None if dl is None else sum(1 for v in dl if v)},
          unmeasured=dl is None or None in dl)
    # the drained ring holds the swimmers; capture two from the lip, by the pit-trap scene's idiom (_pit_trap_raid): the
    # raiders the drain did not catch left the map when it first held one, and each captive gets a fresh warden on a plot
    # square, all ordered at once. The 2026-11-21 sitting on game b: the one unarmed colonist the raid came for was
    # FleeAndCower, then downed, once in the drained moat itself among the held raiders, and never finished a capture; healed,
    # he made one prisoner and was gone before the second order. He is taken off the map too, so no held raider has him to fight.
    S.ticks(60)
    inside = _moat_in_ring(S, G)
    held = [i for i in inside if 'held=True' in i[2]]
    loose = [i for i in inside if 'held=False' in i[2]] if dry_at is not None else []
    gone, bait = drain['gone'], drain['bait']
    if held and drain['heldAfterTicks'] is None:
        gone, bait = _raid_driven_off(S, {i[0] for i in inside}), _moat_bait_off(S, G)
    caught = []
    for pid, at, v in held:                         # every held raider gets a warden; the row asks for two prisoners
        lip = _moat_plot_lip(at)                    # in the plot: the drained moat cuts a warden off from the outer bank
        c = {'pawn': pid, 'verdict': v.split()[1] if len(v.split()) > 1 else v, 'lip': lip, 'after': v,
             'warden': S.pawn('Colonist', lip, 'player')}
        c['accepted'] = S.call('jawa/ordered_job', pawnId=c['warden'], jobDef='RM_CaptureDown', targetAId=pid,
                               targetBX=lip[0], targetBZ=lip[1]).get('accepted')
        caught.append(c)
    trace = [_capture_trace_line(S, caught)]
    for _ in range(MOAT_CAPTURE_TICKS // 60):
        waiting = [c for c in caught if 'prisoner=True' not in c['after']]
        if len(caught) - len(waiting) >= 2 or not waiting:   # nobody left to wait for (one held raider): do not tick 900 for nothing
            break
        for _half in (0, 1):                        # the trace reads every 30 ticks; the verdict every 60, as before
            S.ticks(30)
            trace.append(_capture_trace_line(S, caught))
        for c in waiting:
            c['after'] = S.sc(NSP, 'ProofCaptureDown', c['pawn'])
    S.r['moatCaptureTrace'] = trace                 # beside the rows: a row's detail is cut short in the evidence file
    for c in caught:
        c['wardenAbleAfter'] = _able(S, c['warden'])
    S.r['moatWardenHits'] = {c['warden']: _hits_on(S, c['warden']) for c in caught}
    # Fewer than two prisoners where every unfinished capture lost its warden (downed) or its captive (no longer read)
    # did not ask the mod: UNMEASURED, never FAIL. A held raider beside the lip can down the warden before the capture
    # pins it (RIMMANDRAKE_PROBE_FLOWWORKS_WARDEN_DOWNED_BESIDE_HELD_RAIDER); 'wardensDowned' counts them on the row.
    made = [c for c in caught if 'prisoner=True' in c['after']]
    lost = [c for c in caught if c not in made and (c['wardenAbleAfter'] is False or not c['after'].startswith('VERDICT'))]
    S.row('MOAT_two_held_and_captured', len(made) >= 2,
          {'held': [h[0] for h in held], 'prisoners': [c['pawn'] for c in made], 'wardensDowned': len([c for c in caught if c['wardenAbleAfter'] is False]),
           'captured': caught, 'freeRaidersDrivenOff': len(gone), 'baitColonist': bait or 'not on the map',
           'standingLooseInTheDrainedMoat': loose},
          unmeasured=not swimmers or dry_at is None or (len(held) < 2 and (bool(held) or not loose))
          or (bool(held) and len(made) < 2 and len(made) + len(lost) == len(caught)))
    # RIMMANDRAKE_HOLD_FLOWWORKS_PIT_PRISONERS_THREE_CAPTURE_FAULTS: a held raider who cannot climb out cannot reach a warden on the rim (RM_PitReach: melee reach is the climb criterion)
    # (setting pitLipMeleeDeniedEnabled, shipped on). Red before 1c053b325bc5: visit 8 run T042734 (2 wardens downed) and the
    # sitting's E3 (a warden standing on the rim downed in 360 ticks by 3 stabs).
    raiders = set(G['raiders'])
    stabs = _rim_stabs(S.r['moatWardenHits'], raiders)
    S.row('MOAT_rim_wardens_not_stabbed', not any(stabs.values()) and not any(c['wardenAbleAfter'] is False for c in caught),
          {'hitsByHeldRaiders': {w: h for w, h in stabs.items() if h}, 'wardens': len(caught),
           'wardensDowned': len([c for c in caught if c['wardenAbleAfter'] is False])},
          unmeasured=not caught or any(not isinstance(h, list) for h in S.r['moatWardenHits'].values()))
    _moat_fuel(S, G, dry_at, 'MOAT')
    # control: the same raid with the leaf lowered -- they walk over the bridge, one after the other, and nobody swims
    S.again()
    G = _moat_stage(S, raised=False)
    c = _moat_watch(S, G, until_swimmers=0, until_crossed=2)
    S.row('MOAT_control_bridge_down_no_swim', len(c['crossed']) >= 2 and not c['swam'],
          {'swimmers': sorted(c['swam']), 'crossedToThePlot': sorted(c['crossed']), 'reachedTheRing': sorted(c['reached']),
           'read': sorted(c['read']), 'polls': c['polls'], 'leafDown': c['leafDown']},
          unmeasured=not c['read'] or not c['leafDown'] or (not c['swam'] and len(c['crossed']) < 2))


def _moat_fuel(S, G, dry_at, tag):
    """Chemfuel from the Dump tank, through the powered pump, into the drained moat; then the toss-flame order lights it."""
    _poll_ticks(S, lambda: 'running=True' in S.sc(NSP, 'ProofPump', '%d,%d' % G['pump']), 400)
    p0 = S.sc(NSP, 'ProofPump', '%d,%d;pour' % G['pump'])
    S.ticks(4 * 250); S.pulse(10)
    p1 = S.sc(NSP, 'ProofPump', '%d,%d' % G['pump'])
    rows = S.cells(G['ring'])
    fuel = [c for c, q in zip(G['ring'], rows) if q.get('fluid') == FUEL and q.get('dl')]
    t0, t1 = kv(p0).get('tank', ''), kv(p1).get('tank', '')
    units = [int(t.rsplit(':', 1)[1]) if t.rsplit(':', 1)[-1].isdigit() else None for t in (t0, t1)]
    blind = (_vacuous(p0) or _vacuous(p1) or 'running=True' not in p0 or None in units or not rows
             or all(not q for q in rows) or dry_at is None)
    S.row(tag + '_chemfuel_pumped', bool(fuel) and units[1] < units[0],
          {'pumpBefore': p0, 'pumpAfter': p1, 'chemfuelSquares': len(fuel), 'drained': dry_at is not None}, unmeasured=blind)
    if fuel:
        near = next((c for c in fuel if _moat_lip(G, c)), fuel[0])      # a chemfuel square a colonist on solid ground can stand by
        _toss(S, near, tag + '_moat_burns', at=_moat_lip(G, near))
    else:
        S.row(tag + '_moat_burns', False, 'no chemfuel square in the moat to light', unmeasured=True)


# sc_moat_walkers (owner, 2026-11-23: no raid in a test unless the mod's own function is about raiders; the cheapest test that
# decides the bar, standing_rulings.md): each part of moat_raid_sequence that one ordered colonist can decide, on sc_moat_raid's
# own map. What only raiders decide (they choose to swim, they are held and taken from the rim as enemies, they stab no
# warden) stays with sc_moat_raid, which is paused. The rim capture with no raid is sc_hole_prison's.
MW_POLL, MW_POLLS = 30, 120          # a swim of four squares is watched every 30 ticks, at most 3,600 ticks
MW_REACH_TICKS = 600                 # the labels follow a pour within about 60 ticks (visit 10); ten times that is a refusal
MW_BLOCK_TICKS = 1500                # an order that a drained moat refuses is given this long to be wrong


def _at(S, pid):
    """(x, z) of a pawn on the map (jawa/site_state), or None when the read does not name it."""
    p = next((q for q in S.call('jawa/site_state').get('pawns') or [] if q.get('id') == pid), None)
    return None if p is None or p.get('x') is None else (p['x'], p['z'])


def _mw_in_plot(G, at):
    return at is not None and O[0] + MOAT_W <= at[0] < O[0] + MOAT_N - MOAT_W and O[1] + MOAT_W <= at[1] < O[1] + MOAT_N - MOAT_W


def _order_said(r, pid):
    """What jawa/order_pawn said of one pawn. Its success means arrival, so at waitTicks=0 it is False for a good order too."""
    p = next((q for q in r.get('pawns') or [] if q.get('id') == pid), None)
    if p is None:
        return ('no pawn row: %s' % (r.get('message') or r.get('error') or r))[:120]
    return 'canReach=%s accepted=%s job=%s' % (p.get('canReach'), p.get('orderAccepted'), p.get('curJob'))


def _mw_cross(S, G, pid, to):
    """One drafted colonist is ordered across; every MW_POLL ticks his square and ProofSwim under him are read. -> what was seen."""
    # visit 10 (ArchSmall and Steve1, 2026-11-24): the scene ordered 4 ticks after its staged pour, while the mod's reach labels
    # (RM_WallReach, relabelled on the tick) still held the dry 4 m walls, so the Goto was dropped and he never moved. He is
    # ordered once the mod says he can reach the plot; if it never says so, the order goes out at the bound and the row shows it.
    reach = []

    def open_():
        reach.append(S.sc(WALLREACH, 'ProofReachPair', '%s;%d,%d' % (pid.replace('Human', ''), to[0], to[1])))
        return 'canReach=True' in reach[-1]
    after = _poll_ticks(S, open_, MW_REACH_TICKS, step=30)
    r = S.call('jawa/order_pawn', pawnId=pid, x=to[0], z=to[1], waitTicks=0, draft=True)
    seen = {'orderSaid': _order_said(r, pid), 'start': _at(S, pid), 'reads': 0, 'swam': False, 'tired': None, 'arrived': False, 'last': None,
            'refused': 0, 'reachAfterTicks': after, 'reach': reach[-1]}
    ring = set(G['ring'])
    for _ in range(MW_POLLS):
        S.ticks(MW_POLL)
        at = _at(S, pid)
        if at is None:
            seen['refused'] += 1
            continue
        seen['last'], seen['reads'] = at, seen['reads'] + 1
        txt = S.sc(SWIMP, 'ProofSwim', '%d,%d' % at)
        if txt.startswith('SWIM ' + pid + ' '):
            d = kv(txt)
            if d.get('deepCell') == 'True' and at in ring:
                seen['swam'] = True
            if seen['swam']:
                try:
                    seen['tired'] = max(seen['tired'] or 0.0, float(d.get('exhaustion')))
                except (TypeError, ValueError):
                    pass
        if _mw_in_plot(G, at):
            seen['arrived'] = True
            break
    return seen


def _moat_walkers(S):
    G = _moat_stage(S, raised=True, raiders=False)
    bank, plot = G['raiders_at'][0], (G['col'][0], G['col'][1] + 1)
    w = S.pawn('Colonist', bank, 'player')
    c = _mw_cross(S, G, w, plot)
    # raised leaf: the way over is through the water. Across with no swim read is the bar's false pass ("walking across")
    S.row('MW_raised_leaf_swims_and_tires', c['swam'] and (c['tired'] or 0) > 0, c,
          unmeasured=not c['reads'] or (not c['swam'] and not c['arrived']) or (c['swam'] and c['tired'] is None))
    up = S.sc(DOORS, 'ProofSetGate', 'current|%d,%d|true' % G['sluice'])
    require('lifted=True' in up, 'the sluice did not lift: %s' % up)
    dry_at, dl = None, None
    for k in range(1, MOAT_DRAIN_TICKS // (4 * MOAT_POLL) + 1):
        S.ticks(4 * MOAT_POLL)
        dl = S.dl(G['ring'])
        if None not in dl and not any(dl):
            dry_at = k * 4 * MOAT_POLL
            break
    S.row('MW_drains_fast', dry_at is not None, {'dryAfterTicks': dry_at, 'bound': MOAT_DRAIN_TICKS,
                                                 'wetSquares': None if dl is None else sum(1 for v in dl if v)},
          unmeasured=dl is None or None in dl)
    # drained, leaf up, no ladder: a colonist ordered over a 4 m wall stays where he is
    g = S.pawn('Colonist', bank, 'player')
    S.call('jawa/order_pawn', pawnId=g, x=plot[0], z=plot[1], waitTicks=0, draft=True)
    S.ticks(MW_BLOCK_TICKS)
    at = _at(S, g)
    S.row('MW_drained_moat_is_not_walked_over', not _mw_in_plot(G, at), {'from': bank, 'to': plot, 'at': at, 'dry': dry_at is not None},
          unmeasured=at is None or dry_at is None)
    _moat_fuel(S, G, dry_at, 'MW')
    S.again()
    G = _moat_stage(S, raised=False, raiders=False)
    w = S.pawn('Colonist', bank, 'player')
    c = _mw_cross(S, G, w, plot)
    leaf = kv(S.sc(DPROOF, 'ProofLeaf', '%d,%d' % G['deck']))
    down = leaf.get('progress') == '0' and leaf.get('target') == 'lowered'
    S.row('MW_lowered_leaf_bears_him_dry', c['arrived'] and not c['swam'], dict(c, leafDown=down),
          unmeasured=not c['reads'] or not down or (not c['swam'] and not c['arrived']))


def _toss(S, target, rid, want_fire=True, at=None):
    """The toss-flame order (RM_TossFlame.cs): the colonist walks to the rim and tosses. A lit canal or pond carries the
    liquid-fire engine's own flame, not a vanilla Fire, and chemfuel can burn out within the wait, so the row polls the
    engine's cell report (burning=True) and a vanilla Fire on the square every 60 ticks and keeps the first sight."""
    col = S.pawn('Colonist', at or (target[0], target[1] + 4), 'player')
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
# RIMMANDRAKE_STAGE_FLOWWORKS_PIT_TRAP_RAID_NONE_FELL (Test Pilot sitting, game b 2026-11-21): the trench lay ACROSS the raid's
# path, 9 wide and 1 deep, so each raider stood on the deck for one square (about 15 ticks). A plank deck is ONE span and
# gives way on the total load (120 kg, two raiders): one raider alone walked over it and the lids stayed (57,60 read
# covered=True, held=False), and a raid that arrived strung out never put two on it (9 raiders within 2 squares, 200 polls,
# nobody fell: visit 2's miss). The fall was chance. Now it is his pit-trap PASSAGE (scenes.json): a wall line with a gap,
# and the covered pit runs north from the gap ALONG the raid's path, TRAP_PL squares long, so the raiders the gap funnels
# stand on the deck together (4 of 4 live raids: two held within 210 ticks of the first step). A strip of ground stays
# each side of the pit in the gap: the capture's lip, and the way round for the control and for the raid after the fall.
TRAP_PW, TRAP_PL = 2, 8                             # pit squares: x = O[0]-1 .. O[0], z = O[1] .. O[1]+7
TRAP_STRIP = 1                                      # ground left each side of the pit inside the gap
TRAP_WALL = 18                                      # the wall line reaches this far each side of O[0], at z = O[1]
TRAP_COVER = 'RM_PitCover_PlankLattice'             # gives way under 120 kg on the deck: about two raiders at once
TRAP_TREE = 'Plant_TreeOak'                         # wood the raiders could chop for a ladder (scenes.json: saplings beside it)
RAID_STOP_ON = 'clock_discontinuity,modal_stuck,colony_loss,cancel'   # a raid hurts, downs and kills by design
TRAP_POLL, TRAP_POLLS = 60, 200                     # 12,000 ticks: fall, chop, ladder; 60-tick reads as TR_POLL (why there)
TRAP_RAID_AT = (O[0], O[1] - 12)                     # 8-square arrival scatter stays south of the wall (it was O1-4: some
                                                     # landed north of the trench, between it and the defenders)


def _trap_cells():
    x0 = O[0] - TRAP_PW // 2
    return [(x0 + i, O[1] + j) for j in range(TRAP_PL) for i in range(TRAP_PW)]


def _trap_walls():
    """The wall line at z = O[1], broken by the gap: the pit's width and TRAP_STRIP squares of ground each side."""
    x0 = O[0] - TRAP_PW // 2
    gap = range(x0 - TRAP_STRIP, x0 + TRAP_PW + TRAP_STRIP)
    return [(x, O[1]) for x in range(O[0] - TRAP_WALL, O[0] + TRAP_WALL + 1) if x not in gap]


def _trap_rect(pit, pad=1):
    xs, zs = [c[0] for c in pit], [c[1] for c in pit]
    return '%d,%d,%d,%d' % (min(xs) - pad, min(zs) - pad, max(xs) - min(xs) + 1 + 2 * pad, max(zs) - min(zs) + 1 + 2 * pad)


def _trap_lip(cell):
    """The strip square beside pit square `cell` (every pit square touches one: the pit is TRAP_PW = 2 wide)."""
    x0 = O[0] - TRAP_PW // 2
    return (x0 - 1 if cell[0] == x0 else x0 + TRAP_PW, cell[1])


def _cheb(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


# RIMMANDRAKE_TRACE_FLOWWORKS_FALLEN_RAIDER_WAITS_FOR_NO_LADDER: the fetch scene's pit is 3 m (6 levels), the deepest a
# portable ladder spans (portableLadderMaxLevels 6; RaiderTrenchChecks pins "4 m is past a 3 m ladder"). At 4 m (8) no
# raider can ladder it by the mod's own rule, so the scene asked for what the design refuses. The prison scene keeps 4 m.
TRAP_DEPTH, FETCH_DEPTH = 8, 6


def _pit_trap(S, fall=True, depth=TRAP_DEPTH):
    """Stage the passage: the wall line with its gap, the spiked pit running north from the gap (lidded when `fall`), trees
    south of the wall, two defenders north of the pit, and fire a raid of about six south of the wall. -> the pit cells.
    Staging that does not read back is an AssertionError (the scene's _staging row)."""
    pit = _trap_cells()
    S.dig(pit, depth)
    S.call('jawa/spawn_batch', ops=';'.join('RM_Spikes:%d,%d' % c for c in pit))
    S.call('jawa/build_batch', ops=';'.join('Wall:%d,%d' % c for c in _trap_walls()), stuff='BlocksGranite', faction='player')
    standing = {(t.get('x'), t.get('z')) for t in S.call('jawa/list_things', defName='Wall', rect='%d,%d,%d,1' % (
        O[0] - TRAP_WALL, O[1], 2 * TRAP_WALL + 1)).get('things') or []}
    require(set(_trap_walls()) <= standing, 'the passage wall did not read back whole: missing %s' % sorted(
        set(_trap_walls()) - standing)[:4])
    if fall:
        S.call('jawa/build_batch', ops=';'.join('%s:%d,%d' % ((TRAP_COVER,) + c) for c in pit), faction='player',
               wipeExisting=False)
        lids = [S.sc(EXC, 'ProofCover', '%d,%d' % c) for c in pit]
        require(all('covered=True' in t for t in lids), 'the trench lids did not read back covered: %s' % lids[:3])
    S.call('jawa/set_plants', ops='%s:%d,%d,3,2' % (TRAP_TREE, O[0] + 9, O[1] - 4), density=1.0, growth=1.0)
    for dx in (-2, 2):
        S.pawn('Colonist', (O[0] + dx, O[1] + TRAP_PL + 9), 'player')
    _fire_raid(S, 700, TRAP_RAID_AT)
    return pit


def _watch_trap(S, pit, until_ladder=True, until_held=0):
    """Run the raid in TRAP_POLL chunks on the narrowed governor; each poll reads every live raider's place and trap state
    (ProofTrap held=), and any portable ladder in or beside the trench. -> {reached, held, ladder, raiders, polls, refused}.
    reached: a raider came within 2 squares of the trench (the event the rows need); held: raider ids the trench holds;
    refused: ProofTrap replies that were no TRAP read for a raider standing in the trench (a blind read, not a "not held").
    until_held: stop once that many have fallen, held or dead on the spikes (sc_pit_trap_raid captures the living before
    the fetch can take them out; live game b 2026-11-21: one of two died on landing and a wait for two HELD ran the raid
    out for 12,000 ticks).
    fallen: how many went into the trench, the most of (held ids seen) and (held now + corpses on trench squares) at any
    poll. A raider who falls and dies on the spikes between two reads is never seen held (live game b 2026-11-21: one held
    of a raid whose fallen were gone by the next 300-tick read, and visit 2's FETCH_two_fell read one); nobody dies on a
    trench square without going in, so his corpse there counts. The rows that ask "did they fall" read fallen."""
    prior, S.B.stop_on = S.B.stop_on, RAID_STOP_ON
    seen = {'reached': False, 'held': set(), 'ladder': [], 'raiders': 0, 'polls': 0, 'last': [], 'refused': 0,
            'fallen': 0, 'corpses': 0}
    rect = _trap_rect(pit)
    try:
        for _ in range(TRAP_POLLS):
            S.ticks(TRAP_POLL)
            seen['polls'] += 1
            live = [p for p in S.call('jawa/list_pawns', faction='hostile').get('pawns') or []
                    if not p.get('dead') and p.get('x') is not None]
            seen['raiders'] = max(seen['raiders'], len(live))
            seen['last'] = [(p.get('id'), p.get('x'), p.get('z')) for p in live][:8]
            held_now = 0
            for p in live:
                if min(_cheb((p['x'], p['z']), c) for c in pit) <= 2:
                    seen['reached'] = True
                if (p['x'], p['z']) in pit:
                    txt = S.sc(NSP, 'ProofTrap', str(p['id']))
                    if not txt.startswith('TRAP '):
                        seen['refused'] += 1
                    elif 'held=True' in txt:
                        seen['held'].add(p['id'])
                        held_now += 1
            dead = [t for t in S.call('jawa/list_things', group='Corpse', rect=rect).get('things') or []
                    if (t.get('x'), t.get('z')) in pit]
            seen['corpses'] = max(seen['corpses'], len(dead))
            seen['fallen'] = max(seen['fallen'], len(seen['held']), held_now + len(dead))
            lad = S.call('jawa/list_things', defName='RM_LadderPortable', rect=rect).get('things') or []
            if lad:
                seen['ladder'] = lad
                if until_ladder:
                    break
            if until_held and seen['fallen'] >= until_held:
                break
    finally:
        S.B.stop_on = prior
    if seen['held'] or seen['fallen']:
        seen['reached'] = True
    return seen


def _fetch_rows(S, seen):
    no_raid = not seen['reached']
    why = '' if not no_raid else 'the raid never came within 2 squares of the trench (raiders seen %d, last %s); ' % (
        seen['raiders'], seen['last'])
    S.row('FETCH_two_fell', seen['fallen'] >= 2, why + 'fallen %d (held %s, corpses in the trench %d)' % (
        seen['fallen'], sorted(seen['held']), seen['corpses']), unmeasured=no_raid)
    S.row('FETCH_ladder_into_pit', bool(seen['ladder']),
          ('nobody fell, so there was no one to fetch; ' if not seen['held'] else '') + why + str(seen['ladder']),
          unmeasured=not seen['held'])


def _watch_fetch(S, pit, held):
    """After the ladder: run the raid on until one of the held raiders stands or lies OUT of the pit (carried up to the lip
    by RM_RaiderFetchFallen, or climbed out by the ladder). -> (out ids, polls)."""
    prior, S.B.stop_on = S.B.stop_on, RAID_STOP_ON
    out, polls = set(), 0
    try:
        for _ in range(TRAP_POLLS):
            S.ticks(TRAP_POLL)
            polls += 1
            for p in S.call('jawa/list_pawns', faction='hostile').get('pawns') or []:
                if p.get('id') in held and not p.get('dead') and p.get('x') is not None and (p['x'], p['z']) not in pit:
                    out.add(p['id'])
            if out:
                break
    finally:
        S.B.stop_on = prior
    return out, polls


def _fetch_fallen(S):
    pit = _pit_trap(S, depth=FETCH_DEPTH)
    seen = _watch_trap(S, pit)
    _fetch_rows(S, seen)
    # FLOWWORKS_RAIDERS_BUILD_LADDER_FOR_FALLEN: the ladder is half the bar; the fallen must come out (carried if downed)
    if seen['ladder'] and seen['held']:
        out, polls = _watch_fetch(S, pit, seen['held'])
        S.row('FETCH_fallen_brought_out', bool(out), 'held %s out %s after %d polls' % (sorted(seen['held']), sorted(out), polls))
    else:
        S.row('FETCH_fallen_brought_out', False, 'no ladder into the pit or nobody held, so nothing to bring out', unmeasured=True)
    return pit, seen


def _fetch_fallen_scene(S):
    _fetch_fallen(S)
    S.again()
    pit = _pit_trap(S, fall=False, depth=FETCH_DEPTH)   # control: no lid, so no one falls; the same raid must not ladder the pit
    seen = _watch_trap(S, pit, until_ladder=False)
    S.row('FETCH_control_none_fallen_no_ladder', not seen['ladder'] and not seen['held'] and not seen['fallen'],
          ('the raid never came within 2 squares of the trench (raiders seen %d); ' % seen['raiders'] if not seen['reached']
           else '') + 'held %s ladder %s' % (sorted(seen['held']), seen['ladder']), unmeasured=not seen['reached'])


# RIMMANDRAKE_REBUILD_FLOWWORKS_PITTRAP_SCENE_STOPPED_BY_OWN_RAID (visit 1, 2026-11-15): the draft fired its raid and ran
# S.ticks(4000) on the default governor, which stopped at tick 60 on that same raid (GovernorStop hostile_arrival) and the
# scene died with no rows; it also never ordered a capture, so prisoner=True could only ever read False. Now every tick from
# the raid on runs on RAID_STOP_ON (the moat scene's waiver), the watch stops once two are held, a warden on the north lip is
# ordered RM_CaptureDown on each (the moat's idiom), and each row needs its event: no raid at the trench, nobody fallen, a
# reply that is no VERDICT/TRAP read reads UNMEASURED, never PASS.
PTR_CAPTURE_TICKS = 900                              # one RM_CaptureDown from the lip (the moat's MOAT_CAPTURE_TICKS)


def _ptr_prisoner(S, pid):
    """One ProofCaptureDown read -> (True | False | None, reply); None: the reply was no VERDICT (a blind read)."""
    txt = S.sc(NSP, 'ProofCaptureDown', str(pid))
    return (None if not txt.startswith('VERDICT ') else 'prisoner=True' in txt), txt


def _able(S, pid):
    """Is colonist pid spawned, alive and not downed? (the raid this scene fires shoots the warden: live game b 2026-11-21,
    the first warden was downed at about t+600 of its capture window and the second order went to it.)"""
    return any(p.get('id') == pid and not p.get('dead') and not p.get('downed')
               for p in S.call('jawa/list_pawns', faction='player').get('pawns') or [])


def _ptr_fate(S, pid):
    """What the game recorded last about a captive that is no longer on the map: its kill event (who, with what, when),
    else the last damage, else 'no record'. Read from the bridge's damage recorder; a recorder that refuses says so."""
    r = S.B.call('jawa/damage_log', thingId=str(pid), limit=40) or {}
    ev = r.get('events') or []
    kills = [e for e in ev if e.get('kind') == 'kill']
    if kills:
        e = kills[-1]
        return 'killed at tick %s by %s (%s) at %s,%s' % (e.get('tick'), e.get('instigatorId') or 'no instigator',
                                                        e.get('damageDef'), e.get('x'), e.get('z'))
    if not r.get('success'):
        return 'damage recorder refused: %s' % str(r)[:80]
    return ('last damage %s at tick %s, no kill event' % (ev[-1].get('damageDef'), ev[-1].get('tick'))) if ev else 'no record'


def _raid_driven_off(S, held):
    """Every live hostile the pit does not hold leaves the map. -> the ids that left. One still there is a staging fault."""
    free = [p['id'] for p in S.call('jawa/list_pawns', faction='hostile').get('pawns') or []
            if p.get('id') not in held and not p.get('dead') and p.get('x') is not None]
    for pid in free:
        S.call('jawa/pawn_force_incapacitate', pawn=pid, action='vanish')
    left = [p['id'] for p in S.call('jawa/list_pawns', faction='hostile').get('pawns') or []
            if p.get('id') not in held and not p.get('dead') and p.get('x') is not None]
    require(not left, 'free raiders still on the map after the drive-off: %s' % left[:4])
    return free


def _pit_trap_raid(S):
    for k in ('captureDownEnabled', 'superdeepRoomsEnabled'):
        S.setting(k, True)
    pit = _pit_trap(S)                              # fires the raid after its last tick
    prior, S.B.stop_on = S.B.stop_on, RAID_STOP_ON  # the raid this scene fired is waived for every tick of it, capture too
    try:
        seen = _watch_trap(S, pit, until_ladder=False, until_held=2)
        no_raid = not seen['reached']
        where = {'raidersSeen': seen['raiders'], 'polls': seen['polls'], 'refused': seen['refused'], 'last': seen['last'],
                 'fallen': seen['fallen'], 'corpsesInTrench': seen['corpses']}
        S.row('PTR_two_fall', seen['fallen'] >= 2, dict(where, held=sorted(seen['held'])),
              unmeasured=no_raid or (seen['fallen'] < 2 and seen['refused'] > 0))
        # the scene's "driven off" moment: the capture is asked once the free raiders are gone (visit 2: the live raid
        # downed the warden on the lip inside the capture window, and the row could only read UNMEASURED). Every hostile
        # the pit does not hold leaves the map (Vanish: no corpse, no death event); the held stay where they fell.
        gone = _raid_driven_off(S, seen['held']) if seen['held'] else []
        # One warden per captive, both ordered at once (a player with two colonists at the rim does this). Live game b
        # 2026-11-21: with ONE warden capturing in turn, the warden finished the first capture at t=420 and, free again,
        # hit the second held raider beside its lip; one blow killed the spike-wounded man (damage_log: kill, instigator
        # the warden), and the second read was "no spawned pawn". A warden on RM_CaptureDown does not swing.
        caught = []
        for pid in sorted(seen['held'])[:2]:
            before, v = _ptr_prisoner(S, pid)
            cell = kv(v).get('cell', '')
            lip = _trap_lip(tuple(int(q) for q in cell.split(','))) if before is not None and ',' in cell else None
            c = {'pawn': pid, 'before': before, 'after': before, 'lip': lip, 'accepted': False, 'warden': None,
                 'wardenAbleAfter': None, 'verdict': v[:120], 'reply': v[:120], 'trace': []}
            if lip:
                c['warden'] = S.pawn('Colonist', lip, 'player')
                c['accepted'] = S.call('jawa/ordered_job', pawnId=c['warden'], jobDef='RM_CaptureDown', targetAId=pid,
                                       targetBX=lip[0], targetBZ=lip[1]).get('accepted')
            caught.append(c)
        ptrace = [_capture_trace_line(S, [c for c in caught if c['warden']])]
        for _ in range(PTR_CAPTURE_TICKS // TRAP_POLL):               # 60-tick reads: where each captive went, and when
            waiting = [c for c in caught if c['lip'] and c['after'] is False]
            if not waiting:
                break
            for _half in range(2):                                    # a 30-tick trace: who did what to whom, and when
                S.ticks(TRAP_POLL // 2)
                ptrace.append(_capture_trace_line(S, [c for c in caught if c['warden']]))
            for c in waiting:
                c['after'], c['reply'] = _ptr_prisoner(S, c['pawn'])
                c['trace'] = (c['trace'] + [c['reply'][8:60]])[-3:]
                at = kv(c['reply']).get('cell', '')
                if c['after'] is False and ',' in at and tuple(int(q) for q in at.split(',')) not in pit and 'out' not in c:
                    c['out'] = '%s out of the pit at %s, no prisoner: %s' % (c['pawn'], at, ' || '.join(ptrace[-3:])[:420])
        S.r['ptrCaptureTrace'] = ptrace             # beside the rows, as moatCaptureTrace: a row's detail is cut short
        for c in caught:
            c['reply'] = c['reply'][:120]
            if c['warden']:
                c['wardenAbleAfter'] = _able(S, c['warden'])
                if not c['wardenAbleAfter'] or not c['after']:
                    c['wardenHits'] = _hits_on(S, c['warden'])         # who took the warden off the capture, so the row names it
            if c['after'] is None:                                     # gone: say how, so the row names its own miss
                c['fate'] = _ptr_fate(S, c['pawn'])
        # a capture its warden could not finish (downed, no prisoner) or whose captive is gone did not ask the mod:
        # UNMEASURED, never FAIL
        S.row('PTR_fallen_become_prisoners', bool(caught) and all(c['before'] is False and c['after'] for c in caught),
              {'drivenOff': len(gone), 'captured': [
                  '%s prisoner %s->%s, warden able %s, %s%s' % (c['pawn'], c['before'], c['after'], c['wardenAbleAfter'],
                                                            c.get('fate') or c['reply'][8:70],
                                                            ' hits on warden %s: %s' % (c['warden'], c['wardenHits'])
                                                            if c.get('wardenHits') else '') for c in caught]} if caught
              else 'nobody fell, so there was no one to capture',
              unmeasured=not caught or any(c['before'] is None or c['after'] is None
                                           or (not c['after'] and c['wardenAbleAfter'] is False) for c in caught))
        # RIMMANDRAKE_TRACE_FLOWWORKS_HELD_RAIDER_LEFT_4M_TRENCH_ONCE: a raider the 4 m trench holds, alive and no prisoner,
        # read on a square outside the pit (seen once, 2026-11-21, on the old 1-wide staging; how he left was never read).
        # Red for that: the detail carries the last three 30-tick trace lines before the read that found him out.
        # CAUSE (Test Pilot 2026-11-23, Steve1, measured, fixed d15dd762b231): a comrade's fetch. A raider who falls and is
        # DOWNED on the spikes was picked up by a free raider standing on the rim: RM_RaiderFetchFallen's carry walked to
        # ClosestTouch, so the rim was near enough, and no ladder was ever set (run t18 caught it in the wild 1 run in 18;
        # ordered straight on a free raider it lifted the man out within 30 ticks, 2 of 2; on the fix 0 of 2, and the 3 m
        # fetch scene still brings its fallen out by the ladder, 2 of 2). The check that asks it on demand:
        # design/concepts/FlowWorks/version/in_game/testpilot_20261123/trench.py <out> 2 300 --down-held --order-fetch
        # (row TP_held_stay_held); the C# case is RaiderFetch_no_lift_from_the_rim_of_a_deep_pit.
        # RULED OUT, each by its own run: a ladder (none was read by the trench on any 30-tick read; 4 m is past a
        # portable ladder), a kidnap job on a held raider beside a colonist downed on the strip (the free raiders took the
        # colonists; the held stayed), the raid's flight (the held stayed when every free raider left the map), the old
        # across-the-gap staging (held raiders walked the trench floor to hit the wall at its end and stayed held), a
        # standing held raider (31 of 31 stayed for 1,500 ticks: only a downed one is carried).
        S.row('PTR_held_stay_in_the_trench', bool(caught) and not any('out' in c for c in caught),
              [c['out'] for c in caught if 'out' in c] or 'every captive read stood on a pit square until taken (%d trace lines)'
              % len(ptrace), unmeasured=not caught or all(c['before'] is None for c in caught))
        S.again()
        pit = _pit_trap(S, fall=False)              # control: no lid; the same raid must path round and nobody fall
        seen = _watch_trap(S, pit, until_ladder=False)
        S.row('PTR_control_open_pit_no_one_falls', not seen['held'] and not seen['fallen'],
              {'held': sorted(seen['held']), 'fallen': seen['fallen'], 'corpsesInTrench': seen['corpses'],
               'raidersSeen': seen['raiders'], 'refused': seen['refused'], 'last': seen['last']},
              unmeasured=not seen['reached'] or (not seen['held'] and not seen['fallen'] and seen['refused'] > 0))
    finally:
        S.B.stop_on = prior


# RIMMANDRAKE_REBUILD_FLOWWORKS_ISLANDS_SCENE_SPAWNED_A_DRAW_STYLE (visit 1, 2026-11-15): the draft spawned
# 'RM_SuspensionBridge' (a DrawStyleCategoryDef: spawn_batch 'unknown ThingDef'), dropped two bare gates in the channel, fired
# an unplaced raid and never staged a winch loss. Now the bridges are built through the mod's own drag (RM_SuspensionProofs.
# ProofBuild, RM_DrawbridgeProofs.ProofMakeDrawbridge with its winch houses), read back lowered, six sappers stand on the
# long span, both leaves go up, and each row needs its event: no raider on the span, no winch lost, no leaf down reads
# UNMEASURED, never PASS. If the sappers never take a winch in the window that row FAILs and the harness destroys the west
# winch itself (staged=True in the detail) so the drop and the escape are still asked. The control makes both winches
# unbreakable with RM_DrawbridgeProofs.ProofWinchHold (no damage reaches a held winch) and reads their hit points every
# poll; a held winch damaged or lost leaves the control UNMEASURED.
# RIMMANDRAKE_TRACE_FLOWWORKS_HELD_WINCH_FELL_IN_THE_CONTROL (Test Pilot, game b, 2026-11-21), HARNESS: the control used
# to put each winch back to full hit points before every 120-tick chunk. A frag grenade does 100 to the 200 hit point winch
# house, and two landed inside one chunk (read every 20 ticks: 200 -> 100 -> gone), so "held" winches fell (visit 2).
# RULED OUT: the mod dropping a leaf whose winch still stands (the winch left list_things on the read its leaf first said
# winch=False; the other leaf stayed up); stale winch ids after the restage (every reset answered success on fresh ids).
# RIMMANDRAKE_STAGE_FLOWWORKS_ISLAND_RAIDERS_NEVER_CROSS_LOWERED_LEAF (Test Pilot, game b, 2026-11-21), MOD: the mod's own
# winch job (JobGiver_RM_DrawbridgeWinch) sends the grenadiers at the winch; a frag blast at the winch always reaches the
# hinge anchor beside it and often a leaf deck, one lost square collapses the span, and the six stood on the steel span
# over two holes (CanReachMapEdge False, vanilla regions True, pocket grid current and right). Fix: the attacker's hits
# spare that bridge's decks and anchors (RM_DrawbridgeRaid.SparesBridge; selftest Drawbridge_R5_winch_attack_spares_the_
# leaf_it_would_cross). ProofLeaf now reads standing=n/m and ISL_lost_winch_drops_its_leaf needs every deck standing.
# RULED OUT: a bridge read freeing them (4 of 5 runs with no read stuck, 1 free: it flaked on the grenade scatter); a
# stale reachability or pocket grid after NotifyToggled (grid built at the current generation; the veto was correct).
# Probe: probe_islands_exit.py (--read edge pedge trace, --keep).
#   x: west island <= O0 | drawbridge O0..O0+4 (hole +1..+3) | pillar +4,+5 | steel span +5..+16 (hole +6..+15)
#      | pillar +16,+17 | drawbridge +17..+21 (hole +18..+20) | east island >= +21; channel dug 4 m at z = O1-3..O1+3
DPROOF = 'RimMandrake.FlowWorks.Pits.RM_DrawbridgeProofs'
SPROOF = 'RimMandrake.FlowWorks.Pits.RM_SuspensionProofs'
RAIDW = 'RimMandrake.FlowWorks.Pits.JobGiver_RM_DrawbridgeWinch'
ISL_DEEP, ISL_HALF = 8, 3                           # notches (4 m) and the channel's half-width in rows
ISL_PILLARS = (4, 5, 16, 17)                        # undug squares at z = O1 (dx from O0): anchors stand on them
ISL_DRAW = (((0, 4), 'A', -1), ((17, 21), 'B', 22))   # (dx span, hinge bank, winch dx): each winch on its outer island
ISL_LONG = (5, 16)                                  # the steel span between the pillars (up to 20 between supports)
ISL_LEAVES = (2, 19)                                # a deck square of each leaf
ISL_WINCH_DEF = 'RM_DrawbridgeWinch_Timber'
ISL_KIND, ISL_RAIDERS = 'Grenadier_Destructive', 6  # sapper-capable (drawbridge_proof RAID_UP sapper variant)
ISL_POLL, ISL_POLLS = 120, 50                       # 6,000 ticks a watch


def _isl_xz(dx):
    return O[0] + dx, O[1]


def _isl_channel():
    return [(O[0] + dx, O[1] + dz) for dx in range(1, 21) for dz in range(-ISL_HALF, ISL_HALF + 1)
            if not (dz == 0 and dx in ISL_PILLARS)]


def _isl_leaf(S, dx):
    """That leaf's ProofLeaf read; a reply without its winch and progress (REFUSED, 'LEAF none') is a staging fault, never
    a lost winch or a dropped leaf."""
    txt = S.sc(DPROOF, 'ProofLeaf', '%d,%d' % _isl_xz(dx))
    d = kv(txt)
    require('winch' in d and 'progress' in d, 'leaf %d unreadable: %s' % (dx, txt))
    return d


def _isl_hostile_faction(S):
    """A hostile humanlike faction def from spawn_pawn's refusal of faction '?' (drawbridge_proof.faction's recipe)."""
    probe = S.B.call('jawa/spawn_pawn', _answer=True, kindDef=ISL_KIND, x=0, z=0, faction='?', count=1) or {}
    avail = (probe.get('details') or {}).get('available') or []
    hostile = [f.get('def') for f in avail if f.get('hostile') and f.get('def') not in ('Entities', 'Mechanoid', 'Insect')]
    fac = next((f for f in hostile if str(f).startswith('Pirate')), hostile[0] if hostile else None)
    require(fac, 'no hostile humanlike faction to spawn: %s' % str(probe)[:200])
    return fac


def _isl_stage(S, raiders=True):
    """raiders False (sc_islands_walker) puts one colonist on the span and spawns no hostile. Dig the channel, build both drawbridges (winches on the outer islands) and the steel span, read them back lowered,
    put two colonists on the west island and six sappers on the span, then raise both leaves. -> the staged state."""
    S.dig(_isl_channel(), ISL_DEEP)
    winch = []
    for (a, b), bank, wdx in ISL_DRAW:
        txt = S.sc(DPROOF, 'ProofMakeDrawbridge', '%d,%d;%d,%d;timber;%s;winch' % (_isl_xz(a) + _isl_xz(b) + (bank,)))
        d = kv(txt)
        require(d.get('ok') == 'True' and d.get('leaves') == '1', 'drawbridge %d..%d not built as one leaf: %s' % (a, b, txt))
        require(d.get('winchAt') == '%d,%d' % _isl_xz(wdx), 'drawbridge %d..%d winch not on its outer island: %s' % (a, b, txt))
        winch.append(_isl_xz(wdx))
    txt = S.sc(SPROOF, 'ProofBuild', '%d,%d;%d,%d;steel;god' % (_isl_xz(ISL_LONG[0]) + _isl_xz(ISL_LONG[1])))
    require(txt.startswith('BUILD ok=True') and kv(txt).get('records') == '1', 'the long span was not built: %s' % txt)
    leaves = [_isl_leaf(S, dx) for dx in ISL_LEAVES]
    require(all(l.get('progress') == '0' and l.get('winch') == 'True' for l in leaves),
            'the drawbridges do not read lowered with their winches: %s' % leaves)
    ids = []
    for c in winch:
        t = S.call('jawa/list_things', defName=ISL_WINCH_DEF, rect='%d,%d,1,1' % c).get('things') or []
        require(len(t) == 1 and t[0].get('maxHitPoints'), 'no winch house (with its hit points) listed at %s: %s' % (c, t))
        ids.append((t[0]['id'], t[0].get('maxHitPoints')))
    for dz in (-1, 1):
        S.pawn('Colonist', (O[0] - 3, O[1] + dz), 'player')
    if not raiders:
        walker = S.pawn('Colonist', _isl_xz(10), 'player')
        _isl_raise(S)
        return {'winch': winch, 'winch_ids': ids, 'walker': walker}
    fac = _isl_hostile_faction(S)
    raiders = []
    for k in range(ISL_RAIDERS):
        at = _isl_xz(7 + k)
        r = S.call('jawa/spawn_pawn', kindDef=ISL_KIND, x=at[0], z=at[1], faction=fac, count=1)
        pid = ((r.get('pawns') or [{}])[0]).get('id')
        require(pid, 'raider not spawned at %s: %s' % (at, r))
        # set BEFORE the lord: LordToil_AssaultColonySappers picks its sappers at UpdateAllDuties (Mining raw 20; a refusal
        # from a backstory that disables mining is a reading, the IsGoodSapper check below decides)
        S.B.call('jawa/set_pawn_skill', _answer=True, pawn=pid, skill='Mining', level=20)
        has = S.sc('RimWorld.SappersUtility', 'HasBuildingDestroyerWeapon', pid)
        if has != 'True':
            S.call('jawa/pawn_gear', pawn=pid, action='clear', clearWhat='equipment')
            S.call('jawa/pawn_gear', pawn=pid, action='equip', **{'def': 'Weapon_GrenadeFrag'})
        raiders.append(pid)
    S.call('jawa/lord_assault_spawn', pawns=','.join(raiders), sappers=True)
    good = [p for p in raiders if S.sc('RimWorld.SappersUtility', 'IsGoodSapper', p) == 'True']
    require(good, 'no raider IsGoodSapper (none gets the Sapper duty, so none would go for a winch): %s' % raiders)
    _isl_raise(S)
    return {'winch': winch, 'winch_ids': ids, 'raiders': raiders, 'sappers': good}


def _isl_raise(S):
    for dx in ISL_LEAVES:
        txt = S.sc(DPROOF, 'ProofDevSet', '%d,%d;raise;instant' % _isl_xz(dx))
        require(kv(txt).get('target') == 'raised' and kv(txt).get('progress', '0') != '0', 'leaf %d did not go up: %s' % (dx, txt))


def _isl_counter(S):
    r = S.B.call('jawa/mod_settings_field', _answer=True, typeName=RAIDW, field='WinchJobs', action='get') or {}
    try:
        return int(r.get('value'))
    except (TypeError, ValueError):
        return None


def _isl_watch(S, st, until='loss', hold=False):
    """ISL_POLL chunks on the narrowed governor (a raid hurts, downs and kills by design). Each poll: our raiders still alive,
    those on the span (inside the channel) and those on an island, and which winch still stands. `until`: 'loss' stops at
    the first winch lost, 'escape' at the first raider on an island, None runs every poll. `hold` makes both winches
    unbreakable first (ProofWinchHold: the control) and reads each winch's hit points every poll: `held` is the hold's own
    answer, `hurt` the leaves whose held winch read below its full hit points."""
    prior, S.B.stop_on = S.B.stop_on, RAID_STOP_ON
    seen = {'polls': 0, 'on_span': 0, 'live': 0, 'escaped': [], 'lost': [], 'held': None, 'hurt': [], 'last': []}
    mine = set(st['raiders'])
    try:
        if hold:
            got = [kv(S.sc(DPROOF, 'ProofWinchHold', '%d,%d;on' % _isl_xz(dx))) for dx in ISL_LEAVES]
            seen['held'] = all(g.get('held') == 'True' and g.get('winch') == 'True' for g in got)
        for _ in range(ISL_POLLS):
            S.ticks(ISL_POLL)
            if hold:
                for dx, c, (_, full) in zip(ISL_LEAVES, st['winch'], st['winch_ids']):
                    t = S.B.call('jawa/list_things', _answer=True, defName=ISL_WINCH_DEF, rect='%d,%d,1,1' % c) or {}
                    hp = [x.get('hitPoints') for x in t.get('things') or []]
                    if hp != [full] and dx not in seen['hurt']:
                        seen['hurt'].append(dx)
            seen['polls'] += 1
            live = [p for p in S.call('jawa/list_pawns', faction='hostile').get('pawns') or []
                    if p.get('id') in mine and not p.get('dead') and p.get('x') is not None]
            seen['live'] = len(live)
            seen['last'] = [(p['id'], p['x'], p['z']) for p in live]
            seen['on_span'] = max(seen['on_span'], sum(1 for p in live if O[0] < p['x'] < O[0] + 21
                                                       and abs(p['z'] - O[1]) <= ISL_HALF))
            seen['escaped'] = sorted(p['id'] for p in live if p['x'] <= O[0] or p['x'] >= O[0] + 21)
            seen['lost'] = [dx for dx in ISL_LEAVES if _isl_leaf(S, dx).get('winch') != 'True']
            if (until == 'loss' and seen['lost']) or (until == 'escape' and seen['escaped']):
                break
    finally:
        S.B.stop_on = prior
    return seen


def _islands(S):
    st = _isl_stage(S)
    w0 = _isl_counter(S)
    seen = _isl_watch(S, st, until='loss')
    no_raid = not seen['on_span']
    why = 'no raider of ours stood on the span (last %s); ' % seen['last'] if no_raid else ''
    S.row('ISL_trapped_while_winches_stand', not seen['escaped'],
          why + 'on an island before any winch fell %s, polls %d' % (seen['escaped'], seen['polls']), unmeasured=no_raid)
    w1 = _isl_counter(S)
    jobs = None if w0 is None or w1 is None else w1 - w0
    S.row('ISL_raiders_destroy_a_winch', bool(seen['lost']),
          why + 'leaves whose winch fell %s, WinchJobs +%s, sappers %s' % (seen['lost'], jobs, st['sappers']), unmeasured=no_raid)
    lost, staged = list(seen['lost']), False
    if not lost and not no_raid:
        gone = S.call('jawa/destroy_batch', rects='%d,%d,1,1' % st['winch'][0], categories='Building')
        require(int(gone.get('destroyed') or 0) >= 1, 'the staged winch loss destroyed nothing: %s' % gone)
        lost, staged = [ISL_LEAVES[0]], True
    prior, S.B.stop_on = S.B.stop_on, RAID_STOP_ON
    try:
        S.ticks(10)                                      # the crash lands on the next drive step
    finally:
        S.B.stop_on = prior
    after = [_isl_leaf(S, dx) for dx in lost]
    # A leaf "dropped" only if its decks still stand: the raiders' grenades at the winch used to wreck the hinge anchor and
    # a deck, the span collapsed, and ProofLeaf went on reading "progress 0" over a hole (test pilot 2026-11-21).
    def _stands(l):
        n, _, m = (l.get('standing') or '').partition('/')
        return n.isdigit() and m.isdigit() and int(m) > 0 and n == m
    dropped = [dx for dx, l in zip(lost, after) if l.get('progress') == '0' and _stands(l)]
    wrecked = [dx for dx, l in zip(lost, after) if not _stands(l)]
    S.row('ISL_lost_winch_drops_its_leaf', bool(lost) and dropped == lost,
          (why or ('' if lost else 'no winch was lost; ')) + ('leaf %s lost its decks with its winch; ' % wrecked if wrecked else '')
          + 'staged=%s leaves %s after %s' % (staged, lost, after),
          unmeasured=not lost)
    out = _isl_watch(S, st, until='escape') if dropped else None
    S.row('ISL_raiders_escape', bool(out and out['escaped']),
          ('no leaf came down, so there was no way off; ' if not dropped else '') +
          ('' if not out else 'on an island %s, live %d, polls %d, last %s' % (out['escaped'], out['live'], out['polls'],
                                                                               out['last'])),
          unmeasured=not dropped or not (out and (out['live'] or out['escaped'])))
    S.again()                                            # control: the same span, both winches held at full hit points
    st = _isl_stage(S)
    c0 = _isl_counter(S)
    ctl = _isl_watch(S, st, until=None, hold=True)
    c1 = _isl_counter(S)
    up = [_isl_leaf(S, dx) for dx in ISL_LEAVES]
    raised = all(l.get('target') == 'raised' and l.get('progress', '0') != '0' for l in up)
    leaky = bool(ctl['lost']) or bool(ctl['hurt']) or not ctl['held']
    S.row('ISL_control_unbreakable_winches_stay_trapped', not ctl['escaped'] and raised,
          ('no raider of ours stood on the span; ' if not ctl['on_span'] else '') +
          ('the hold did not hold (lost %s, hurt %s); ' % (ctl['lost'], ctl['hurt']) if leaky else '') +
          'held winches %s, on an island %s, leaves %s, WinchJobs +%s, polls %d' % (
              ctl['held'], ctl['escaped'], [l.get('progress') for l in up],
              None if c0 is None or c1 is None else c1 - c0, ctl['polls']),
          unmeasured=not ctl['on_span'] or leaky)


# sc_islands_walker (owner, 2026-11-23: the cheapest test that decides the bar): the bridges' half of
# island_bridges_trap_and_fail, with one ordered colonist on the span and no raider. That raiders go for a winch and break it
# stays with sc_islands, which is paused.
ISLW_WAIT = 1500


def _islands_walker(S):
    st = _isl_stage(S, raiders=False)
    home = (O[0] - 3, O[1])
    S.call('jawa/order_pawn', pawnId=st['walker'], x=home[0], z=home[1], waitTicks=0, draft=True)
    S.ticks(ISLW_WAIT)
    at, up = _at(S, st['walker']), [_isl_leaf(S, dx) for dx in ISL_LEAVES]
    raised = all(l.get('target') == 'raised' and l.get('progress', '0') != '0' for l in up)
    S.row('ISLW_raised_leaves_hold_him_on_the_span', at is not None and O[0] < at[0] < O[0] + 21, {'at': at, 'leaves': up},
          unmeasured=at is None or not raised)
    gone = S.call('jawa/destroy_batch', rects='%d,%d,1,1' % st['winch'][0], categories='Building')
    require(int(gone.get('destroyed') or 0) >= 1, 'the staged winch loss destroyed nothing: %s' % gone)
    S.ticks(10)                                          # the crash lands on the next drive step
    leaf, other = _isl_leaf(S, ISL_LEAVES[0]), _isl_leaf(S, ISL_LEAVES[1])
    n, _, m = (leaf.get('standing') or '').partition('/')
    down = leaf.get('progress') == '0' and n.isdigit() and n == m and int(m) > 0
    S.row('ISLW_lost_winch_drops_its_leaf_alone', down and other.get('progress', '0') != '0' and leaf.get('winch') != 'True',
          {'lost': leaf, 'other': other})
    S.call('jawa/order_pawn', pawnId=st['walker'], x=home[0], z=home[1], waitTicks=0, draft=True)
    S.ticks(ISLW_WAIT)
    at = _at(S, st['walker'])
    S.row('ISLW_he_walks_off_over_the_dropped_leaf', at is not None and at[0] <= O[0], {'at': at}, unmeasured=at is None or not down)


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


def _walk_kit(S):
    """The walk's map and its reads, shared by sc_walk (his walk) and its three split scenes: the cells, the journal tap
    opened at scene start, the pond's litres, the state digest and pays() (a row: the pond's litres fell and the cells it
    paid into are wet)."""
    import types
    import validation_core as V
    K = types.SimpleNamespace(tap=V.tap_start(S.B))
    K.pond = [(O[0] - 4 + i, O[1] - 1 + j) for i in range(3) for j in range(3)]
    K.swim = [(O[0] + 2 + i, O[1] - 6 + j) for i in range(3) for j in range(3)]      # apart from the pond, moat and fuel pit
    K.fuel_pit = [(O[0] + 2 + i, O[1] + 4 + j) for i in range(3) for j in range(3)]
    K.moat3 = _line(O[0] - 14, O[1], 10)                                               # west of the pond, joins (O-4, O)
    moat = _line(O[0] - 1, O[1], 21)
    K.moat1, K.moat2 = moat[:10], moat[10:]
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
    K.litres, K.digest, K.pays = litres, digest, pays
    return K


def _walk_log_row(S, K, tag):
    """WALK_log_clean: no warning or error naming FlowWorks since the scene's tap opened, on a journal proven live and read
    without a gap (a lost or dead journal is UNMEASURED, never clean)."""
    import validation_core as V
    tap = K.tap
    alive = V.log_alive(S.B, tag).get('alive')
    ours = [str(x.get('Message', ''))[:160] for x in tap.since() if any(k in str(x.get('Message', '')).lower() for k in FW_MARKS)]
    S.row('WALK_log_clean', not ours, {'flowworks_lines': ours[:5], 'lost': tap.lost, 'alive': alive, 'gaps': tap.gaps[:3],
          'warn_plus_all_mods': len(tap.entries)}, unmeasured=bool(tap.lost) or not alive)


def _walk(S):
    """sc_walk on his full list. The bar: state digests match across a mid-way reload (control: a pre-fill reload differs);
    the pond pays again after the reload and an off/on of the master switch; no leftovers; the log clean (FlowWorks lines).
    Stage 6 visit 1 (RIMMANDRAKE_FINISH_FLOWWORKS_WALK_SCENE_HALF_THE_BAR_UNASKED): the draft compared 'stock'/'cells', keys
    engine_state never returns (None == None passed); and depthEngineEnabled snaps at game load unless depthEngineLiveForTests
    is set, so its off/on never stopped anything. Every row below refuses a vacuous read (UNMEASURED, never PASS).
    Holder run-1794816885 added the bar's swimmer (one in 2 m of water at the mid-way save, read again after the reload: same
    cell, still in deep water; "the swimmers stand on the bed" is its red) and its second order on the same map (chemfuel
    into its own pit first, then the pond drained into a third moat). Not here: prisoners at the save, the wetted garden
    (moved to 0.2.0), and a PUMPED chemfuel fill (the scene pours it through ProofFillWithFluid)."""
    K = _walk_kit(S)
    tap, pond, swim, fuel_pit, moat1, moat2, moat3 = K.tap, K.pond, K.swim, K.fuel_pit, K.moat1, K.moat2, K.moat3
    litres, digest, pays = K.litres, K.digest, K.pays

    S.setting('depthEngineLiveForTests', True)        # the off/on below must reach the running engine, not the next load
    S.dig(pond, 4); S.fill(pond, 2.0, WATER)
    S.dig(swim, 4); S.fill(swim, 2.0, WATER)          # brim-full 2 m: deep enough to swim (>= 1.8 m), a bank to leave by
    p0 = litres()
    S.dig(moat1, 4); S.pulse(40)
    pays('WALK_pond_pays', p0, moat1)

    swimmer = S.pawn('Colonist', swim[4], 'player')
    a = digest()
    if S.save_mid is None:
        S.row('WALK_reload_digest_matches', False, 'no mid-way save hook passed to the scene', unmeasured=True)
        S.row('WALK_swimmer_survives_reload', False, 'no mid-way save hook passed to the scene', unmeasured=True)
    else:
        r0 = _ph_read(S, swimmer)
        k0, t0 = _ph_swim(S, swimmer, swim)
        S.save_mid(); S.ticks(600); S.load_mid()
        b = digest()
        S.row('WALK_reload_digest_matches', a == b, (a, b), unmeasured=_vacuous(a) or _vacuous(b))
        r1 = _ph_read(S, swimmer)
        k1, t1 = _ph_swim(S, swimmer, swim)
        afloat = bool(k0) and k0.get('deepCell') == 'True'
        S.row('WALK_swimmer_survives_reload', afloat and bool(k1) and bool(r1) and r1['cell'] == r0['cell']
              and k1.get('deepCell') == 'True' and k1.get('water') == k0.get('water'),
              {'before': (r0 and r0['cell'], t0), 'after': (r1 and r1['cell'], t1)},
              unmeasured=not afloat or r0 is None or _vacuous(b))
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

    # the second order, on this same map (its false pass is "the repeat runs on a fresh map"): chemfuel first, into its own
    # pit, then the water drained after; the fuel keeps its stock, the pond pays a third time, the census holds exactly
    # water and chemfuel with every wet cell recorded
    S.walk(swimmer, (O[0] + 6, O[1] - 5), 600)        # out of the swim pool before the long run (not a row)
    S.dig(fuel_pit, 4); S.fill(fuel_pit, 1.0, FUEL); S.pulse(10)
    f0, p3 = S.dl(fuel_pit), litres()
    S.dig(moat3, 4); S.pulse(40)
    pays('WALK_second_order_pond_pays', p3, moat3)
    f1 = S.dl(fuel_pit)
    bad = None in f0 or None in f1 or not any(f0)
    S.row('WALK_second_order_fuel_holds', not bad and all(abs(x - y) <= 1e-6 for x, y in zip(f0, f1)), (f0, f1),
          unmeasured=bad)
    census2 = S.sc(FLUIDID, 'ProofCensus')
    m2 = re.search(r'unrecorded (\d+) \| fluids \[([^\]]*)\]', census2)
    fl = None if m2 is None else {x.strip() for x in m2.group(2).split(',') if x.strip()}
    S.row('WALK_second_order_no_leftovers', m2 is not None and m2.group(1) == '0' and fl == {WATER, FUEL}, census2,
          unmeasured=m2 is None)

    _walk_log_row(S, K, 'sc_walk')


# sc_walk split in three (RIMMANDRAKE_SHRINK_FLOWWORKS_SCENES_HUNG_BRIDGE_RAN_27_TIMES, design/specs/2026-11-24-oversized-
# scenes/table.md section 1: about eight claims in one scene, 11 runs and 3 not passed). Each scene stages only what its claim
# reads, on the FlowWorks tier list; no row reads another mod. The rows keep sc_walk's ids and logic (_walk_kit), so a fault
# that turned an sc_walk row red turns the same row red here (selftest_walk_scene.py).
WALK_RELOAD_GAP = 60     # ticks between the mid-way save and its load: the save must survive game time, not only a reload


def _walk_reload(S):
    """sc_walk_reload: a save and reload keep the pond and the swimmer. Dig and fill the pond and the swim pool, put a
    swimmer in 2 m of water, save, 60 ticks, load: the state digest is equal and the swimmer is in the same cell, still in
    deep water. Control: the scene-begin save (made before the fill) differs."""
    K = _walk_kit(S)
    S.setting('depthEngineLiveForTests', True)
    S.dig(K.pond, 4); S.fill(K.pond, 2.0, WATER)
    S.dig(K.swim, 4); S.fill(K.swim, 2.0, WATER)
    S.pulse(5)
    swimmer = S.pawn('Colonist', K.swim[4], 'player')
    a = K.digest()
    if S.save_mid is None:
        for rid in ('WALK_reload_digest_matches', 'WALK_swimmer_survives_reload', 'WALK_control_prefill_reload_differs'):
            S.row(rid, False, 'no mid-way save hook passed to the scene', unmeasured=True)
    else:
        r0 = _ph_read(S, swimmer)
        k0, t0 = _ph_swim(S, swimmer, K.swim)
        S.save_mid(); S.ticks(WALK_RELOAD_GAP); S.load_mid()
        b = K.digest()
        S.row('WALK_reload_digest_matches', a == b, (a, b), unmeasured=_vacuous(a) or _vacuous(b))
        r1 = _ph_read(S, swimmer)
        k1, t1 = _ph_swim(S, swimmer, K.swim)
        afloat = bool(k0) and k0.get('deepCell') == 'True'
        S.row('WALK_swimmer_survives_reload', afloat and bool(k1) and bool(r1) and r1['cell'] == r0['cell']
              and k1.get('deepCell') == 'True' and k1.get('water') == k0.get('water'),
              {'before': (r0 and r0['cell'], t0), 'after': (r1 and r1['cell'], t1)},
              unmeasured=not afloat or r0 is None or _vacuous(b))
        S.again()                                      # the control: the scene-begin save, made before the fill
        c = K.digest()
        S.row('WALK_control_prefill_reload_differs', c != a, (c, a), unmeasured=_vacuous(a) or c[0] is None)
    _walk_log_row(S, K, 'sc_walk_reload')


def _walk_switch(S):
    """sc_walk_switch: off and on leaves the water alone, and the switch reaches the running engine. The pond pays its
    first moat (the instrument sees a draw); off then on, the digest is equal; off, a dry moat dug onto the wet one stays
    dry for 600 ticks and the pond keeps its litres; on, the pond pays it; no leftover fluid."""
    import re
    K = _walk_kit(S)
    S.setting('depthEngineLiveForTests', True)        # the off/on must reach the running engine, not the next load
    S.dig(K.pond, 4); S.fill(K.pond, 2.0, WATER)
    p0 = K.litres()
    S.dig(K.moat1, 4); S.pulse(40)
    K.pays('WALK_pond_pays', p0, K.moat1)
    a2 = K.digest()
    S.setting('depthEngineEnabled', False); S.ticks(600); S.setting('depthEngineEnabled', True); S.ticks(600)
    b2 = K.digest()
    S.row('WALK_toggle_off_on_digest_matches', a2 == b2, (a2, b2), unmeasured=_vacuous(a2) or _vacuous(b2))
    p2 = K.litres()
    S.setting('depthEngineEnabled', False)
    S.dig(K.moat2, 4); S.ticks(600)
    held, p_off = S.dl(K.moat2), K.litres()
    bad = None in held or _vacuous((p2,)) or p_off is None
    S.row('WALK_switch_off_holds_water', not bad and not any(held) and p_off == p2, (p2, p_off, held), unmeasured=bad)
    S.setting('depthEngineEnabled', True); S.ticks(600); S.pulse(40)
    K.pays('WALK_pond_pays_again', p2, K.moat2)
    e, census = S.call('jawa/flowworks_engine_state'), S.sc(FLUIDID, 'ProofCensus')
    m = re.search(r'unrecorded (\d+) \| fluids \[([^\]]*)\]', census)
    bad = m is None or e.get('bodyCount') is None or a2[2] is None
    S.row('WALK_no_leftovers', not bad and m.group(1) == '0' and m.group(2) == WATER and e.get('bodyCount') == a2[2],
          (census, e.get('bodyCount'), a2[2]), unmeasured=bad)
    _walk_log_row(S, K, 'sc_walk_switch')


def _walk_second_order(S):
    """sc_walk_second_order: fuel first, then water, works. Chemfuel poured into its own pit first, then the pond drained
    into a moat: the pond pays, the fuel keeps its stock, and the census holds exactly water and chemfuel with every wet
    cell recorded."""
    import re
    K = _walk_kit(S)
    S.setting('depthEngineLiveForTests', True)
    S.dig(K.pond, 4); S.fill(K.pond, 2.0, WATER)
    S.dig(K.fuel_pit, 4); S.fill(K.fuel_pit, 1.0, FUEL); S.pulse(10)
    f0, p3 = S.dl(K.fuel_pit), K.litres()
    S.dig(K.moat3, 4); S.pulse(40)
    K.pays('WALK_second_order_pond_pays', p3, K.moat3)
    f1 = S.dl(K.fuel_pit)
    bad = None in f0 or None in f1 or not any(f0)
    S.row('WALK_second_order_fuel_holds', not bad and all(abs(x - y) <= 1e-6 for x, y in zip(f0, f1)), (f0, f1),
          unmeasured=bad)
    census2 = S.sc(FLUIDID, 'ProofCensus')
    m2 = re.search(r'unrecorded (\d+) \| fluids \[([^\]]*)\]', census2)
    fl = None if m2 is None else {x.strip() for x in m2.group(2).split(',') if x.strip()}
    S.row('WALK_second_order_no_leftovers', m2 is not None and m2.group(1) == '0' and fl == {WATER, FUEL}, census2,
          unmeasured=m2 is None)
    _walk_log_row(S, K, 'sc_walk_second_order')


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


def _garden(S, nets='WPFCSDY', chunks=GARDEN_W // GARDEN_CHUNK):
    """sc_garden on every net (his look), or the nets a support scene names: the layout, each tool call and each row are
    the same ones whichever nets are staged, so a support reads its rows exactly as sc_garden did."""
    ox, oz = O
    W, P, F, Cn, St = (ox, oz), (ox, oz + 6), (ox, oz + 12), (ox, oz + 18), (ox, oz + 24)
    D, Y = (ox + 16, oz), (ox + 16, oz + 10)
    S.call('jawa/destroy_batch', rects='%d,%d,30,32' % (ox - 4, oz - 6), categories='Building,Plant,Item,Filth')
    S.call('jawa/set_terrain_batch', ops='Soil:%d,%d,30,32' % (ox - 4, oz - 6))
    S.call('jawa/set_roof_batch', ops='None:%d,%d,30,32' % (ox - 4, oz - 6))
    S.call('jawa/weather_set', weather='Clear', lockWeather=True)     # the still needs sun; the reload drops the lock
    if 'C' in nets or 'S' in nets:
        S.setting('converterRateMultiplier', CONV_MULT, typ=MACH)
    if 'D' in nets:
        S.setting('drillUnitsPerCycle', DRILL_PER_CYCLE)
    if 'Y' in nets:
        S.setting('sheetOverflowEnabled', True, typ=SHEET_SET)

    def build(ops, **kw):
        return S.call('jawa/build_batch', ops=';'.join(ops), faction='player', wipeExisting=False, **kw)

    def pipe(at, n):
        return ['RM_UniversalPipe:%d,%d' % (at[0] + i, at[1]) for i in range(2, 2 + n)]

    part = {'W': ['RM_LiquidTank:%d,%d' % W] + pipe(W, 5), 'P': ['RM_LiquidTank:%d,%d' % P] + pipe(P, 4),
            'F': ['RM_LiquidTank:%d,%d' % F] + pipe(F, 4),
            'C': ['RM_LiquidTankTall:%d,%d' % Cn] + pipe(Cn, 5) + ['RM_LiquidTank:%d,%d' % (Cn[0] + 7, Cn[1])],
            'S': ['RM_LiquidTankTall:%d,%d' % St] + pipe(St, 6) + ['RM_LiquidTank:%d,%d' % (St[0] + 8, St[1])]}
    build([op for k in 'WPFCS' if k in nets for op in part[k]])
    mach = {'W': ['RM_LiquidPump:%d,%d' % (W[0] + 3, W[1]), 'RM_SprinklerHead:%d,%d' % (W[0] + 5, W[1]),
                  'PowerConduit:%d,%d' % (W[0] + 3, W[1] - 1), 'PowerConduit:%d,%d' % (W[0] + 3, W[1] - 2),
                  'Battery:%d,%d,0' % (W[0] + 3, W[1] - 4)],
            'P': ['RM_SprinklerHead:%d,%d' % (P[0] + 5, P[1])], 'F': ['RM_PipeFaucet:%d,%d' % (F[0] + 5, F[1])],
            'C': ['RM_DripFilter:%d,%d' % (Cn[0] + 4, Cn[1])], 'S': ['RM_SunPanStill:%d,%d' % (St[0] + 3, St[1])],
            'D': ['RM_LiquidDrill:%d,%d,0' % D, 'PowerConduit:%d,%d' % (D[0] - 1, D[1]), 'Battery:%d,%d,0' % (D[0] - 2, D[1] - 1)]}
    build([op for k in 'WPFCSD' if k in nets for op in mach[k]])
    if 'Y' in nets:
        build(['Wall:%d,%d' % (Y[0] + i, Y[1] + j) for i in range(-1, 6) for j in range(-1, 6) if i in (-1, 5) or j in (-1, 5)],
              stuff='Steel')
    for k, b in (('W', (W[0] + 3, W[1] - 4)), ('D', (D[0] - 2, D[1] - 1))):
        if k not in nets:
            continue
        # jawa/battery_set, not jawa/gss_stage: gss_stage resolves Gimme Some Slack types and is refused (TypeLoad) on a list
        # without it, which left this scene unstaged on 2026-11-20 (owner_review_stage.py carries the same lesson).
        bat = S.call('jawa/list_things', defName='Battery', rect='%d,%d,1,1' % b, limit=2).get('things') or []
        require(bool(bat), 'no Battery at %s to charge' % (b,))
        got = S.call('jawa/battery_set', thing=bat[0].get('id'), mode='setPct', value=1.0)
        require((got.get('storedEnergyPctAfter') or 0) >= 0.99, 'battery at %s not charged: %s' % (b, str(got)[:160]))
    if 'W' in nets:
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

    ids = {k: thing(d, at) for k, d, at, n in (('headW', 'RM_SprinklerHead', (W[0] + 5, W[1]), 'W'),
                                              ('headP', 'RM_SprinklerHead', (P[0] + 5, P[1]), 'P'),
                                              ('pump', 'RM_LiquidPump', (W[0] + 3, W[1]), 'W'),
                                              ('faucet', 'RM_PipeFaucet', (F[0] + 5, F[1]), 'F'),
                                              ('filter', 'RM_DripFilter', (Cn[0] + 4, Cn[1]), 'C'),
                                              ('still', 'RM_SunPanStill', (St[0] + 3, St[1]), 'S'),
                                              ('drill', 'RM_LiquidDrill', D, 'D')) if n in nets}
    missing = sorted(k for k, v in ids.items() if not v)
    ids.setdefault('headW', None); ids.setdefault('headP', None)
    require(not missing, 'not built: %s' % missing)
    d0 = None
    if 'D' in nets:
        drill = S.sc(NSP, 'ProofDrill', '%d,%d;%s;200' % (D[0], D[1], FRESH))
        require(drill.startswith('DRILL'), 'drill yield: %s' % drill)
        outlet = tuple(int(v) for v in drill.split('outlet=')[1].split()[0].split(','))
        S.dig([outlet], 8)
    S.ticks(250)                                   # sprinkler_live.COLD_WAIT: the pump's power switches on first

    fill = {k: tank(at, liq, u) for k, at, liq, u in (('W', W, FRESH, 100000), ('P', P, FRESH, 100000),
                                                      ('F', F, FRESH, 100000), ('C', Cn, TOXIC, 250000),
                                                      ('S', St, SALT, 250000)) if k in nets}
    require(all(v[0] for v in fill.values()), 'a tank would not fill: %s' % fill)
    spill = S.sc(SHEET, 'ProofSheetSpill', '%d,%d;15000;Pump' % (Y[0] + 2, Y[1] + 2)) if 'Y' in nets else None
    drinker = None
    if 'F' in nets:
        drinker = S.pawn('Colonist', (F[0] + 5, F[1] + 1), 'player')
        S.call('jawa/pawn_need', pawn=drinker, action='need', need='RM_Thirst', level=0.05)
    if 'D' in nets:
        d0 = S.sc(NSP, 'ProofDrill', '%d,%d' % D)

    def feed():
        # the drinker stays thirsty only until the faucet's tank has paid its drink: after that a thirsty drinker took a
        # second drink from the filter's fresh output tank (visit 3, 2026-11-21: C2 63985 = 32 x 2000 - 15, one tank drink
        # at tick ~40000), so the filter row read a drink as a lost batch (SITE)
        drank = 'F' in fill and bool(log) and log[-1]['t'].get('F') and log[-1]['t']['F'][0] < fill['F'][0]
        for p in S.call('jawa/list_pawns', faction='player').get('pawns') or []:
            needs = dict((x.get('need'), x.get('level')) for x in
                         (S.B.call('jawa/pawn_need', pawn=p['id'], action='list') or {}).get('needs') or [])
            if needs.get('Food', 1.0) < 0.5:
                S.B.call('jawa/pawn_need', pawn=p['id'], action='need', need='Food', level=1.0)
            # topped up well above ThirstyBelow (0.3, RM_ThirstMath): at < 0.3 a pawn already seeks a drink inside the chunk
            if (p['id'] != drinker or drank) and needs.get('RM_Thirst', 1.0) < 0.9:
                S.B.call('jawa/pawn_need', pawn=p['id'], action='need', need='RM_Thirst', level=1.0)

    log = []                                       # one entry a chunk: tank units, drill read, yard read, head lines
    stop, cells_prior = None, None
    tanks = [(n, at) for n, at in (('W', W), ('P', P), ('F', F), ('C', Cn), ('C2', (Cn[0] + 7, Cn[1])), ('S', St),
                                   ('S2', (St[0] + 8, St[1]))) if n[0] in nets]
    for k in range(chunks):
        feed()
        try:
            S.ticks(GARDEN_CHUNK)
        except Exception as e:                     # noqa: BLE001 - a GovernorStop: the window is broken, rows say so
            stop = repr(e)[:300]
            break
        log.append({'t': {n: tank(at) for n, at in tanks},
                    'drill': S.sc(NSP, 'ProofDrill', '%d,%d' % D) if 'D' in nets else None,
                    'yard': S.sc(SHEET, 'ProofSheetRect', '%d;%d;5;5' % Y) if 'Y' in nets else None,
                    'headW': inspect(ids['headW']), 'headP': inspect(ids['headP'])})
        # the yard's 25 squares, read on every chunk that still holds half the spill: it dries through the window (live
        # 2026-11-20: 14552 dL after one chunk, 3695 after 24), so an end-of-window read would see a film, not the 3 cm
        half = _num(spill, 'accepted') if str(spill).startswith('SPILL') else None
        if half and (_num(log[-1]['yard'], 'dl') or 0) >= half / 2:
            got, err = _yard_cells(S, Y, cells_prior)
            log[-1]['cells'], log[-1]['cellsErr'] = got, err
            cells_prior = got or cells_prior
    S.r['garden_log'] = log
    why = ('the clock stopped: %s; ' % stop) if stop else ''
    _garden_rows(S, fill, log, d0, spill, why, full=stop is None, nets=nets)


def _garden_rows(S, fill, log, d0, spill, why, full, nets='WPFCSDY'):
    import re
    u = lambda e, n: (e['t'][n][0] if e and e['t'].get(n) else None)            # noqa: E731
    tk = lambda e, n: (e['t'][n][1] if e and e['t'].get(n) else None)           # noqa: E731
    last = log[-1] if log else None

    sprayed = False
    if 'W' in nets:
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

    if 'P' in nets:
        # P: the same head with no pump on its net never sprays (and only means something when W's head did)
        p_end = u(last, 'P')
        S.row('GARDEN_no_pump_no_spray', p_end == fill['P'][0] and (last['headP'] or '').startswith('No pressure'),
              why + str({'filled': fill['P'][0], 'end': p_end, 'head': last and last['headP'], 'pumpedHeadSprayed': sprayed}),
              unmeasured=p_end is None or not sprayed or not full)

    if 'F' in nets:
        # F: the faucet's tank is drawn by the thirsty colonist (no other fixture on its net)
        f_end = u(last, 'F')
        S.row('GARDEN_faucet_drinks_from_its_tank', f_end is not None and f_end < fill['F'][0],
              why + str({'filled': fill['F'][0], 'end': f_end}), unmeasured=f_end is None or not full)

    if 'C' in nets:
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

    if 'S' in nets:
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

    if 'D' in nets:
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

    if 'Y' in nets:
        # Y: the walled yard's 3 cm lies level over all 25 squares (no dry island); the latest read still holding half of it.
        # Level means the SURFACE (depth + the kernel's ±1 cm micro-relief, D8/D9), not equal depths: visit 2 (2026-11-19)
        # read maxDl 461 over a mean of 312 on every one of 24 reads, the relief's own signature, and the old depth test
        # failed it (RIMMANDRAKE_PROBE_FLOWWORKS_GARDEN_YARD_MOUND_RELIEF_OR_KERNEL). The read must also see a mound planted
        # after it, or the row is UNMEASURED.
        took = _num(spill, 'accepted') if str(spill).startswith('SPILL') else None
        good = [e['yard'] for e in log if took and (_num(e['yard'], 'dl') or 0) >= took / 2]
        y = good[-1] if good else (log[-1]['yard'] if log else None)
        wet, Y = _num(y, 'wet'), (O[0] + 16, O[1] + 10)            # _garden's yard
        held = [e for e in log if took and (_num(e['yard'], 'dl') or 0) >= took / 2]
        lvs = [(log.index(e), _yard_level(e['cells'])) for e in held if e.get('cells')]
        lvs = [(i, lv) for i, lv in lvs if lv]
        err = next((e.get('cellsErr') for e in held if not e.get('cells')), None) or (None if held else 'no chunk holds half the spill')
        worst = max(lvs, key=lambda t: t[1]['spread']) if lvs else None
        lows = [(i, lv['low']) for i, lv in lvs if lv['low']]
        # the instrument's own foil, after the window: 4 cm more on the corner square, read back before a pulse can level it.
        # It must rise there by most of the foil and nowhere else, or the per-square read cannot see a mound (UNMEASURED).
        base = _yard_cells(S, Y, held[-1]['cells'])[0] if held and held[-1].get('cells') else None
        rise = others = None
        if base:
            S.sc(SHEET, 'ProofSheetSpill', '%d,%d;%d;Pump' % (Y[0], Y[1], YARD_MOUND_DL))
            mound = _yard_cells(S, Y, base)[0]
            if mound:
                d = {(a[0], a[1]): b[2] - a[2] for a, b in zip(base, mound)}
                rise, others = d.pop(Y), max([abs(v) for v in d.values()] or [0])
        sees = rise is not None and rise >= 0.9 * YARD_MOUND_DL and others <= YARD_LEVEL_DL
        whole = bool(lvs) and len(lvs) == len(held)
        S.row('GARDEN_walled_yard_lies_level', bool(good) and wet == 25 and whole and worst[1]['spread'] <= YARD_LEVEL_DL
              and not lows,
              why + str({'worstSurfaceSpread': worst and worst[1]['spread'], 'atChunk': worst and worst[0], 'limit': YARD_LEVEL_DL,
                         'chunksRead': len(lvs), 'chunksHeld': len(held), 'depthSpread': worst and worst[1]['depthSpread'],
                         'free': worst and worst[1]['free'], 'low': lows[:2], 'foil': {'rise': rise, 'others': others},
                         'err': err, 'read': y, 'spill': spill[:40]}),
              unmeasured=not good or not whole or not sees)


SHEET_MATH = 'RimMandrake.FlowWorks.RM_SheetMath'
# RM_SheetMath.Params (read 2026-11-20): ReliefDl = RetentionDl = DlPerCm = 200 dL (1 cm on one square), SheetCapDl = 50 cm.
SHEET_RELIEF_DL, SHEET_RETENTION_DL, SHEET_CAP_DL = 200, 200, 10000
# The surface a read can see after a pulse: Pulse runs Level then Losses (RM_SheetMath.cs Pulse); Level sets every free
# member's surface to L0 or L0 + 1 (1 dL), then Losses takes each wet cell's soak and evaporation as whole dL with its own
# milli-dL remainder carried, so on one terrain class each loss differs by at most 1 dL between squares: 1 + 1 + 1 = 3 dL
# (0.015 cm). Live 2026-11-20 (sc_garden_20261120T221816) read 0-3 over 15 chunks. A foil of 4 cm (800 dL) is twice the
# relief's whole range, so a read that cannot see it cannot see a mound at all.
YARD_LEVEL_DL, YARD_MOUND_DL = 3, 800


def _yard_cells(S, Y, prior=None):
    """[(x, z, dl, relief)] over the 5x5 yard: dl by ProofSheetCell, relief by the mod's own RM_SheetMath.Relief on the
    map's salt (Gen.HashCombineInt(world seed, map.uniqueID), RM_MapComponent_Sheet) and cell index z * W + x. `prior`
    reuses its reliefs. -> (cells, None) or (None, why)."""
    if prior is None:
        w, m = S.call('jawa/world_info_get'), S.call('jawa/map_info')
        seed, uid, W = (w.get('info') or {}).get('seed'), m.get('mapId'), m.get('sizeX')
        if None in (seed, uid, W):
            return None, 'no seed / map id / width: %s %s %s' % (seed, uid, W)
        h = S.sc('Verse.Gen', 'HashCombineInt', '%d|%d' % (seed, uid))
        try:
            salt = int(h) & 0xFFFFFFFF
        except ValueError:
            return None, 'HashCombineInt: %s' % h[:80]
        rel = {}
        for i in range(5):
            for j in range(5):
                x, z = Y[0] + i, Y[1] + j
                r = S.sc(SHEET_MATH, 'Relief', '%d|%d|%d' % (salt, z * W + x, SHEET_RELIEF_DL))
                try:
                    rel[(x, z)] = int(r)
                except ValueError:
                    return None, 'Relief: %s' % r[:80]
    else:
        rel = {(c[0], c[1]): c[3] for c in prior}
    out = []
    for (x, z), r in sorted(rel.items()):
        dl = _num(S.sc(SHEET, 'ProofSheetCell', '%d,%d' % (x, z)), 'dl')
        if dl is None:
            return None, 'ProofSheetCell %d,%d unreadable' % (x, z)
        out.append((x, z, int(dl), r))
    return out, None


def _yard_level(cells):
    """The surface spread over the free members (R < dl < cap, where LevelPuddle sets dl + relief to L0 or L0 + 1), the
    depth spread beside it, and the cells held at or below retention whose surface lies under the level (water that should
    have run to them): {'spread', 'depthSpread', 'free', 'low'}; None when no square is free."""
    free = [c[2] + c[3] for c in cells if SHEET_RETENTION_DL < c[2] < SHEET_CAP_DL]
    if not free:
        return None
    lo = min(free)
    return {'spread': max(free) - lo, 'depthSpread': max(c[2] for c in cells) - min(c[2] for c in cells), 'free': len(free),
            'low': [(c[0], c[1]) for c in cells if c[2] <= SHEET_RETENTION_DL and c[2] + c[3] < lo - 1]}


TUB_LABEL = 'RimMandrake.FlowWorks.RM_Patch_MouseoverDepth'
TUB_POOL = 'RimMandrake.FlowWorks.RM_GeyserPoolProof'
SUBMERGE = 'RimMandrake.FlowWorks.RM_SubmergeDraw'
TUB_MAP = 250     # the calm site's side, the draft's list rect: a geyser whose pit or cold control would leave it is skipped


def _tub_layout(gx, gz):
    """geyser_tub_live.py's measured layout (PASS 4 of 4, visit 2) round a geyser whose 2x2 is gx..gx+1, gz..gz+1: the 6x6
    pit of geyser_pit_scene.pit_rect, its floor square beside the vent (the label and soak square), and the 2x2 cold
    control dug 3 squares east of the pit."""
    return {'rect': (gx - 2, gz - 2, 6, 6), 'floor': (gx - 1, gz - 1),
            'beside': [(gx + 6, gz - 1), (gx + 7, gz - 1), (gx + 6, gz), (gx + 7, gz)]}


def _geyser_tub(S):
    """inv_geyser_tub. RIMMANDRAKE_POINT_FLOWWORKS_GEYSER_CHECK_AT_VISIT_ONE_RUNNER: the draft inspected the geyser's own
    cell and waited for a hot-spring need, which the mod never writes (visit 2 FAIL). These are geyser_tub_live.py's
    reads: the player's terrain line (RM_Patch_MouseoverDepth.ProofPitLabel) on the pool's floor, and the soak hediffs
    RM_HotPoolSoak / RM_HotPoolAfterglow on an ordered RM_SoakInGeyserPool. The dry control is the same pit before its fill."""
    if str(HERE) not in sys.path:     # imported by path (a selftest, scene_empty_game): live_session sits beside this file
        sys.path.append(str(HERE))
    from live_session import hediffs
    gey = S.call('jawa/list_things', defName='SteamGeyser', rect='0,0,%d,%d' % (TUB_MAP, TUB_MAP), limit=50).get('things') or []
    fits = [t for t in gey if isinstance(t, dict) and 2 <= t.get('x', -1) and t['x'] + 7 < TUB_MAP and 2 <= t.get('z', -1)
            and t['z'] + 3 < TUB_MAP]
    require(fits, 'no SteamGeyser with room for its pit on the prepared map: %s' % str(gey)[:160])
    g, L = fits[0]['id'], _tub_layout(fits[0]['x'], fits[0]['z'])
    x0, z0, w, h = L['rect']
    S.dig([(x0 + i, z0 + j) for i in range(w) for j in range(h)], 8)
    S.ticks(70)

    def label(c):
        return S.sc(TUB_LABEL, 'ProofPitLabel', '%d,%d' % c)

    t = label(L['floor'])
    S.row('TUB_dry_pit_not_a_tub', t.startswith('line=Pit') and 'Hot tub' not in t, t)
    # ProofFillRect takes METRES (geyser_pit_scene.py's fill of its G2 pool)
    f = S.sc(SUBMERGE, 'ProofFillRect', '%d,%d,%d,%d,1.00,%s' % (x0, z0, w, h, WATER))
    S.ticks(30)
    t = label(L['floor'])
    S.row('TUB_reads_hot_tub', 'Hot tub' in t and 'Water 1.00 m' in t, '%s (fill: %s)' % (t, f[:80]))
    S.dig(L['beside'], 8, 1.0)
    t = label(L['beside'][0])
    S.row('TUB_beside_stays_cold', t.startswith('line=Pit') and 'water' in t and 'Hot tub' not in t, t)
    p = S.pawn('Colonist', L['floor'], 'player')
    o = S.call('jawa/ordered_job', pawnId=p, jobDef='RM_SoakInGeyserPool', targetAId=g, targetBX=L['floor'][0],
               targetBZ=L['floor'][1], waitTicks=1)
    S.ticks(600)
    mid = hediffs(S.call('jawa/pawn_get', pawn=p))
    pool = S.sc(TUB_POOL, 'Read', g)
    S.ticks(2700)
    after = hediffs(S.call('jawa/pawn_get', pawn=p))
    S.row('TUB_pawn_soaks_bonus', bool(o.get('accepted')) and 'RM_HotPoolSoak' in mid and 'RM_HotPoolAfterglow' in after
          and 'soakers=1' in pool, {'order': str(o)[:120], 'mid': mid, 'after': after, 'pool': pool[:200]},
          unmeasured=not o.get('accepted'))


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
scene_source_draws = _run('scene_source_draws', _source_draws)
scene_source_refills = _run('scene_source_refills', _source_refills)
scene_lake_endless = _run('scene_lake_endless', _src_lake_site)
scene_pawn_height = _run('scene_pawn_height', _pawn_height)
scene_hose_look = _run('scene_hose_look', _hose_look)
scene_trench_cover = _run('scene_trench_cover', _trench_cover)
scene_trench_cover_pawns = _run('scene_trench_cover_pawns', lambda S: _trench_cover(S, raid=False))
scene_ice = _run('scene_ice', _ice)
scene_moat_raid = _run('scene_moat_raid', _moat_raid)
scene_moat_walkers = _run('scene_moat_walkers', _moat_walkers)
scene_toss_flame = _run('scene_toss_flame', _toss_flame)
scene_wetting = _run('scene_wetting', _wetting)
scene_fetch_fallen = _run('scene_fetch_fallen', _fetch_fallen_scene)
scene_islands = _run('scene_islands', _islands)
scene_islands_walker = _run('scene_islands_walker', _islands_walker)
scene_walk_moat_season = _run('scene_walk_moat_season', _walk)
scene_walk_reload = _run('scene_walk_reload', _walk_reload)
scene_walk_switch = _run('scene_walk_switch', _walk_switch)
scene_walk_second_order = _run('scene_walk_second_order', _walk_second_order)
scene_pit_trap_raid = _run('scene_pit_trap_raid', _pit_trap_raid)
scene_garden = _run('scene_garden', _garden)
# sc_garden's two supports (RIMMANDRAKE_SHRINK_FLOWWORKS_SCENES_HUNG_BRIDGE_RAN_27_TIMES; table.md section 1: a game day,
# seven machines in one staging, a fed colony, deciding no bar). The pumped head beside the head with no pump, over one clean
# pulse (the first chunk holds the cold pulse); the faucet drink, one colonist, one chunk.
SUPPORT_PUMP_CHUNKS, SUPPORT_FAUCET_CHUNKS = 3, 1
scene_sprinkler_pump = _run('scene_sprinkler_pump', lambda S: _garden(S, nets='WP', chunks=SUPPORT_PUMP_CHUNKS))
scene_faucet_drink = _run('scene_faucet_drink', lambda S: _garden(S, nets='F', chunks=SUPPORT_FAUCET_CHUNKS))
scene_geyser_tub = _run('scene_geyser_tub', _geyser_tub)
scene_coating_wash = _run('scene_coating_wash', _coating_wash)
STAGE3_SCENES = {f.__name__: f for f in (scene_fill_front, scene_one_surface, scene_source_pays, scene_pawn_height,
                 scene_hose_look, scene_trench_cover, scene_ice, scene_moat_raid, scene_moat_walkers,
                 scene_trench_cover_pawns, scene_islands_walker, scene_toss_flame, scene_wetting,
                 scene_fetch_fallen, scene_islands, scene_walk_moat_season, scene_pit_trap_raid, scene_garden,
                 scene_geyser_tub, scene_coating_wash, scene_walk_reload, scene_walk_switch,
                 scene_walk_second_order, scene_source_draws, scene_source_refills, scene_lake_endless,
                 scene_sprinkler_pump, scene_faucet_drink)}


def _hole_prison_stage(B, snapshot, reload_snapshot, receipt, save_mid=None, load_mid=None):
    """scene_hole_prison in the table's shape, so the certificate's empty-game check examines it: it asserts instead of
    writing rows, so an assertion is one UNMEASURED staging row (as _run does) and a clean end is one PASS row."""
    rows = []
    try:
        scene = globals()['scene_hole_prison']   # looked up at call time: a selftest swaps the scene for a stub
        scene(B, snapshot, reload_snapshot, receipt, save_occupied=save_mid, load_occupied=load_mid)
        rows.append({'id': 'PRISON_capture_holds_without_bed', 'status': 'PASS', 'kind': 'MOD',
                     'detail': 'every require of scene_hole_prison held'})
    except AssertionError as e:
        rows.append({'id': 'scene_hole_prison_staging', 'status': 'UNMEASURED', 'kind': 'HARNESS', 'detail': repr(e)[:400]})
    return {'status': 'PASS' if all(r['status'] == 'PASS' for r in rows) else 'FAIL', 'rows': rows}


_hole_prison_stage.__name__ = 'scene_hole_prison'
STAGE3_SCENES['scene_hole_prison'] = _hole_prison_stage



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
