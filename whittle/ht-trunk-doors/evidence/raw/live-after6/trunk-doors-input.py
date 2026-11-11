"""Natural giant growth seals an occupied workshop; a real inside cutter reopens it.

Run with Windows Python against this clone and an existing registered disposable
site. No clock jumps, debug blocker insertion, direct growth hooks or debug kill.
A root enclosed by its growing contact and existing walls must be unreachable by
vanilla root-touch, while the inside cutter can reach the owned trunk. Preserve
exact door/item/pawn identities, settings and the guarded scene-begin snapshot.
The old/current production planner comparison supplies the matched offline RED.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import time
import uuid
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
for folder in (ROOT/'src/RimMandrake/Utils', ROOT/'src/RimMandrake/Utils/modcheck'):
    sys.path.insert(0, str(folder))
import validation_core as V
import test_site_saves as T
import helpers as H
import clockgate as C
import game_paths as G

MC = 'RimMandrake.HugeThings.MapComponent_HugeFootprints'
SETTINGS = 'RimMandrake.HugeThings.RM_HugeThingsSettings'
PROOF = 'RimMandrake.FlowWorks.RM_PitPrisonProof'
RECT = '90,90,96,30'
# Keep the measured workshop/contact geometry. The registered calm site's
# original colonists stand in the unused gaps, so clear only owned fixture areas.
CLEAR_RECTS = ('94,95,13,18', '121,94,61,13', '170,106,12,9')
MAP_RECT = '0,0,250,250'
RETAINED_GEYSER = dict(id='SteamGeyser10411', **{'def': 'SteamGeyser'}, label='Steam geyser',
                       x=162, z=97, spawned=True, rot=0, stackCount=1, hitPoints=-1, maxHitPoints=-1)
PLANT = 'RM_Nogtyl'
BLOCKER = 'RM_HugeTrunkBlocker'
CUT = 'RM_CutHugePlantFromTrunk'


def require(ok, message):
    if not ok:
        raise AssertionError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def kv(text):
    return dict(re.findall(r'(\w+)=([^\s|]+)', str(text)))


class Run:
    def __init__(self, out):
        self.out = out
        self.bridge = V.Bridge()
        self.rec = dict(script=str(Path(__file__).resolve()), script_sha256=sha(__file__), calls=[],
                        started=time.time(), ok=False, level='L2', fixture_ids=[])
        self.prior = {}
        self.originals = {}
        self.retained = []
        self.retained_cells = set()

    def persist(self):
        self.out.write_text(json.dumps(self.rec, indent=2, default=str, allow_nan=False)+'\n', encoding='utf-8')

    def call(self, tool, allow=False, **args):
        result = self.bridge.call(tool, **args)
        require(not re.search(r'bridge token:|authorization:|bearer ', json.dumps(result), re.I), 'credential-bearing response')
        self.rec['calls'].append(dict(tool=tool, args=args, result=result))
        self.persist()
        if not allow:
            require(result.get('success') is not False, '%s refused: %s' % (tool, result))
        return result

    def sc(self, method, args='', typ=MC):
        result = self.call('jawa/static_call', type=typ, method=method, args=args)
        require(isinstance(result.get('result'), str) and not result['result'].startswith('FAIL'), str(result))
        return result['result']

    def field(self, field, typ=SETTINGS):
        result = self.call('jawa/mod_settings_field', typeName=typ, field=field, action='get')
        require(isinstance(result.get('value'), str), 'unreadable setting '+field)
        return result['value']

    def setting(self, field, value):
        if field not in self.prior:
            self.prior[field] = self.field(field)
        self.call('jawa/mod_settings_field', typeName=SETTINGS, field=field, action='set', value=str(value))
        require((float(self.field(field)) == float(value) if field == 'plantTrunkScale' else self.field(field).lower() == str(value).lower()), 'setting did not stick '+field)

    def ticks(self, count):
        start = self.call('jawa/site_state')['ticksGame']
        executed = C.advance_chunk(T.call_session(self.call), count)
        end = self.call('jawa/site_state')['ticksGame']
        require(executed == count and end-start == count, 'governor tick delta differs')

    def things(self, defname=None, rect=RECT):
        args = dict(rect=rect, limit=5000)
        if defname:
            args['defName'] = defname
        result = self.call('jawa/list_things', **args)
        require(result.get('isCompleteList') is True and result.get('countMatched') == len(result.get('things', [])), 'incomplete thing census')
        return result['things']

    def claimed_cells(self, cells):
        sources = {}
        for x, z in cells:
            state = self.sc('DebugCellState', 'current|%d,%d' % (x,z))
            require(kv(state).get('claimed') == 'True',
                    'HARNESS: required contact not actually claimed at %d,%d' % (x,z))
            sources['%d,%d' % (x,z)] = state
        return sources

    def pawns(self, rect=RECT):
        result = self.call('jawa/list_pawns', rect=rect, limit=1000)
        require(result.get('truncated') == 0 and result.get('returned') == len(result.get('pawns', [])), 'incomplete pawn census')
        return result['pawns']

    @staticmethod
    def near_fixture(pawn, margin=0):
        for rect in CLEAR_RECTS:
            x, z, w, h = map(int, rect.split(','))
            if x-margin <= pawn['x'] < x+w+margin and z-margin <= pawn['z'] < z+h+margin:
                return True
        return False

    def pin_originals(self):
        rows = self.pawns(MAP_RECT)
        require(rows == self.rec['baseline']['map_pawns'], 'SITE: original census changed before isolation')
        self.originals = {p['id']: p for p in rows}
        require(all(p.get('isPlayer') and p.get('intelligence') == 'Humanlike' and p.get('def') == 'Human'
                    and p.get('spawned') and not p.get('dead') and not p.get('downed') for p in rows),
                'SITE: original map pawns are not the supported draftable human colonists')
        require(not any(self.near_fixture(p, margin=1) for p in rows),
                'SITE: original pawn has less than two-cell distance from a fixture rectangle')
        self.rec['originals_pinned'] = []
        for pawn in rows:
            draft = self.call('jawa/set_draft', pawnId=pawn['id'], drafted=True)
            require(draft.get('drafted') is True and type(draft.get('wasDrafted')) is bool,
                    'SITE: original draft state unreadable')
            self.rec['originals_pinned'].append(dict(pawn=pawn, draft=draft))
        self.check_originals('isolated')

    def prepare_clear(self):
        # Census every plot before any drafting, roof, destroy or terrain write.
        plots = {rect: self.things(None, rect) for rect in CLEAR_RECTS}
        names = sorted({t['def'] for things in plots.values() for t in things})
        defs = self.call('jawa/get_defs', defs=';'.join('ThingDef/'+n for n in names),
                         fields='destroyable,size', deep=True, limit=200)
        require(defs['foundCount'] == len(names) and not defs['notFound'] and not defs['malformed'],
                'SITE: incomplete pre-clear destroyability census')
        fields = {d['defName']: d['fields'] for d in defs['defs']}
        require(all(type(fields[n].get('destroyable')) is bool for n in names),
                'SITE: unreadable pre-clear destroyability')
        retained_by_rect = {}
        for rect, things in plots.items():
            retained = [t for t in things if not fields[t['def']]['destroyable']]
            expected = [RETAINED_GEYSER] if rect == CLEAR_RECTS[1] else []
            require(retained == expected, 'SITE: unexpected non-destroyable baseline in '+rect)
            retained_by_rect[rect] = retained
        size = fields['SteamGeyser']['size']
        require(size == dict(x=2, z=2), 'SITE: retained geyser occupied size changed')
        self.retained = [dict(RETAINED_GEYSER)]
        self.retained_cells = {(RETAINED_GEYSER['x']+dx, RETAINED_GEYSER['z']+dz)
                               for dx in range(size['x']) for dz in range(size['z'])}
        self.rec['pre_clear'] = dict(plots=plots, defs=defs, retained_by_rect=retained_by_rect,
                                     retained_cells=sorted(self.retained_cells))
        self.persist()
        return retained_by_rect

    def editable_rects(self, rect):
        # Row runs exclude the retained object's complete occupied rectangle.
        x, z, w, h = map(int, rect.split(','))
        runs = []
        for zz in range(z, z+h):
            start = None
            for xx in range(x, x+w+1):
                editable = xx < x+w and (xx, zz) not in self.retained_cells
                if editable and start is None:
                    start = xx
                elif not editable and start is not None:
                    runs.append('%d,%d,%d,1' % (start, zz, xx-start))
                    start = None
        return runs

    def check_originals(self, phase):
        rows = self.pawns(MAP_RECT)
        by_id = {p['id']: p for p in rows}
        state = self.call('jawa/site_state', rect=RECT)
        checks = []
        for pid, original in self.originals.items():
            pawn = by_id.get(pid)
            require(pawn and pawn.get('spawned') and not pawn.get('dead') and not pawn.get('downed')
                    and (pawn['x'], pawn['z']) == (original['x'], original['z']),
                    'SITE_interference: original pawn moved or became unavailable at '+phase)
            # This instrument reports the actual PRE-WRITE draft state. A false
            # wasDrafted fails even though the call then redrafts for safe cleanup.
            draft = self.call('jawa/set_draft', pawnId=pid, drafted=True)
            require(draft.get('wasDrafted') is True and draft.get('drafted') is True,
                    'SITE_interference: original undrafted at '+phase)
            checks.append(dict(pawn=pawn, draft=draft))
        require(not any(p['id'] not in self.rec['fixture_ids'] and self.near_fixture(p) for p in rows),
                'SITE_interference: non-fixture pawn entered scene at '+phase)
        require(not any(p['id'] in self.originals and (p.get('job') == CUT or p.get('queued')) for p in state['pawns'])
                and not any(p['claimant'] in self.originals for p in state['reservationsInRect']),
                'SITE_interference: original job/reservation at '+phase)
        retained = [self.identity(t['id']) for t in self.retained]
        require(retained == self.retained, 'SITE_interference: retained baseline object changed at '+phase)
        self.rec.setdefault('original_invariants', []).append(dict(phase=phase, pawns=checks, site_state=state, retained=retained))
        self.persist()

    def reach(self, pawn, x, z):
        result = self.call('jawa/order_pawn', allow=True, pawnId=pawn, x=x, z=z, pathEndMode='oncell',
                           waitTicks=0, unpause=False, draft=True)
        self.call('jawa/stop_job', pawnId=pawn, mode='stopall')
        rows = result.get('pawns', [])
        require(len(rows) == 1 and result.get('ticksElapsed') == 0 and rows[0]['start'] == rows[0]['end'], 'invalid paused path read')
        require(type(rows[0].get('canReach')) is bool, 'path answer missing')
        return rows[0]['canReach']

    def spawn_pawn(self, x, z):
        rows = self.call('jawa/spawn_pawn', kindDef='Colonist', x=x, z=z, faction='player', count=1, xenotype='Baseliner')['pawns']
        require(len(rows) == 1, 'wrong spawn cardinality')
        pid = rows[0]['id']
        self.rec['fixture_ids'].append(pid)
        C.declare_fixture(pid)
        self.call('jawa/set_draft', pawnId=pid, drafted=True)
        return pid

    def stage_plant(self, x, z, growth=0.2499):
        result = self.call('jawa/artboard_stage', phase='subjects', pause=True, killHostiles=False,
                           ops='id=plant|kind=plant|x=%d|z=%d|def=%s|growth=%.7f' % (x, z, PLANT, growth))
        rows = result.get('ops', [])
        require(len(rows) == 1 and rows[0].get('ok') and abs(float(rows[0]['readBack']['growth'])-growth) < 0.000001, 'plant initial growth not staged exactly')
        plants = self.things(PLANT, '%d,%d,1,1' % (x, z))
        require(len(plants) == 1, 'plant identity missing')
        return plants[0]['id']

    def identity(self, tid):
        rows = [t for t in self.things() if t['id'] == tid]
        require(len(rows) == 1, 'lost Thing '+tid)
        return rows[0]

    def supplement(self):
        query = self.call('jawa/designate_batch', action='query', limit=10000)
        require(query.get('truncated') is False and query['total'] == query['returned'], 'incomplete designation census')
        rows = [d for d in query['designations'] if 90 <= d['x'] < 186 and 90 <= d['z'] < 120]
        observation = 'CODEX_TrunkDoors_Observe_'+uuid.uuid4().hex[:12]
        saved = T.save_site(self.call, observation, G.SAVES)
        self.rec.setdefault('supplement_saves', []).append(saved)
        path = Path(G.SAVES)/(observation+'.rws')
        growth = []
        for thing in ET.parse(path).getroot().iter('thing'):
            if thing.find('growth') is None:
                continue
            xyz = list(map(int, re.findall(r'-?\d+', thing.findtext('pos', ''))))
            if len(xyz) == 3 and 90 <= xyz[0] < 186 and 90 <= xyz[2] < 120:
                growth.append(dict(id=thing.findtext('id'), pos=thing.findtext('pos'),
                                   growth=thing.findtext('growth'), age=thing.findtext('age')))
        return dict(designations=sorted(rows, key=lambda d: json.dumps(d, sort_keys=True)),
                    plant_growth=sorted(growth, key=lambda d: d['id']))


    def scenario(self, tx):
        retained_by_rect = self.prepare_clear()
        self.pin_originals()
        for rect in CLEAR_RECTS:
            require(not self.pawns(rect), 'SITE: fixture rectangle contains pawns; refuse clearing')
            runs = self.editable_rects(rect)
            self.call('jawa/set_roof_batch', ops=';'.join('None:'+run for run in runs))
            cleared = self.call('jawa/destroy_batch', categories='All', rects=rect)
            x, z, w, h = map(int, rect.split(','))
            skipped = sum(x <= xx < x+w and z <= zz < z+h for xx, zz in self.retained_cells)
            require(cleared['pawnsSkipped'] == 0 and cleared['undestroyableSkipped'] == skipped,
                    'SITE: unexpected protected objects in fixture clear')
            require(self.things(None, rect) == retained_by_rect[rect], 'SITE: bounded clear changed retained set or left objects')
            self.call('jawa/set_terrain_batch', ops=';'.join('Soil:'+run for run in runs))
        self.check_originals('cleared')
        for field, value in dict(giantPlantsEnabled=True, plantTrunkEnabled=True, plantTrunkScale=1, plantItemPushEnabled=False).items():
            self.setting(field, value)
        self.sc('RefreshAllMaps')
        # A real workshop with one southern door. The root outside is surrounded
        # on six adjacent cells by existing walls; its only open touch
        # cell is the doorway approach, which is genuine Nogtyl contact after growth.
        walls = {(x, z) for x in range(95, 106) for z in (102, 111)} | {(x, z) for x in (95, 105) for z in range(103, 111)}
        walls.remove((100, 102))
        walls |= {(99, 99), (100, 99), (101, 99), (99, 100), (101, 100), (101, 101)}
        self.call('jawa/build_batch', ops=';'.join('Wall:%d,%d' % p for p in sorted(walls)), stuff='WoodLog', faction='player')
        self.call('jawa/build_batch', ops='Door:100,102;TableStonecutter:98,108', stuff='WoodLog', faction='player')
        door = self.things('Door', '100,102,1,1')
        bench = self.things('TableStonecutter', '96,106,5,5')
        require(len(door) == len(bench) == 1, 'workshop door/bench not built')
        self.rec['door_before'], self.rec['bench_before'] = door[0], bench[0]
        self.rec['walls_before'] = self.things('Wall')
        cutter = None
        self.rec['cutter_candidates'] = []
        for attempt in range(6):
            pid = self.spawn_pawn(100+attempt % 2, 107+attempt // 2)
            priority = self.call('jawa/set_work_priority', allow=True, pawnId=pid, workType='PlantCutting', priority=1)
            self.rec['cutter_candidates'].append(dict(pawn=pid, priority=priority))
            if priority.get('success') is True and int(priority.get('readBack', 0)) > 0:
                cutter = pid
                break
        require(cutter is not None, 'SITE: bounded Baseliner candidates have no capable PlantCutting worker')
        self.rec['cutter'] = cutter
        self.rec['failure_stage'] = 'HARNESS_baseline_geometry'
        require(self.reach(cutter, 100, 97), 'HARNESS: workshop already inaccessible')
        # These are the two open root-touch cells; both are measured Nogtyl
        # contact after the threshold. Closing them must seal this exact room.
        self.rec['geometry_obstruction_cells'] = [[99, 101], [100, 101]]
        self.call('jawa/build_batch', ops='Wall:99,101;Wall:100,101', stuff='WoodLog', faction='player')
        obstruction = self.things('Wall', '99,101,2,1')
        self.rec['failure_stage'] = 'HARNESS_planted_obstruction'
        require(len(obstruction) == 2 and not self.reach(cutter, 100, 97), 'HARNESS: planted walls do not seal chokepoint')
        removed = self.call('jawa/destroy_batch', categories='Building', rects='99,101,2,1')
        require(removed['destroyed'] == 2 and removed['perCategory'] == {'Building': 2}
                and removed['undestroyableSkipped'] == 0, 'HARNESS: control-wall removal differs')
        require(not self.things(None, '99,101,2,1') and self.reach(cutter, 100, 97), 'HARNESS: removing control walls did not restore route')
        self.rec['geometry_control'] = dict(blocked=obstruction, restored_access=True)
        self.rec['failure_stage'] = 'HARNESS_natural_growth'
        plant = self.stage_plant(100, 100)
        self.rec['plant_id'] = plant
        young = self.sc('DebugPlantState', 'current|100,100')
        require(kv(young).get('oldEnough') == 'False' and kv(young).get('desired') == '0' and kv(young).get('blockingSupported') == 'True' and kv(young).get('blocking') == 'True', 'HARNESS: not a supported enabled young unblocked plant')
        require(not self.things(BLOCKER, '96,96,9,6') and self.reach(cutter, 100, 97), 'young plant already seals access')
        self.rec['young_state'] = young
        samples = []
        for _ in range(6):
            self.ticks(2000)
            state = self.sc('DebugPlantState', 'current|100,100')
            samples.append(dict(state=state, things=self.things(BLOCKER, '96,96,9,6')))
            if kv(state).get('oldEnough') == 'True' and int(kv(state).get('claimed', 0)) > 0:
                break
        self.rec['growth_samples'] = samples
        self.check_originals('grown')
        require(samples and kv(samples[-1]['state']).get('oldEnough') == 'True' and int(kv(samples[-1]['state']).get('desired', 0)) > 0 and int(kv(samples[-1]['state']).get('claimed', 0)) > 0, 'SITE: plant did not naturally grow claimed contacts')
        require(float(kv(samples[-1]['state'])['growth']) > 0.2499, 'no measured natural growth')
        self.ticks(500)
        blockers = self.things(BLOCKER, '100,101,1,1')
        sealed = not self.reach(cutter, 100, 97)
        self.rec['sealed'] = dict(blockers=blockers, access=not sealed, state=self.sc('DebugPlantState', 'current|100,100'))
        self.rec['doorway_claims'] = self.claimed_cells([(99, 101), (100, 101)])
        self.check_originals('sealed')
        self.rec['failure_stage'] = 'MOD_seal'
        require(sealed and len(blockers) == 1, 'MOD: growth did not seal workshop doorway (old access-preserving behavior)')
        require(len(self.things(BLOCKER, '99,101,1,1')) == 1, 'MOD: second open root-touch cell did not fill')
        require(self.identity(door[0]['id']) == door[0], 'growth changed door identity/HP')
        # Standard root work is explicitly unable to reach it. The replacement
        # giver must permit touching this owned blocker, not silently leave a gap.
        absent = self.call('jawa/workgiver_probe', pawn=cutter, thing=blockers[0]['id'], workGiver=CUT)
        require(absent['gates']['canReach'] is True and absent['gates']['workActive'] is True and absent.get('job') is None,
                'missing-designation negative has another false scan gate')
        self.rec['no_designation_probe'] = absent
        self.call('jawa/designate_batch', action='add', designation='CutPlant', rect='100,100,1,1')
        root_probe = self.call('jawa/workgiver_probe', pawn=cutter, thing=plant, workGiver='PlantsCut')
        require(root_probe['gates']['canReachTouchDeadly'] is False, 'root was deliberately left reachable')
        probe = self.call('jawa/workgiver_probe', pawn=cutter, thing=blockers[0]['id'], workGiver=CUT)
        self.rec['cut_probes'] = dict(root=root_probe, trunk=probe)
        require(probe['gates']['canReach'] is True and probe['gates']['canReserve'] is True and probe.get('job', {}).get('def') == CUT,
                'trunk cutting giver did not produce a reachable/reservable real job')
        self.rec['failure_stage'] = 'MOD_natural_cut_pickup'
        prepared = self.sc('PrepareCutter', cutter, 'RimMandrake.HugeThings.TrunkDoorValidationHooks')
        self.rec['cutter_prepared'] = prepared
        second = None
        self.rec['second_candidates'] = []
        for attempt in range(6):
            pid = self.spawn_pawn(101+attempt % 2, 107+attempt // 2)
            priority = self.call('jawa/set_work_priority', allow=True, pawnId=pid, workType='PlantCutting', priority=1)
            self.rec['second_candidates'].append(dict(pawn=pid, priority=priority))
            if priority.get('success') is True and int(priority.get('readBack', 0)) > 0:
                second = pid
                break
        require(second is not None, 'HARNESS: no capable second reservation worker')
        self.sc('PrepareCutter', second, 'RimMandrake.HugeThings.TrunkDoorValidationHooks')
        self.call('jawa/set_draft', pawnId=second, drafted=False)
        second_positive = self.call('jawa/workgiver_probe', pawn=second, thing=blockers[0]['id'], workGiver=CUT)
        require(second_positive['gates']['canReach'] is True and second_positive['gates']['workActive'] is True and
                second_positive.get('job', {}).get('def') == CUT, 'second cutter has no matched unreserved positive')
        self.rec['second_unreserved_positive'] = second_positive
        self.call('jawa/set_draft', pawnId=second, drafted=True)
        # No OrderCut or ordered_job: only a cut designation and normal work AI.
        self.call('jawa/set_draft', pawnId=cutter, drafted=False)
        self.call('jawa/stop_job', pawnId=cutter, mode='stopall')
        self.rec['pickup_samples'] = []
        for _ in range(25):
            self.ticks(20)
            state = self.sc('CutState', cutter, 'RimMandrake.HugeThings.TrunkDoorValidationHooks')
            self.rec['pickup_samples'].append(state)
            if kv(state).get('current') == CUT:
                break
        require(kv(state).get('current') == CUT and kv(state).get('forced') == 'False' and kv(state).get('plant') == plant
                and kv(state).get('contact') == blockers[0]['id'], 'unforced natural worker pickup did not start correct trunk job')
        self.rec['cut_order'] = state
        self.check_originals('natural_pickup')
        # A second capable, undrafted cutter can reach the trunk but the plant is
        # reserved. Probe both the scan target and the actual reservation target.
        self.call('jawa/set_draft', pawnId=second, drafted=False)
        reservation = self.call('jawa/workgiver_probe', pawn=second, thing=blockers[0]['id'], workGiver=CUT)
        root_reservation = self.call('jawa/workgiver_probe', pawn=second, thing=plant, workGiver='PlantsCut')
        require(reservation['gates']['canReach'] is True and reservation['gates']['workActive'] is True and
                root_reservation['gates']['canReserve'] is False and reservation.get('job') is None,
                'matched reservation negative has another false gate or bypassed root reservation')
        self.rec['reservation_control'] = dict(trunk=reservation, root=root_reservation)
        self.call('jawa/set_draft', pawnId=second, drafted=True)
        self.rec['cut_work_samples'] = []
        for _ in range(20):
            self.ticks(20)
            state = self.sc('CutState', cutter, 'RimMandrake.HugeThings.TrunkDoorValidationHooks')
            self.rec['cut_work_samples'].append(state)
            require(kv(state).get('current') == CUT, 'cutting job exited before measured work')
            if float(kv(state)['work']) > 0:
                break
        require(float(kv(state)['work']) > 0 and any(t['id'] == plant for t in self.things(PLANT)), 'no real in-progress work before cutting save')
        work_before_save = state
        occupied = 'CODEX_TrunkDoors_Cutting_'+uuid.uuid4().hex[:12]
        self.rec['cut_save'] = T.save_site(self.call, occupied, G.SAVES)
        self.rec['cut_reload'] = T.load_site(self.call, 'calm', name=occupied, check=False, map_controls=('modal_broker',))
        require(self.rec['cut_reload']['verified'], 'cutting snapshot did not reload')
        H.quiet_world(T.call_session(self.call), tx, wild_spawner=False, log_raids=False)
        self.check_originals('occupied_reload')
        self.rec['cut_job_after_reload'] = self.sc('CutState', cutter, 'RimMandrake.HugeThings.TrunkDoorValidationHooks')
        restored_work = kv(self.rec['cut_job_after_reload'])
        require(restored_work.get('current') == CUT and restored_work.get('plant') == plant and
                restored_work.get('contact') == blockers[0]['id'] and restored_work.get('work') == kv(work_before_save).get('work'),
                'cutting work/targets changed across occupied reload')
        for _ in range(80):
            self.ticks(100)
            if not any(t['id'] == plant for t in self.things(PLANT)):
                break
        require(not any(t['id'] == plant for t in self.things(PLANT)), 'actual cutting job never removed enclosed plant')
        self.check_originals('cut_completed')
        self.call('jawa/set_draft', pawnId=cutter, drafted=True)
        self.ticks(500)
        require(not self.things(BLOCKER, '96,96,9,6'), 'plant blockers survived cutting/cleanup')
        require(self.reach(cutter, 100, 97), 'access not restored after real cutting')
        require(self.identity(door[0]['id']) == door[0] and self.identity(bench[0]['id']) == bench[0], 'cutting altered door/workshop')
        require(self.things('Wall') == self.rec['walls_before'], 'growth/cutting changed existing walls')
        self.rec['cut_recovered'] = True
        self.rec['failure_stage'] = 'MOD_placement_controls'
        self.controls()

    def controls(self):
        # Each plant has positive free contact cells as well as the obstructed
        # one: an absent/disabled footprint cannot satisfy placement protection.
        guard = self.spawn_pawn(125, 101)
        self.call('jawa/spawn_batch', ops='Steel:140,101,17')
        item = self.things('Steel', '140,101,1,1')
        require(len(item) == 1, 'item control absent')
        self.call('jawa/build_batch', ops='Door:155,101', stuff='WoodLog', faction='player')
        door = self.things('Door', '155,101,1,1')
        require(len(door) == 1, 'protected building control absent')
        self.call('jawa/build_batch', ops='SteamGeyser:165,101', faction='none', wipeExisting=False)
        geyser = self.things('SteamGeyser', '165,101,2,2')
        require(len(geyser) == 1 and geyser[0]['id'] != RETAINED_GEYSER['id'], 'independent indestructible fixture absent')
        self.rec['indestructible_def'] = self.call('jawa/get_defs', defs='ThingDef/SteamGeyser', fields='destroyable')
        require(self.rec['indestructible_def']['defs'][0]['fields']['destroyable'] is False, 'indestructible definition differs')
        for x in (125, 140, 155, 165, 175):
            self.stage_plant(x, 100)
        self.stage_plant(175, 110)
        self.rec['control_growth_samples'] = []
        for _ in range(6):
            self.ticks(2000)
            states = [self.sc('DebugPlantState', 'current|%d,%d' % xy) for xy in
                      ((125,100),(140,100),(155,100),(165,100),(175,100),(175,110))]
            self.rec['control_growth_samples'].append(states)
            if all(kv(state).get('oldEnough') == 'True' and int(kv(state).get('claimed', 0)) > 0 for state in states):
                break
        require(all(kv(state).get('oldEnough') == 'True' and int(kv(state).get('claimed', 0)) > 0 for state in states),
                'HARNESS: controls did not naturally grow claimed contacts')
        self.check_originals('controls_grown')
        self.ticks(500)
        self.rec['guarded_cell_claims'] = self.claimed_cells([(125, 101), (140, 101), (155, 101), (165, 101)])
        self.rec['baseline_geyser_claims'] = {'%d,%d' % cell: self.sc('DebugCellState', 'current|%d,%d' % cell)
                                            for cell in sorted(self.retained_cells)}
        geyser_cells = self.retained_cells | {(x, z) for x in (165, 166) for z in (101, 102)}
        for x in (125, 140, 155, 165):
            require(not self.things(BLOCKER, '%d,101,1,1' % x), 'placement control was overwritten')
            free = self.things(BLOCKER, '%d,98,7,6' % (x-3))
            require(free and all((t['x'], t['z']) not in geyser_cells for t in free),
                    'obstruction control lacks an independent free-space positive or overlaps a geyser')
        require(self.identity(item[0]['id']) == item[0], 'item moved/wiped with item push disabled')
        require(self.identity(door[0]['id']) == door[0], 'existing building wiped/changed')
        require(self.identity(geyser[0]['id']) == geyser[0], 'indestructible fixture changed')
        pawn_rows = [p for p in self.pawns() if p['id'] == guard]
        require(len(pawn_rows) == 1 and pawn_rows[0]['x'] == 125 and pawn_rows[0]['z'] == 101 and not pawn_rows[0].get('dead') and not pawn_rows[0].get('downed'), 'pawn placement control moved/hurt')
        self.setting('plantItemPushEnabled', True)
        self.ticks(500)
        moved = self.identity(item[0]['id'])
        require(moved['stackCount'] == item[0]['stackCount'] and (moved['x'], moved['z']) != (140, 101), 'item push lost its stack or did not move')
        require(kv(self.sc('DebugCellState', 'current|%d,%d' % (moved['x'], moved['z']))).get('claimed') == 'False', 'item pushed into another footprint')
        require(121 <= moved['x'] < 182 and 94 <= moved['z'] < 107, 'SITE: pushed item left cleared fixture area')
        require((moved['x'], moved['z']) not in self.retained_cells, 'item pushed onto retained baseline object')
        require(self.things(BLOCKER, '140,101,1,1'), 'cleared item cell never realized')
        move = self.call('jawa/order_pawn', allow=True, pawnId=guard, x=125, z=105, waitTicks=0, unpause=False, draft=True)
        require(len(move.get('pawns', [])) == 1 and move['ticksElapsed'] == 0
                and move['pawns'][0].get('orderAccepted') is True and move['pawns'][0].get('canReach') is True,
                'HARNESS: guard move was not accepted/reachable')
        self.ticks(100)
        guard_after = [p for p in self.pawns() if p['id'] == guard]
        require(len(guard_after) == 1 and (guard_after[0]['x'], guard_after[0]['z']) == (125, 105),
                'SITE: guard did not actually arrive after governed movement')
        self.ticks(500)
        require(self.things(BLOCKER, '125,101,1,1'), 'vacated pawn contact never retried')
        self.check_originals('controls_item_pawn')
        clear_plant = self.things(PLANT, '175,110,1,1')
        require(len(clear_plant) == 1 and self.things(BLOCKER, '175,111,1,1'), 'ground ClearArea fixture absent')
        clear_id = clear_plant[0]['id']
        self.rec['ground_clear_negative'] = self.sc('ClearFixtureContact', clear_id+'|175,111|NaturalRockOnly',
                                                   'RimMandrake.HugeThings.TrunkDoorValidationHooks')
        require(self.things(PLANT, '175,110,1,1') and self.things(BLOCKER, '175,111,1,1'), 'NaturalRockOnly cleared giant')
        self.rec['ground_clear_positive'] = self.sc('ClearFixtureContact', clear_id+'|175,111|BlockingBuildingsOnly',
                                                   'RimMandrake.HugeThings.TrunkDoorValidationHooks')
        self.ticks(500)
        require(not self.things(PLANT, '175,110,1,1') and not self.things(BLOCKER, '172,107,7,7'),
                'ground ClearArea left owner or owned blockers')
        self.check_originals('controls_ground_clear')
        free_before = self.things(BLOCKER, '172,98,7,6')
        require(free_before, 'free-space positive has no blockers')
        self.setting('plantTrunkEnabled', False)
        self.sc('RefreshAllMaps')
        self.ticks(500)
        require(not self.things(BLOCKER), 'disabled trunk feature left blockers')
        self.setting('plantTrunkEnabled', True)
        self.sc('RefreshAllMaps')
        self.ticks(500)
        require(self.things(BLOCKER, '172,98,7,6'), 'reenabled free-space feature did not resume')
        self.check_originals('controls_reenabled')
        self.rec['controls'] = dict(pawn=guard, item=item[0], building=door[0], indestructible=geyser[0], free_before=free_before,
                                    item_after_push=moved, vacated_pawn_retried=True, disabled=True, reenabled=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    r = Run(args.out)
    snapshot = 'CODEX_TrunkDoors_Begin_'+uuid.uuid4().hex[:12]
    saved = False
    baseline = baseline_pawns = None
    tx = None
    try:
        dll = HERE.parent/'Assemblies/RM_HugeThings.dll'
        r.rec['assembly_sha256'] = sha(dll)
        r.rec['running'] = r.call('jawa/running_mods', assembly='RM_HugeThings', details=True)
        ids = [x.lower() for x in r.rec['running'].get('packageIds', [])]
        require(len(ids) == len(set(ids)) == 17 and all(x in ids for x in
                ('ludeon.rimworld', 'ludeon.rimworld.royalty', 'ludeon.rimworld.ideology', 'ludeon.rimworld.biotech',
                 'ludeon.rimworld.anomaly', 'ludeon.rimworld.odyssey', 'mandrake.rm.biomes',
                 'mandrake.rm.hugethings', 'mandrake.rm.hugethingstestraces', 'mandrake.rm.flowworks', 'mandrake.rm.patches',
                 'oskarpotocki.vanillafactionsexpanded.core')),
                'wrong loaded all-five-DLC tier')
        matches = r.rec['running'].get('assembly', {}).get('matches', [])
        require(len(matches) == 1 and matches[0].get('sha256') == sha(dll), 'loaded DLL differs from this clone')
        name = T.read_registry().get('calm', {}).get('save') or T.SITES['calm']['save']
        require(name.startswith('RM_TestSite_') and (Path(G.SAVES)/(name+'.rws')).is_file(), 'existing registered site missing')
        r.rec['site_load'] = T.load_site(r.call, 'calm', name=name, map_controls=('modal_broker',))
        require(r.rec['site_load']['verified'], 'SITE: registered site did not load')
        r.rec['snapshot'] = T.save_site(r.call, snapshot, G.SAVES)
        saved = True
        r.rec['baseline_load'] = T.load_site(r.call, 'calm', name=snapshot, check=False, map_controls=('modal_broker',))
        require(r.rec['baseline_load']['verified'], 'scene-begin reload failed')
        baseline = r.sc('Rect', RECT, PROOF)
        baseline_pawns = r.pawns()
        r.rec['baseline'] = dict(rectangle=baseline, pawns=baseline_pawns, map_pawns=r.pawns(MAP_RECT), supplement=r.supplement())
        tx = H.SettingsTransaction(T.call_session(r.call)); tx.__enter__()
        quiet = H.quiet_world(T.call_session(r.call), tx, wild_spawner=False, log_raids=False)
        require(quiet.verified, 'quiet controls unreadable')
        r.rec['quiet'] = quiet.evidence
        r.scenario(tx)
        r.rec['ok'] = True
    except Exception as exc:
        r.rec['error'] = repr(exc)
    finally:
        errors = []
        for field, value in r.prior.items():
            try:
                r.setting(field, value)
                require(r.field(field) == value, 'exact setting restoration mismatch '+field)
            except Exception as exc:
                errors.append(repr(exc))
        if r.prior:
            try:
                r.sc('RefreshAllMaps')
            except Exception as exc:
                errors.append(repr(exc))
        if tx:
            try:
                tx.__exit__(None, None, None)
            except Exception as exc:
                errors.append(repr(exc))
        if saved:
            try:
                r.rec['restore_load'] = T.load_site(r.call, 'calm', name=snapshot, check=False, map_controls=('modal_broker',))
                require(r.rec['restore_load']['verified'], 'scene-begin restoration load failed')
                restored = r.sc('Rect', RECT, PROOF)
                restored_pawns = r.pawns()
                restored_extra = r.supplement()
                r.rec['restored'] = dict(rectangle=restored, pawns=restored_pawns, supplement=restored_extra)
                require(restored == baseline and restored_pawns == baseline_pawns
                        and restored_extra == r.rec['baseline']['supplement'], 'restored rectangle/fixtures differ from exact baseline')
                r.rec['restored']['map_pawns'] = r.pawns(MAP_RECT)
                require(r.rec['restored']['map_pawns'] == r.rec['baseline']['map_pawns'],
                        'restored map-wide pawn census differs from exact baseline')
                r.rec['restored']['retained'] = [r.identity(t['id']) for t in r.retained]
                require(r.rec['restored']['retained'] == r.retained, 'retained baseline object differs after snapshot reload')
                r.rec['restored_original_drafts'] = []
                for original in r.rec.get('originals_pinned', []):
                    expected = original['draft']['wasDrafted']
                    draft = r.call('jawa/set_draft', pawnId=original['pawn']['id'], drafted=expected)
                    r.rec['restored_original_drafts'].append(draft)
                    require(draft.get('wasDrafted') is expected and draft.get('drafted') is expected,
                            'original draft state differs before restoration comparison')
                for field, value in r.prior.items():
                    require(r.field(field) == value, 'post-load setting mismatch '+field)
            except Exception as exc:
                errors.append(repr(exc))
        for pid in r.rec['fixture_ids']:
            C.withdraw_fixture(pid)
        r.rec['restoration'] = dict(ok=saved and not errors, errors=errors, settings=dict(r.prior))
        r.rec['ok'] = r.rec['ok'] and r.rec['restoration']['ok']
        r.rec['finished'] = time.time()
        r.persist()
        print('PASS' if r.rec['ok'] else 'FAIL', r.rec.get('error', ''), errors, flush=True)
    return 0 if r.rec['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
