#!/usr/bin/env python3
"""Real bounded live adapter for TITAN_PASSAGE_PRUNE_WHALES_ON_FOOT.

Existing calm_v3 only. Stage ONLY current tile biome; no generation/roster edits.
PROVE: complete production pool; EXPECT nonempty own-roster land kinds with zero
abstract MaxFlightTime before any generated pawn. LIES: empty/capped/source roster.
PROVE: event-off CanFireNow on a fresh tick, paired with enabled real incident;
EXPECT pending + tremor, DebugArriveNow then one governed tick, new spawned ID,
seaMatch and own-roster membership. LIES: cached LastArrived, direct pawn spawn.
PROVE: finally reload guarded scene-begin; EXPECT exact tile, pawn identity/state,
passage fields, letters, full-map rectangle hash, time/weather/settings/isolation.
Synthetic biome fixture, NOT native Stillsand terrain-generation integration;
NOT natural two-hour timing, completed crossing, flight, or showcase evidence.
All raw bridge responses are journalled without slicing, including governed ticks.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
for p in (ROOT/'src/RimMandrake/Utils', ROOT/'src/RimMandrake/Utils/modcheck'):
    sys.path.insert(0, str(p))
import validation_core as V
import test_site_saves as T
import helpers as H
from game_paths import SAVES, MODS_CONFIG
import passage_pool_live as P

SETTINGS = 'RimMandrake.HugeThings.RM_HugeThingsSettings'
PROOF = 'RimMandrake.FlowWorks.RM_PitPrisonProof'
PASSAGE_MEMBERS = 'kind,start,end,arrivalTick,warnedTick,warningTicks,arrived,HasPending,PendingKind,ArrivalTick,LastArrived'


def need(ok, reason):
    if not ok:
        raise AssertionError(reason)


def credential_safe(value):
    """Keep complete replies except credential values. Startup journal cursors
    can return the bridge token as their latest message; never persist that value.
    Returns sanitized value and explicit redaction count without altering game data.
    """
    if isinstance(value,dict):
        pairs = {k:credential_safe(v) for k,v in value.items()}
        return {k:v[0] for k,v in pairs.items()}, sum(v[1] for v in pairs.values())
    if isinstance(value,list):
        pairs = [credential_safe(v) for v in value]
        return [v[0] for v in pairs], sum(v[1] for v in pairs)
    if isinstance(value,str):
        value,n = re.subn(r'(?i)(bridge token:\s*)(?!\[credential redacted\])\S+', r'\1[credential redacted]',value)
        value,m = re.subn(r'(?i)(authorization:\s*bearer\s*)(?!\[credential redacted\])\S+', r'\1[credential redacted]',value)
        return value,n+m
    return value,0


class Run(V.Bridge):
    def __init__(self, out):
        self.out = out
        self.rec = dict(script=__file__, started=time.time(), calls=[], rows=[],
                        scope=__doc__, status='IN_PROGRESS')
        self.journal = out.with_suffix('.calls.jsonl').open('x', encoding='utf-8')
        super().__init__()
        tools = self.S.list_tools()
        self.rec['tool_inventory'] = tools
        self.rec['jawa_tool_count'] = sum(x['name'].startswith('jawa/') for x in tools)
        need(self.rec['jawa_tool_count'] > 0, 'companion tool census empty')

    def _raw(self, tool, kw):
        r,count = credential_safe(super()._raw(tool, kw))
        self.rec['credential_values_redacted'] = self.rec.get('credential_values_redacted',0)+count
        event = dict(tool=tool, args=kw, raw_response=r, wall=time.time())
        self.journal.write(json.dumps(event, default=str)+'\n')
        self.journal.flush()
        return r

    def call(self, tool, allow=False, **kw):
        r = super().call(tool, **kw)
        self.rec['calls'].append(dict(tool=tool, args=kw, result=r))
        if not allow:
            need(r.get('success') is not False, f'{tool} refused: {r}')
        return r

    def hook(self, method):
        return self.call('jawa/static_call', type=P.HOOKS, method=method, args='')

    def row(self, name, detail):
        self.rec['rows'].append(dict(id=name, status='PASS', detail=detail))
        self.save()
        print(name, 'PASS', flush=True)

    def save(self):
        self.out.write_text(json.dumps(self.rec, indent=2, default=str)+'\n', encoding='utf-8')

    def setting(self, field, value):
        self.call('jawa/mod_settings_field', typeName=SETTINGS, field=field, action='set', value=str(value))
        got = self.call('jawa/mod_settings_field', typeName=SETTINGS, field=field, action='get')['value']
        need(str(got).lower() == str(value).lower(), f'{field} readback disagrees')

    def advance(self, n):
        before = self.call('jawa/site_state')['ticksGame']
        self.ticks(n)
        after = self.call('jawa/site_state')['ticksGame']
        need(after-before == n, f'governed tick delta {after-before} != {n}')

    def pawns(self):
        r = self.call('jawa/list_pawns', limit=10000, includeHealth=True)
        need(r['truncated'] == 0 and r['returned'] == r['totalOnMap'] == len(r['pawns']), 'incomplete full-map pawn census')
        return sorted(r['pawns'], key=lambda p:p['id'])

    def settings(self):
        r = self.call('jawa/mod_settings_field', typeName=SETTINGS, action='list')
        need(r['count'] == len(r['fields']), 'incomplete settings list')
        return {x['name']:x['value'] for x in r['fields']}

    def restore_jobs(self, wanted):
        """Reload can select a different idle wander target. Replay only that
        known simple job through the supported order API, paused, then compare.
        This restores recorded job/target/queue fields, not internal toil/RNG state.
        Any other job difference remains a refusal rather than a generic rewrite.
        """
        got = {p['id']:p for p in self.call('jawa/site_state', rect='0,0,250,250')['pawns']}
        self.rec['jobs_after_reload_before_replay'] = list(got.values())
        for p in wanted:
            q = got[p['id']]
            if p == q:
                continue
            need(p['job'] == q['job'] == 'GotoWander' and not p['queued'] and not q['queued'] and
                 all(p.get(k) == q.get(k) for k in ('id','label','faction','x','z','inRect','targetB','targetC')) and
                 set(p['targetA']) == {'x','z'}, 'nontrivial job difference cannot be replayed safely')
            r = self.call('jawa/ordered_job', pawnId=p['id'], jobDef=p['job'],
                          targetAX=p['targetA']['x'], targetAZ=p['targetA']['z'], waitTicks=0)
            need(r['nowRunningRequested'] and r['ticksElapsed'] == 0, 'paused wander-target restore did not apply')

    def snapshot(self):
        mi = self.call('jawa/map_info')
        need((mi['sizeX'],mi['sizeZ']) == (250,250), 'declared full-map rectangle must cover the whole map')
        ti = self.call('jawa/world_tile_get', tiles=str(mi['tile']))
        need(ti['count'] == ti['requested'] == 1 and ti['truncated'] == 0 and not ti['errors'], 'incomplete tile snapshot')
        pc = self.call('jawa/map_comp_read', comp='MapComponent_TitanPassages', members=PASSAGE_MEMBERS)
        need(not pc['missing'] and set(pc['values']) == set(PASSAGE_MEMBERS.split(',')), 'incomplete passage snapshot')
        rect = self.call('jawa/static_call', type=PROOF, method='Rect', args='0,0,250,250')
        need(rect.get('result') and not str(rect['result']).startswith('FAIL'), 'full-map rectangle unreadable')
        state = self.call('jawa/site_state', rect='0,0,250,250')
        return dict(map={k:mi[k] for k in ('mapId','tile','mapBiome','sizeX','sizeZ')},
                    tile=ti['tiles'][0], pawns=self.pawns(), passage=pc['values'],
                    letters=self.call('jawa/letter_list')['letters'], rect=rect['result'],
                    settings=self.settings(), debug=H.read_settings(T.call_session(self.call)),
                    difficulty=self.call('jawa/difficulty_tune')['before'],
                    ticksGame=state['ticksGame'], weather=state['weather'], conditions=state['conditions'],
                    jobs=sorted(state['pawns'],key=lambda p:p['id']),
                    autoHome=state['autoHome'], storyteller=state['storyteller'],
                    incidentQueue=state['incidentQueue'],
                    wildSpawner=self.call('jawa/wild_spawner_block', action='get')['blocked'])

    def run(self):
        saved = False
        baseline = None
        tx = None
        prior = None
        original_files = None
        snap = 'CODEX_HTPassage_Begin_'+time.strftime('%Y%m%dT%H%M%S')
        try:
            self.rec['artifact_sha256'] = hashlib.sha256((HERE.parent/'Assemblies/RM_HugeThings.dll').read_bytes()).hexdigest()
            self.rec['driver_source_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
            original_paths = [Path(SAVES)/'RM_TestSite_calm_v3.rws'] + [p for p in Path(MODS_CONFIG).parent.glob('*.xml') if 'hugethings' in p.name.lower()]
            original_files = {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in original_paths}
            self.rec['original_disk_hashes'] = original_files
            self.rec['load'] = T.load_site(self.call, 'calm', map_controls=('modal_broker',))
            need(self.rec['load']['verified'], 'existing calm_v3 load failed')
            self.call('jawa/set_game_speed', speed='Paused')
            self.rec['scene_begin'] = T.save_site(self.call, snap, SAVES)
            saved = True
            self.rec['initial_reload'] = T.load_site(self.call, 'calm', name=snap, check=False, map_controls=('modal_broker',))
            need(self.rec['initial_reload']['verified'], 'scene-begin initial reload failed')
            self.call('jawa/set_game_speed', speed='Paused')
            baseline = self.snapshot()
            self.rec['baseline'] = baseline
            prior = baseline['settings']
            need(baseline['passage']['HasPending'] == 'False', 'baseline contains pending passage')
            tx = H.SettingsTransaction(T.call_session(self.call))
            tx.__enter__()
            quiet = H.quiet_world(T.call_session(self.call), tx, wild_spawner=False, log_raids=False)
            self.rec['quiet'] = quiet.evidence
            need(quiet.verified, 'isolation not verified')
            self.setting('giantAnimalsEnabled', True)
            mi = baseline['map']
            self.rec['biome_set'] = self.call('jawa/world_tile_set', tiles=str(mi['tile']), biome=P.BIOME)
            now = self.call('jawa/map_info')
            need(now['mapId'] == mi['mapId'] and now['tile'] == mi['tile'] and now['mapBiome'] == P.BIOME, 'biome fixture/map identity failed')
            tile = self.call('jawa/world_tile_get', tiles=str(mi['tile']))['tiles'][0]
            self.rec['staged_tile'] = tile
            diff = {k:[baseline['tile'].get(k),tile.get(k)] for k in baseline['tile'] if baseline['tile'].get(k) != tile.get(k)}
            self.rec['tile_changes'] = diff
            need(set(diff) == {'biome'}, f'non-biome tile scalar changed: {diff}')
            roster = self.call('jawa/biome_probe', biomes=P.BIOME, animals=True, plants=False, topN=10000)['biomes'][0]
            need(roster['animalsListed'] == roster['wildAnimalCount'] == len(roster['animals']), 'capped resolved roster')
            own = [x['defName'] for x in roster['animals'] if x['commonality'] > 0]
            self.rec['resolved_roster'] = roster
            self.rec['historical_kinds_loaded_probe'] = self.call('jawa/get_defs',
                defs=';'.join('PawnKindDef/'+n for n in ('RM_Reefback','RM_Lanternwhale','RSW_Reefback','RSW_Lanternwhale','RSW_ShadeWhale','RSW_SandoAquaMonster')), fields='race')
            self.setting('titanEventsEnabled', False)
            self.advance(1)
            off = self.hook('PassageCanFire')
            off_pool = P.land_pool(off)
            need(not off_pool['active'] and not off_pool['canFire'], 'event-off gate can fire')
            # dryRun exercises CanFireNow without bypassing the worker gate via TryExecute.
            dry = self.call('jawa/fire_incident', allow=True, incidentDef='RM_TitanPassage', forced=True, dryRun=True)
            need(dry['canFireNow'] is False and dry['fired'] is False, 'event-off incident availability not false')
            need(self.hook('PassageReport')['result'] == 'pending=False kind=none arrivalIn=-1', 'event-off changed passage state')
            self.row('event_off_fresh_tick', dict(pool=off, incident_probe=dry, scope='CanFireNow availability; dryRun does not invoke TryExecute'))
            self.setting('titanEventsEnabled', True)
            self.advance(1)
            pool_response = self.hook('PassageCanFire')
            pool = P.land_pool(pool_response)
            need(pool['canFire'] and pool['active'] and pool['hints'] == 'roster', 'production own-roster branch unavailable')
            kinds = [k['kind'] for k in pool['kinds']]
            need(all(k in own for k in kinds), 'pool outside resolved own roster')
            races = []
            self.rec['kind_defs'] = []
            for k in kinds:
                kd = self.call('jawa/get_def', defName=k, defType='PawnKindDef')
                self.rec['kind_defs'].append(kd)
                races.append(kd['extra']['race'])
            self.rec['race_defs'] = self.call('jawa/get_defs', defs=';'.join('ThingDef/'+x for x in races), fields='race,statBases,modExtensions,comps', deep=True)
            rd = self.rec['race_defs']
            need(not rd['notFound'] and len(rd['defs']) == len(races) and all(x['fields']['race']['canFlyIntoMap'] is False for x in rd['defs']), 'eligible race has flying entry or unreadable flight flag')
            self.rec['race_comp_defs'] = []
            for race in races:
                loaded = self.call('jawa/get_def', defName=race, defType='ThingDef')
                self.rec['race_comp_defs'].append(loaded)
                classes = (loaded['extra']['modExtensions'] or []) + [x['class'] for x in loaded.get('comps') or []] + [x['compClass'] or '' for x in loaded.get('comps') or []]
                need(not any(re.search(r'flight|flying|flyer',x,re.I) for x in classes), 'eligible race has a flight comp/extension; refusing generation')
            stats = self.call('jawa/animal_stats', defs=','.join(races), extraStats='MaxFlightTime')
            self.rec['pre_generation_flight_stats'] = stats
            need(not stats['notFound'] and not stats['refused'] and stats['count'] == len(set(races)), 'flight stat unreadable')
            need(all(x['stats']['MaxFlightTime']['value'] == 0 for x in stats['animals']), 'eligible pool contains a flyer; refusing generation')
            self.rec['pool_response'] = pool_response
            self.rec['own_roster'] = own
            self.row('A2_complete_land_pool', pool)
            pawns_before = self.pawns()
            letters_before = self.call('jawa/letter_list')['letters']
            fired = self.call('jawa/fire_incident', incidentDef='RM_TitanPassage', forced=True)
            self.rec['incident'] = fired
            need(fired['fired'] is True and not fired['blockedByDialog'], 'real incident did not execute')
            pending = self.call('jawa/map_comp_read', comp='MapComponent_TitanPassages', members=PASSAGE_MEMBERS)
            self.rec['scheduled'] = pending
            # map_comp_read ProbeRender deliberately prefixes Defs with their type.
            scheduled_kind = re.fullmatch(r'PawnKindDef:(\w+)', pending['values']['kind'])
            need(pending['values']['HasPending'] == 'True' and scheduled_kind is not None and scheduled_kind[1] in kinds, 'incident did not schedule eligible kind')
            tremors = self.call('jawa/letter_list')['letters']
            new_letters = [x for x in tremors if x not in letters_before]
            need(len(tremors) == len(letters_before)+1 and len(new_letters) == 1, 'incident did not add exactly one letter')
            # Verse.TaggedString serializes as {RawText,Length,StrippedLength}.
            label = new_letters[0]['label']
            text = label if isinstance(label,str) else label.get('RawText')
            need(isinstance(text,str) and 'tremor' in text.lower() and
                 new_letters[0]['arrivalTick'] == pending['ticksGame'], 'tremor letter missing')
            self.rec['debug_arrive_now'] = self.hook('PassageArriveNow')
            self.advance(1)
            response = self.hook('PassageReport')
            arrived = P.arrival(response, pool, own)
            self.rec['arrival_response'] = response
            self.rec['arrived'] = arrived
            after = self.pawns()
            new = [p for p in after if p['id'] not in {p['id'] for p in pawns_before}]
            self.rec['new_pawns'] = new
            need(len(new) == 1 and new[0]['id'] == arrived['pawn'] and new[0]['kindDef'] == arrived['kind'], 'arrival census mismatch')
            need(arrived['kind'] == scheduled_kind[1], 'scheduled/arrived kind differs')
            flight = self.call('jawa/pawn_flight', pawn=arrived['pawn'], action='report', unpause=False)
            self.rec['arrived_flight_read_only'] = flight
            need(flight['count'] == 1 and flight['pawns'][0]['pawn'] == arrived['pawn'] and
                 flight['pawns'][0]['flying'] is False and flight['pawns'][0]['canEverFly'] is False and
                 flight['pawns'][0]['maxFlightTimeStat'] == 0, 'arrived pawn not confirmed grounded/nonflying')
            letters = self.call('jawa/letter_list')['letters']
            need(len(letters) == len(tremors)+1 and any(arrived['pawn'] in (x['lookTargetIds'] or []) for x in letters), 'arrival letter does not target actual pawn')
            self.row('A3_real_forced_arrival', dict(arrived=arrived, trigger='DebugArriveNow + 1 governed tick'))
            self.rec['status'] = 'PASS'
        except Exception as ex:
            self.rec.update(status='FAIL', error=repr(ex), traceback=traceback.format_exc())
        finally:
            errors = []
            # Mod settings are restored before the scene reload; debug/difficulty
            # statics must also be restored AFTER reload, which resets storyteller.
            if prior:
                for f in ('giantAnimalsEnabled','titanEventsEnabled'):
                    try:
                        self.setting(f, prior[f])
                    except Exception as ex:
                        errors.append(repr(ex))
            if saved:
                try:
                    self.rec['restore_load'] = T.load_site(self.call, 'calm', name=snap, check=False, map_controls=('modal_broker',))
                    need(self.rec['restore_load']['verified'], 'scene-begin restoration load failed')
                    self.call('jawa/set_game_speed', speed='Paused')
                except Exception as ex:
                    errors.append(repr(ex))
            if tx:
                try:
                    tx.__exit__(None,None,None)
                except Exception as ex:
                    errors.append(repr(ex))
            if baseline:
                try:
                    self.restore_jobs(baseline['jobs'])
                    debug_now = H.read_settings(T.call_session(self.call))
                    self.rec['debug_after_reload_before_restore'] = debug_now
                    for field,value in baseline['debug'].items():
                        if debug_now.get(field) != value:
                            self.call('jawa/debug_settings', action='set', field=field, value=value)
                    restored = self.snapshot()
                    self.rec['restored'] = restored
                    differences = {k:dict(before=baseline[k], after=restored[k]) for k in baseline if baseline[k] != restored[k]}
                    self.rec['restore_differences'] = differences
                    need(not differences, 'exact restoration differs: '+','.join(differences))
                    self.row('exact_scene_and_settings_restored', dict(compared=list(baseline)))
                except Exception as ex:
                    errors.append(repr(ex))
            if original_files is not None:
                try:
                    after_files = {p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in original_files}
                    self.rec['restored_disk_hashes'] = after_files
                    need(after_files == original_files, 'original calm save or HugeThings disk settings changed')
                except Exception as ex:
                    errors.append(repr(ex))
            self.rec['restore_errors'] = errors
            if errors:
                self.rec['status'] = 'FAIL'
            self.rec['finished'] = time.time()
            self.save()
            self.journal.close()
            print(self.rec['status'], self.rec.get('error',''), errors, flush=True)
        return 0 if self.rec['status'] == 'PASS' else 1


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    need(not args.out.exists(), 'refuse to overwrite existing live attempt')
    sys.exit(Run(args.out).run())
