"""Throwaway (Maturation advance row 2, Pyrelands): build version/test_table.json + .md.
The bar -> test mapping is hand judgment written here; runs_today is MEASURED by running every offline test and by
checking every live scene's entry function exists in validation.py. Columns match ExplosiveKnockback's table."""
import json, re, subprocess, time, datetime, sys
P = 'design/concepts/Pyrelands/'; V = P + 'version/'; SRC = 'src/RimMandrake/Pyrelands/'; VAL = SRC + 'validation.py'
NOW = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
tree = json.load(open(P + 'tree.json')); rec = json.load(open(P + 'record.json')); scn = json.load(open(P + 'scenes.json'))
leaves = {l['id']: l for l in tree['leaves']}; inv = {i['id']: i for i in rec['inventory']}
valdefs = set(re.findall(r'^def (\w+)\(', open(VAL).read(), re.M))
K = SRC + 'Source/Kernel/'
T = {}
def off(tid, f, observes, reads, cmd=None, new=False, item=None, mod_rows=None):
    import os  # Stage 3: a specified test counts as built once its file exists; its item stays named, filed
    if item: item = item.replace(' (to file at Stage 3)', '')
    if new and os.path.exists(f): new = False
    T[tid] = dict(id=tid, kind='offline', stage='4-5', file=f, observes=observes, reads=reads,
                  command=cmd or ('python3 ' + f), **({'new': True} if new else {}), **({'item': item} if item else {}), **({'mod_rows': mod_rows} if mod_rows else {}))
off('T_FUZZ', 'src/RimMandrake/Utils/selftest_pyrelands_fuzz.py', 'seeded fuzz of the production kernels: burn-line component and fire-front clock, furnace thermal charge and bed-ignition clock, biome score, ash fall and fire-ecology gates, ash-on-sand rates, AshFertility (dry, watered, burn bonus), tuning relationships', [K + 'RM_BurnKernel.cs', K + 'RM_FireEcoKernel.cs', K + 'RM_FurnaceKernel.cs', K + 'RM_FireHawkKernel.cs', SRC + 'Source/PyrelandsTuning.cs', SRC + 'Source/SelfTest/Fuzz/PyrelandsFuzz.cs'])
off('T_LINT', 'src/RimMandrake/Utils/selftest_pyrelands_lint.py', 'lint_pyrelands_defs.py clean on the real mod and 30 planted defects caught: XML against C#, tuning order, deep ash stays the ground (pyre_ground_deep_ash), the BiomeDef resolves and can win a tile, plant density equals the enforcer, every wildPlants row is on the allowlist, kernels in both csprojs', ['src/RimMandrake/Utils/lint_pyrelands_defs.py', SRC + 'Defs/', SRC + 'Source/'])
off('T_ALLOWLIST', 'src/RimMandrake/Utils/selftest_pyrelands_allowlist_postfix.py', 'the real wild-plant allowlist Postfix compiled against stubs over every gate, setting, biome, cave and candidate combination; 15 mutants red', [SRC + 'Source/WildPlantAllowlist.cs', K + 'RM_FireEcoKernel.cs'])
off('T_BURN_COST', 'src/RimMandrake/Utils/selftest_pyrelands_burn_cost.py', 'the two big-burn hot paths: the fire-tick postfix allocates no closure (scorch-fruit roll scan), the burrow scan is throttled and disc-bounded', [SRC + 'Source/FireEcologyHook.cs', SRC + 'Source/RM_JobGiver_BurrowOnFire.cs'])
off('T_TRACKS', 'src/RimMandrake/Utils/selftest_pyrelands_track_contrast.py', 'footprints in the ash cover are visible against it and the hover says ash', [SRC + 'Defs/', SRC + 'Textures/'])
off('T_FURNACE_WARMTH', 'src/RimMandrake/Utils/selftest_furnace_warmth.py', 'C# selftest of the furnace-beast warmth maths (felt-temperature aura, strength, falloff)', [SRC + 'Source/FurnaceWarmthMath.cs', SRC + 'Source/SelfTest/Program.cs'])
off('T_SITE', SRC + 'selftest_pyrelands_site.py', 'the live site preparation refuses each dirty case; manifests and defaults cannot drift from validation.py and the C# source; biomeGenerationEnabled ships off with scribe default off', [SRC + 'preflight_pyrelands.py', VAL, SRC + 'Source/RM_PyrelandsMod.cs'])
off('T_FRUIT_CLEAR', SRC + 'selftest_pyrelands_fruit_clear.py', 'the scene harness clears every scorch-fruit and stray fire before sc_scorchfruit (harness, not mod)', [VAL])
off('T_SETTINGS_SCREENS', 'src/RimMandrake/Utils/selftest_settings_screens.py', 'the real Mod Settings screen: every setting grouped, resettable, scoped honestly, Reset-all present; mutants caught (Pyrelands rows only)', [SRC + 'Source/RM_PyrelandsMod.cs'], mod_rows='Pyrelands:')
off('T_BARBSLINGER', 'src/RimMandrake/Utils/selftest_barbslinger_two_tails.py', 'the barbslinger art shows two tails', [SRC + 'Textures/', SRC + 'Defs/ThingDefs_Races/'])
off('T_REVIEW_MAP', SRC + 'review/selftest_pyre_review_map.py', 'the review map plan: layout, coverage, every def a station names exists', [SRC + 'review/'])
# the fire-hawk hunt rewards (bar inv_firehawk_hunt_rewards, his card 2026-11-14): tests built with the items 2026-11-13
off('T_FH_LETTER', SRC + 'selftest_pyrelands_firehawk_letter.py', 'the first-sighting letter: keyed strings for every key the code translates, the Mod Settings toggle ships on, is saved and drawn, and feeds the once-per-game gate with its saved flag', [SRC + 'Source/FireHawkRewards.cs', SRC + 'Source/RM_PyrelandsMod.cs', SRC + 'Languages/'])
off('T_FH_CRESTFEATHER', SRC + 'selftest_pyrelands_firehawk_crestfeather.py', 'the crestfeather trophy: the def exists with label, Beauty and a MarketValue above the hawk\'s; the hawk\'s race carries the 35 % butcher-trophy extension and the postfix that rolls it is on', [SRC + 'Defs/ThingDefs_Items/RM_PristineFirehawkCrestfeather.xml', SRC + 'Defs/ThingDefs_Races/', SRC + 'Source/FireHawkRewards.cs'])
# specified, built in Stage 3
off('T_SETTINGS_SWEEP_OFFLINE', SRC + 'selftest_pyrelands_settings_sweep.py', 'the settings sweep moved off the game: every Scribe field of RM_PyrelandsSettings has its default equal to its initializer and to shipped behaviour; every mechanic switch has a reader in its mechanic outside the settings file; every mechanic entry point consults PyrelandsMechanicsGate.On (static half of g10); a mutant dropping a reader or flipping a default goes red', [SRC + 'Source/RM_PyrelandsMod.cs', SRC + 'Source/PyrelandsMechanicsGate.cs', SRC + 'Source/'], new=True, item='RIMMANDRAKE_MOVE_PYRE_SETTINGS_SWEEP_OFFLINE (to file at Stage 3)')
off('T_DEFS_OFFLINE', SRC + 'selftest_pyrelands_defs_offline.py', 'static def reads: the biome weather list holds no ordinary rain; the biome description says engineered; flamefang venom is tendable and immunizable with falling tended severity (g7, def half); furnace-beast body size 6 in the def and its heat-immunity patch targets it (g6, static half); the sand shovel yields 5 glass sand and leaves gravel', [SRC + 'Defs/', SRC + 'Source/Patch_FurnaceBeastHeatImmunity.cs', SRC + 'Source/RM_TerrainDig.cs'], new=True, item='RIMMANDRAKE_PIN_PYRE_DEF_FACTS_OFFLINE (to file at Stage 3)')
off('T_CUT_STAYS_CUT', SRC + 'selftest_pyrelands_cut_stays_cut.py', 'the cut legs stay cut: no Firebreak terrain or chemfuel firebreak, no lightning breaker or fulgurite, no world-map herd migration in any description (g12)', [SRC + 'Defs/', SRC + 'About/', SRC + 'Languages/', SRC + 'Patches/'], new=True, item='RIMMANDRAKE_PIN_PYRE_CUT_LEGS_ABSENT (to file at Stage 3)')
# his card 2026-11-14 on ullai crossing the map in vanilla herd migrations: "Yes, let them cross"
off('T_ULLAI_HERD_MIGRATES', SRC + 'selftest_pyrelands_ullai_herd_migration.py', 'RM_Ullai stays a herd vanilla herd migration can pick: herdAnimal true, an animal (not a tool user, organic flesh), herdMigrationAllowed never false through its parents or any patch, a PawnKindDef for it, and RM_Pyrelands lists it with commonality above 0 (IncidentWorker_HerdMigration.IsValidBiomeAnimal); 12 mutants red', [SRC + 'Defs/ThingDefs_Races/RM_Ullai.xml', SRC + 'Defs/BiomeDefs/Pyrelands.xml', 'src/RimMandrake/Pyrelands/Patches/', '/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data/Core/Defs/ThingDefs_Races/Races_Animal_Base.xml'])
off('T_ASH_PROBE_OFFLINE', SRC + 'selftest_pyrelands_ash_probe.py', 'PyrelandsAshField.ProbeCell reports fertility part by part (dry, watered, burn bonus) from RM_FireEcoKernel.AshFertility, and refuses with ashWaterFertilityEnabled off', [SRC + 'Source/PyrelandsAshField.cs', K + 'RM_FireEcoKernel.cs'], new=True, item='RIMMANDRAKE_PIN_PYRE_ASH_PROBE_OFFLINE (to file at Stage 3)')
GAME = 'a running Pyrelands map with the biome\'s clocks (tier_reason of the leaf): a dev quicktest colony on the minimal list plus mandrake.rm.biomes, ~90 s'
for c in scn['scenes']:
    fn = c['entry_point'].split('::')[1]; full = c['id'] == 'sc_walk'
    reqs = c.get('requirement') or []
    T[c['id']] = dict(id=c['id'], kind='live_full' if full else 'live_minimal', stage='6', file=VAL, entry=fn,
        observes=c['expect'] if isinstance(c['expect'], str) else json.dumps(c['expect']), reads=[VAL, P + 'scenes.json'],
        command='python.exe src\\RimMandrake\\Pyrelands\\validation.py --live %s   (%s)' % (fn, 'full list' if full else 'minimal list + mandrake.rm.biomes'),
        why_game='two weeks of ordinary play with a mid-way reload: clocks, saves and the whole list together' if full else GAME,
        why_full_list='the walk is ordinary play on his list (leaf walk_season_on_the_pyre, tier live_full)' if full else None,
        entry_exists=fn in valdefs, item=c.get('entry_point_item'))
for fn in ['startup_and_def_wiring', 'mapgen_log', 'grass_cover', 'animal_census', 'ambient_ash_drift', 'opening_front', 'scorchfruit_produces', 'scorchfruit_spoils', 'furnace_room', 'ashfall_weather_accumulation', 'ashfall_drifts', 'blackrain']:
    T['P_' + fn] = dict(id='P_' + fn, kind='live_minimal', stage='6', file=VAL, entry=fn, observes='older north-star proof function cited by record.json proof_evidence', reads=[VAL],
        command='python.exe src\\RimMandrake\\Pyrelands\\validation.py --live %s' % fn, why_game=GAME, why_full_list=None, entry_exists=fn in valdefs)
for fn, f in [('P_firefoam_aim', SRC + 'firefoam_aim_live_proof.py'), ('P_gate', SRC + 'gate_live_proof.py')]:
    T[fn] = dict(id=fn, kind='live_minimal', stage='6', file=f, observes='live proof script cited by record.json proof_evidence', reads=[f], command='python.exe ' + f.replace('/', '\\'), why_game=GAME, why_full_list=None, entry_exists=True)
FHL = SRC + 'firehawk_rewards_live.py'; fhdefs = set(re.findall(r'^    def (\w+)\(', open(FHL).read(), re.M))
for fn, obs in [('firehawk_first_sighting_letter', 'a staged hawk carrying an ember on the home map, unfogged: exactly one letter pointing at it; a second carrying hawk: still one; toggle off and re-armed: none'),
                ('firehawk_crestfeather_yield', '400 fire-hawks butchered through the patched Pawn.ButcherProducts under a fixed seed: the 35 % yield within 4 sigma; the trophy\'s Beauty and MarketValue in the running game equal the def\'s')]:
    T[fn] = dict(id=fn, kind='live_minimal', stage='6', file=FHL, entry=fn, observes=obs, reads=[FHL], command='modcheck run Pyrelands --chains ' + fn + '   (minimal list + mandrake.rm.biomes; state reads only, flight never watched)',
        why_game=GAME, why_full_list=None, entry_exists=fn in fhdefs)
T['RECORD_ART_SHEET'] = dict(id='RECORD_ART_SHEET', kind='record', stage='2', file='infrastructure/state/ledger/events/', observes='his approval of the shipped art sheet exists on the ledger (OWNER:1792122659817386516)', reads=['infrastructure/state/ledger/events/'])
T['LOOK_STAGE8'] = dict(id='LOOK_STAGE8', kind='look', stage='8', file='(his walk)', observes='his walk of a fresh map: the burn line walking across deep ash, scorch-fruit right behind it, the grass greening a few days later (vision line 9)', reads=[], runs_today={'ran': False, 'why': 'Stage 8'})
# RIMMANDRAKE_KEEP_PYRELANDS_TABLE_ADDITIONS_THE_MAKER_ERASES: other tools write into the table this replaces (testq_blocks.py's
# testq blocks, round-6 tests, a record's rerun command). Keep every test this file does not define and every key it does not
# write (never runs_today or new: those are measured here); carried offline tests are rerun below with the rest.
import os
PREV = json.load(open(V + 'test_table.json')) if os.path.exists(V + 'test_table.json') else {}
MADE = set(T)
for tid, t in (PREV.get('tests') or {}).items():
    if tid not in T:
        T[tid] = {k: v for k, v in t.items() if k != 'runs_today'}
    else:
        for k, v in t.items():
            if k not in T[tid] and k not in ('runs_today', 'new'): T[tid][k] = v
# ---- bars: decides / supports (hand judgment)
B = [
 ('burn_line_walks', ['sc_burn_line_walks'], ['T_FUZZ', 'P_opening_front', 'LOOK_STAGE8']),
 ('ash_ground_and_blowing_ash', ['sc_ash_ground', 'sc_fire_dusts_ash'], ['T_LINT', 'T_FUZZ', 'T_TRACKS', 'P_ambient_ash_drift']),
 ('ash_fertile_when_watered', ['sc_ash_watered'], ['T_FUZZ']),
 ('fresh_burn_compounds_with_black_rain', ['sc_burn_compounds'], ['T_FUZZ', 'T_ASH_PROBE_OFFLINE']),
 ('grass_carpets_and_regreens', ['sc_grass_regreens'], ['T_LINT', 'P_grass_cover', 'LOOK_STAGE8']),
 ('scorchfruit_born_of_fire', ['sc_scorchfruit'], ['T_FRUIT_CLEAR', 'T_BURN_COST', 'P_scorchfruit_produces', 'P_scorchfruit_spoils', 'LOOK_STAGE8']),
 ('populations_are_the_biomes_own', ['sc_populations', 'T_ALLOWLIST'], ['T_LINT', 'T_SITE', 'P_animal_census', 'P_mapgen_log']),
 ('ruins_stand_blackened', ['sc_ruins'], []),
 ('firehawk_lights_ahead', ['sc_firehawk'], ['T_FUZZ']),
 ('furnacebeast_warms', ['sc_furnace', 'sc_furnace_bed', 'sc_furnace_giant', 'T_FURNACE_WARMTH'], ['T_FUZZ', 'T_DEFS_OFFLINE', 'P_furnace_room']),
 ('ashwallow_dives_unharmed', ['sc_ashwallow', 'sc_heat_dome'], ['T_BURN_COST']),
 ('ullai_graze_old_burns', ['sc_ullai'], ['T_LINT']),
 ('three_skies', ['sc_three_skies'], ['P_ashfall_weather_accumulation', 'P_ashfall_drifts', 'P_blackrain']),
 ('no_ordinary_rain', ['T_DEFS_OFFLINE', 'sc_no_rain'], []),
 ('ash_fertility_probe', ['T_ASH_PROBE_OFFLINE'], ['T_FUZZ', 'sc_burn_compounds']),
 ('walk_season_on_the_pyre', ['sc_walk'], ['LOOK_STAGE8']),
 ('firefoam_sprayer_reaches_the_fruit', ['sc_firefoam_sprayer'], ['P_firefoam_aim']),
 ('sand_shovel_yields_glass_sand', ['sc_sand_shovel'], ['T_DEFS_OFFLINE']),
 ('fire_rite_hook_silent_alone', ['sc_rite_hook_alone'], []),
 ('biome_text_says_engineered', ['T_DEFS_OFFLINE'], []),
 ('flamefang_bite_carries_venom', ['sc_flamefang_venom'], ['T_DEFS_OFFLINE']),
 ('inv_biome_self_contained', ['T_LINT', 'sc_populations'], ['T_SITE', 'P_startup_and_def_wiring', 'P_mapgen_log']),
 ('inv_plant_roster', ['sc_populations', 'T_ALLOWLIST', 'T_LINT'], ['P_grass_cover']),
 ('inv_embergrass_regrow', ['sc_grass_regreens'], ['T_LINT']),
 ('inv_animal_roster', ['sc_populations'], ['P_animal_census', 'sc_flamefang_venom', 'T_DEFS_OFFLINE']),
 ('inv_ash_field', ['sc_ash_ground', 'sc_ash_watered', 'sc_burn_compounds'], ['T_FUZZ', 'T_LINT', 'T_TRACKS', 'sc_fire_dusts_ash', 'P_ambient_ash_drift']),
 ('inv_burn_line_fire_clock', ['sc_burn_line_walks', 'T_FUZZ'], ['P_opening_front', 'sc_fire_dusts_ash', 'T_BURN_COST']),
 ('inv_scorchfruit', ['sc_scorchfruit'], ['T_FRUIT_CLEAR', 'P_scorchfruit_produces', 'P_scorchfruit_spoils']),
 ('inv_ruins_scorched', ['sc_ruins'], []),
 ('inv_firehawk_ember', ['sc_firehawk'], ['T_FUZZ']),
 ('inv_furnacebeast', ['sc_furnace', 'sc_furnace_bed', 'T_FURNACE_WARMTH'], ['T_FUZZ', 'T_DEFS_OFFLINE', 'P_furnace_room']),
 ('inv_burrowers_heat_dome', ['sc_ashwallow', 'sc_heat_dome'], ['T_BURN_COST']),
 ('inv_ullai_herd_giant', ['sc_ullai', 'sc_furnace_giant'], ['T_CUT_STAYS_CUT', 'T_ULLAI_HERD_MIGRATES']),
 ('inv_weather', ['sc_three_skies', 'sc_no_rain', 'T_DEFS_OFFLINE'], ['P_ashfall_weather_accumulation', 'P_ashfall_drifts', 'P_blackrain']),
 ('inv_firebreak_firefoam', ['T_CUT_STAYS_CUT'], []),
 ('inv_firefoam_sprayer', ['sc_firefoam_sprayer'], ['P_firefoam_aim']),
 ('inv_sand_shovel', ['sc_sand_shovel'], ['T_DEFS_OFFLINE']),
 ('inv_lightning_breaker', ['T_CUT_STAYS_CUT'], []),
 ('inv_fire_rite_hook', ['sc_rite_hook_alone'], []),
 ('inv_settings_gate', ['T_SETTINGS_SWEEP_OFFLINE', 'T_SETTINGS_SCREENS', 'T_SITE'], ['sc_walk', 'P_gate']),
 ('inv_art_and_text', ['RECORD_ART_SHEET', 'T_DEFS_OFFLINE'], ['sc_three_skies', 'T_BARBSLINGER', 'T_TRACKS', 'T_REVIEW_MAP']),
 ('inv_firehawk_hunt_rewards', ['T_FH_LETTER', 'T_FH_CRESTFEATHER', 'firehawk_first_sighting_letter', 'firehawk_crestfeather_yield'], ['T_FUZZ', 'LOOK_STAGE8']),
 # his card 2026-11-14 ("Yes, let them cross"), leaf added by the locked change 91a7c61989 (OWNER:1794748469904049550)
 ('ullai_cross_the_map_as_vanilla_herds', ['T_ULLAI_HERD_MIGRATES', 'sc_foreign_arrivals', 'T_CUT_STAYS_CUT'], []),
]
# a leaf that states an existing bar's promise is coverage of that bar, not a bar (locked change 91a7c61989; the leaf's
# experience is the bar's text, letter and crestfeather alike, and promises nothing a player would notice beyond it)
COVERAGE = {'firehawk_hunt_rewards': 'inv_firehawk_hunt_rewards'}
PB = {b['id']: b for b in PREV.get('bars') or [] if isinstance(b, dict)}
B = [(bid, dec + [x for x in PB.get(bid, {}).get('decides', []) if x not in MADE and x not in dec],
      sup + [x for x in PB.get(bid, {}).get('supports', []) if x not in MADE and x not in sup]) for bid, dec, sup in B]
# ---- measure: run every built offline test
for t in T.values():
    if t['kind'] != 'offline': 
        if t['kind'].startswith('live'):
            t['runs_today'] = {'ran': False, 'why': 'live: this run is offline only; entry %s in %s' % ('exists' if t['entry_exists'] else 'ABSENT', t['file'].split('/')[-1])}
        elif t['kind'] == 'record':
            n = subprocess.run(['git', 'grep', '-c', '1792122659817386516', '--', 'infrastructure/state/ledger/events/'], capture_output=True, text=True).stdout.strip()
            t['runs_today'] = {'ran': True, 'result': 'PASS' if n else 'FAIL', 'last': n.replace('\n', '; ')[:200], 'at': NOW}
        continue
    if t.get('new'):
        t['runs_today'] = {'ran': False, 'why': 'specified, not built (Stage 3)'}; continue
    s = time.time(); r = subprocess.run(['python3', t['file']], capture_output=True, text=True, timeout=600); d = round(time.time() - s, 2)
    lines = (r.stdout + r.stderr).strip().splitlines(); last = lines[-1][:200] if lines else ''
    res = 'PASS' if r.returncode == 0 else 'FAIL'
    if t.get('mod_rows'):
        rows = [l for l in lines if t['mod_rows'] in l and l.split()[0] in ('ok', 'FAIL')]
        bad = [l for l in rows if l.startswith('FAIL')]
        res = 'PASS' if rows and not bad else 'FAIL'; last = '%s; %s rows for this mod, %d red' % (last, len(rows), len(bad))
    t['runs_today'] = {'ran': True, 'rc': r.returncode, 'seconds': d, 'last': last, 'at': NOW, 'result': res}
def runnable(tid):
    t = T[tid]; rt = t.get('runs_today', {})
    if t['kind'] in ('offline', 'record'): return rt.get('ran') and rt.get('result') == 'PASS'
    if t['kind'].startswith('live'): return t['entry_exists']
    return False
SO = {'2': 2, '3': 3, '4-5': 4, '6': 6, '8': 8}
bars = []
for bid, dec, sup in B:
    src = 'tree.json' if bid in leaves else 'record.json'
    kind = leaves[bid]['leaf_kind'] if bid in leaves else ('inventory, scope out (absence)' if inv[bid].get('scope') == 'out' else 'inventory')
    offd = [x for x in dec if T[x]['kind'] in ('offline', 'record')]
    bars.append(dict(id=bid, source=src, kind=kind, proves_at=max((T[x]['stage'] for x in dec), key=lambda s: SO[s]), decides=dec, supports=sup, held=[],
        offline_decides=offd, offline_green_today=bool(offd) and all(runnable(x) for x in offd),
        every_decider_runnable_today=all(runnable(x) for x in dec), any_test_runnable_today=any(runnable(x) for x in dec + sup)))
LOCKED = json.load(open(V + 'locked_bars.json'))['ids']
assert set(COVERAGE) <= set(leaves) and set(COVERAGE.values()) <= set(LOCKED) and not set(COVERAGE) & set(LOCKED), 'a coverage leaf must map onto a locked bar'
assert set(b['id'] for b in bars) == (set(leaves) - set(COVERAGE)) | set(inv) == set(LOCKED) and len(bars) == len(LOCKED), 'bar set differs from locked_bars.json (bars.md)'
for b in bars: b['covered_by_leaves'] = sorted(l for l, t in COVERAGE.items() if t == b['id'])
for b in bars:
    for x in b['decides'] + b['supports']: assert x in T, x
lost = [(tid, k) for tid, t in (PREV.get('tests') or {}).items() for k in t if k not in ('runs_today', 'new') and k not in T.get(tid, {})]
lost += [(bid, x) for bid, pb in PB.items() for x in pb.get('decides', []) + pb.get('supports', []) if x not in MADE and bid in {b['id'] for b in bars}
         and x not in next(b for b in bars if b['id'] == bid)['decides'] + next(b for b in bars if b['id'] == bid)['supports']]
assert not lost, 'the remake would lose what the previous table held: %s' % lost[:5]
out = dict(mod='Pyrelands', version='0.1.0', made=NOW, made_by='rm-builder, Maturation advance row 2 beside the pilot (throwaway make_test_table.py)',
    stages={'2': 'preflight (a program)', '4-5': 'blind offline challenge and game-logic testing', '6': 'in-game acceptance', '8': 'his live walk'},
    rule='a bar passes when every test in decides passes; proves_at is the highest stage among them; supports add evidence but decide nothing',
    settings_move='inv_settings_gate was proven only by the two-week walk (coverage_rest). Its defaults, readers and gate checks are now decided offline by T_SETTINGS_SWEEP_OFFLINE (specified), T_SETTINGS_SCREENS and T_SITE (built); sc_walk keeps only the gate-off read in play, as support. No bar text is edited.',
    coverage_leaves={l: dict(bar=t, why='the leaf states the bar\'s promise; it is that bar\'s coverage, not a bar') for l, t in COVERAGE.items()},
    held_statements=[], held_note='0 held look statements name Pyrelands (grep of design/RimMandrake/validation_holding/*.md for pyre|ember|scorch|ash, 2026-11-14; the same grep for knockback finds 7 lines)',
    corrections=json.load(open('/mnt/d/ClaudeWork/scratch/pyrelands_advance/corrections.json')), tests=T, bars=bars)
json.dump(out, open(V + 'test_table.json', 'w'), indent=1, ensure_ascii=False); open(V + 'test_table.json', 'a').write('\n')
# ---- read view
live = [t for t in T.values() if t['kind'].startswith('live')]; offl = [t for t in T.values() if t['kind'] == 'offline']
sc = [t for t in live if t['id'].startswith('sc_')]
cnt = dict(bars=len(bars), any=sum(b['any_test_runnable_today'] for b in bars), every=sum(b['every_decider_runnable_today'] for b in bars),
    offgreen=sum(b['offline_green_today'] for b in bars), offonly=sum(all(T[x]['kind'] in ('offline', 'record') for x in b['decides']) for b in bars),
    offonly_built=sum(all(T[x]['kind'] in ('offline', 'record') and not T[x].get('new') for x in b['decides']) for b in bars),
    sc=len(sc), sc_ok=sum(t['entry_exists'] for t in sc), built=sum(not t.get('new') for t in offl), spec=sum(bool(t.get('new')) for t in offl),
    green=sum(t['runs_today'].get('result') == 'PASS' for t in offl if not t.get('new')))
md = ['# Pyrelands 0.1.0: test-and-stage table', '', 'Generated %s from `test_table.json` (the record; this is its read view). Stages: 2 preflight, 4-5 blind offline, 6 in-game, 8 his walk. A bar passes when every deciding test passes. Same columns as Explosive Knockback\'s table.' % NOW, '', '## Counts (measured)', '',
 '- bars: %(bars)d' % cnt,
 '- with at least one test runnable today (a built offline test that ran green, or an in-game scene whose entry exists in validation.py): %(any)d' % cnt,
 '- with every deciding test runnable today: %(every)d' % cnt,
 '- with an offline deciding test, all green today: %(offgreen)d' % cnt,
 '- decided offline only (no game needed): %(offonly)d, of which every decider is built: %(offonly_built)d' % cnt,
 '- scenes.json scenes: %(sc)d, entry exists %(sc_ok)d, absent %%d' % cnt % (cnt['sc'] - cnt['sc_ok']),
 '- offline tests: %(built)d built (ran today: %(green)d green for this mod), %(spec)d specified for Stage 3' % cnt, '',
 '## Bars', '', '| bar | from | proves at | decides | supports | runnable today |', '|---|---|---|---|---|---|']
for b in bars:
    r = 'all' if b['every_decider_runnable_today'] else ('some' if any(runnable(x) for x in b['decides']) else 'none')
    md.append('| `%s` | %s | %s | %s | %s | %s |' % (b['id'], b['source'].split('.')[0], b['proves_at'], ', '.join(b['decides']), ', '.join(b['supports']) or '-', r))
md += ['', '## Leaves that are coverage of a bar (not bars)', ''] + ['- `%s` covers bar `%s`' % (l, t) for l, t in COVERAGE.items()]
md += ['', '## Tests', '', '| test | kind | stage | file | runs today |', '|---|---|---|---|---|']
for t in T.values():
    rt = t.get('runs_today', {})
    s = ('%s %.1fs' % (rt['result'], rt['seconds'])) if rt.get('seconds') is not None else (rt.get('result') or rt.get('why', ''))
    md.append('| `%s` | %s | %s | `%s`%s | %s |' % (t['id'], t['kind'], t['stage'], t['file'], (' :: ' + t['entry']) if t.get('entry') else '', s))
md += ['', '## Corrections applied (judge gaps sorted CORRECTION)', '', '| gap | where | status |', '|---|---|---|']
for c in out['corrections']: md.append('| %s | %s | %s |' % (c['gap'], c['where'], c['status']))
md += ['', '## The settings move', '', out['settings_move'], '', '## Held look statements', '', out['held_note'] + '.', '']
open(V + 'test_table.md', 'w').write('\n'.join(md))
print(json.dumps(cnt))
