"""
Apply the Twilight Sea's five mutator passes (ICE MARGIN, DAY/NIGHT SHORE,
SEA FOG, DROWNED COAST, SHIPPING LANE) from twilight_plan.json (built by
plan_twilight_mutators.py) to the live planet over the RimBridge bridge.

MUST run under python.exe (Windows loopback; python3 in WSL2 cannot reach
the bridge - NAT-mode network namespace). Reads twilight_plan.json via a
Windows path for the same reason.

Traps hit while writing this:
  - jawa/world_tile_get (which would have given an exact coastSides scalar)
    THROWS "Object must implement IConvertible" on this build regardless of
    argument shape tried (tiles=[...] and tiles="a,b,c" both failed the same
    way) -- so every coastal gate in the plan was computed from the ENGINE
    SOURCE formula (TileMutatorDef.IsValidTile: a neighbour counts only if
    its PrimaryBiome is Ocean or Lake) applied to now_tiles.csv's biome
    column, not from a live per-tile read. See plan_twilight_mutators.py's
    header for the full derivation.
  - THE FOG PROBE, run before anything else per the task brief: two Ocean
    tiles got FoggyMutator written, read back, and the setter reported
    success with no errors -- but that is NOT evidence FoggyMutator is legal
    on Ocean. Tile.AddMutator (which jawa/world_mutators_set calls) never
    calls TileMutatorDef.IsValidTile at all -- read directly in the RimWorld
    source, confirmed no gate check exists in either the setter's C# or
    AddMutator itself. The write cannot fail no matter what def or tile you
    give it (short of an unknown defName or an exception in the def's
    OnAddedToTile worker). So "success: true, no errors" was read from the
    engine source BEFORE this script ran, expected, and NOT the test that
    decides anything.
    The real test is FoggyMutator's actual biomeWhitelist, read directly out
    of Defs/Odyssey/TileMutators/TileMutators_Modifiers.xml via the rimsage
    MCP (not the live roster's truncated note): BorealForest, ColdBog,
    TemperateForest, TemperateSwamp, TropicalRainforest, TropicalSwamp,
    Grasslands, Glowforest, Scarlands. Ocean is not there and never was.
    FoggyMutator is REMOVED from both probe tiles after the probe runs, and
    pass 3 ships as the WindyMutator fallback BRIEF.md specified in advance --
    already folded into the WindyMutator group in twilight_plan.json (the
    seaice_band + arid_shore subsets), so no separate write is needed for it.
  - world_mutators_audit's coastal check (`marineMutators`) is a BOOLEAN per
    tile (World.CoastDirectionAt != Invalid), not the numeric coastSidesRange
    this plan enforces. Critically, CoastDirectionAt returns Invalid outright
    for any tile whose OWN PrimaryBiome has canBuildBase=false -- which is
    true for every Ocean tile on this planet, confirmed by reading
    world/_roads/_muts_now.json: every sampled Ocean tile shows isCoastal
    False regardless of what borders it, while SeaIce tiles bordering Ocean
    show isCoastal True. So Fish_Increased / AnimalLife_Increased /
    VEE_MarineSanctuary (placed on Ocean tiles in this plan) would ALWAYS
    read as "offenders" if fed into marineMutators -- not because anything
    is wrong, but because the audit's coastal check cannot ever be True for
    an Ocean tile. Only the LAND/SeaIce-side defs go into marineMutators;
    the Ocean-tile defs are verified by plain world_mutators_get read-back
    instead (done in verify script).
  - THE INCIDENT: world_mutators_audit scans the WHOLE PLANET, every tile,
    every time -- there is no way to scope it to one sea. The first live run
    of this script put VEE_SaltPlains into the final marineMutators list
    (because BRIEF's own GATES table mentions it in the same breath as other
    coastal defs) and that flagged 313 PRE-EXISTING VEE_SaltPlains placements
    across the ENTIRE PLANET as "offenders" -- ordinary inland desert salt
    flats hundreds of tiles from any sea, none of them written this session,
    because VEE_SaltPlains was never actually coastal-gated in the first
    place (its real gate is inland biome + no-river; see plan script header).
    The auto-remove-offenders loop then DELETED 48 of those plus 2
    pre-existing VEE_GravelBeach tiles near an unrelated Lake elsewhere on
    the planet (CoastDirectionAt only recognises Ocean neighbours, not Lake,
    so a legitimate lake-adjacent gravel beach reads as "non-coastal" too).
    All 50 were identified from the report's removed_offenders list and
    RESTORED live (jawa/world_mutators_set add + world_commit +
    world_mutators_get confirming all 50 present again) before anything else
    continued -- see twilight_apply_report.json's final_audit_INCIDENT block
    for the exact tile list. The fix, baked into the code below: (1)
    marineMutators is restricted to defs that are ACTUALLY coastal-gated per
    BRIEF's own table with a numeric coastSidesRange -- never VEE_SaltPlains;
    (2) limit is raised so nothing hides past the default cap of 30; (3)
    every offender is checked against THIS SESSION'S OWN written tile lists
    before being touched, and only a genuine intersection is ever removed.
    Measured after the fix: offenderCount 13, all 13 pre-existing elsewhere
    on the planet (Volcano, AB_PyroclasticConflagration, AB_FeraliskInfested-
    Jungle biomes -- nowhere near the Twilight Sea), none on a tile this
    session wrote. Nothing further removed.
    The general lesson: a whole-planet audit tool is a loaded gun on a repo
    four other seats share. Never pass a def to marineMutators without first
    confirming, from the def's OWN gate (not a category guess), that a "not
    coastal" verdict for that def would actually mean something -- and
    always intersect offenders against your own written tiles before any
    removal call, never trust the tool's list as scoped to your own work.
"""
import sys, json

sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint

PLAN_PATH = r'D:\Luke\dev\Rimworld\world\_twilight\twilight_plan.json'
REPORT_PATH = r'D:\Luke\dev\Rimworld\world\_twilight\twilight_apply_report.json'

plan = json.load(open(PLAN_PATH))
groups = plan['groups']
meta = plan['meta']

report = {'fog_probe': None, 'writes': [], 'final_audit': None}

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:

    def set_mut(action, mutators, tiles, note):
        if not tiles:
            report['writes'].append({'def': mutators, 'note': note, 'intended': 0, 'skipped': True})
            print(mutators, 'SKIPPED (0 tiles) --', note)
            return
        r = rb.call('jawa/world_mutators_set', {
            'action': action, 'mutators': mutators,
            'tiles': ','.join(str(t) for t in tiles), 'readBack': 0,
        })
        row = {
            'def': mutators, 'action': action, 'note': note, 'intended': len(tiles),
            'success': r.get('success'), 'added': r.get('added'), 'removed': r.get('removed'),
            'unknownDefs': r.get('unknownDefs'), 'errors': r.get('errors'),
        }
        report['writes'].append(row)
        print(json.dumps(row)[:300])

    # ================================================================
    # THE FOG PROBE -- must run before anything else, per the task brief
    # ================================================================
    probe_tiles = meta['fog_probe_tiles']
    r = rb.call('jawa/world_mutators_set', {
        'action': 'add', 'mutators': 'FoggyMutator',
        'tiles': ','.join(str(t) for t in probe_tiles), 'readBack': 2,
    })
    rb.call('jawa/world_commit', {})
    got = rb.call('jawa/world_mutators_get', {
        'tiles': ','.join(str(t) for t in probe_tiles), 'limit': 5,
    })
    landed = {row['tile']: [m['def'] for m in row['mutators']] for row in got.get('tiles', [])}
    report['fog_probe'] = {
        'tiles': probe_tiles, 'setter_success': r.get('success'), 'setter_errors': r.get('errors'),
        'readback': landed,
        'verdict': 'REJECTED -- Ocean is not in FoggyMutator biomeWhitelist '
                   '(BorealForest,ColdBog,TemperateForest,TemperateSwamp,TropicalRainforest,'
                   'TropicalSwamp,Grasslands,Glowforest,Scarlands), read from '
                   'Defs/Odyssey/TileMutators/TileMutators_Modifiers.xml. The setter reporting '
                   'success is expected and not evidence -- Tile.AddMutator never validates '
                   'biomeWhitelist. Removing FoggyMutator from both probe tiles now; pass 3 '
                   'ships as WindyMutator (already in the WindyMutator write below).',
    }
    print('FOG PROBE setter success:', r.get('success'), 'readback:', landed)
    # Remove it -- it does not belong on Ocean regardless of what the setter allowed.
    rb.call('jawa/world_mutators_set', {
        'action': 'remove', 'mutators': 'FoggyMutator',
        'tiles': ','.join(str(t) for t in probe_tiles), 'readBack': 0,
    })
    rb.call('jawa/world_commit', {})
    print('fog probe tiles cleaned up (FoggyMutator removed)')

    # ================================================================
    # PASS 1 -- THE ICE MARGIN
    # ================================================================
    set_mut('add', 'Iceberg', groups['Iceberg'],
             'iceedge tiles, temp -100..0C, biome SeaIce, no river, coast_count 3-5 (engine-exact)')
    set_mut('add', 'Fish_Increased', groups['Fish_Increased'],
             'UNION of the 39 open-water edge tiles (pass 1) and the shipping-lane fisheries '
             '(pass 5, near Boilquay/Deepwater Hold) -- one def, written once for both passes')
    set_mut('add', 'AnimalLife_Increased', groups['AnimalLife_Increased'],
             'the 39 open-water edge tiles (ice margin only, pass 1), ungated, minus Fish_Decreased tiles')
    set_mut('add', 'VEE_GravelBeach', groups['VEE_GravelBeach'],
             'ice tiles at shore distance 1 with a real Ocean/Lake neighbour (coast_count 1-6)')

    # ================================================================
    # PASS 2 -- THE DAY SHORE AND THE NIGHT SHORE
    # ================================================================
    set_mut('add', 'VEE_SaltPlains', groups['VEE_SaltPlains'],
             'dayside ring, biome Desert/ExtremeDesert/Tundra/AridShrubland/Grasslands, no river')
    set_mut('add', 'DryGround', groups['DryGround'],
             'MEASURED EMPTY: biome Scarlands/BorealForest/Tundra absent from every ring tile')
    set_mut('add', 'Oasis', groups['Oasis'],
             'dayside ring, biome Desert/ExtremeDesert/Savanna, temp 20-60C, no river')
    set_mut('add', 'SunnyMutator', groups['SunnyMutator'], 'dayside ring, ungated')
    set_mut('add', 'IceDunes', groups['IceDunes'],
             'MEASURED EMPTY: biome SeaIce/IceSheet absent from every nightside ring tile')
    set_mut('add', 'VEE_DeepSnow', groups['VEE_DeepSnow'],
             'MEASURED EMPTY: biome IceSheet/SeaIce/Tundra absent from every nightside ring tile')
    set_mut('add', 'WindyMutator', groups['WindyMutator'],
             'nightside ring (Arid/Desert biome) UNION SeaIce band UNION dayside arid shores '
             '(the pass-3 fallback, folded in here -- see fog probe above)')

    rb.call('jawa/world_commit', {})
    print('committed passes 1-2')

    # ================================================================
    # PASS 4 -- THE DROWNED COAST
    # ================================================================
    set_mut('add', 'VEE_RisingWaters', groups['VEE_RisingWaters'],
             'flat ring tiles, coast_count 1-5')
    set_mut('add', 'VEE_RelictDelta', groups['VEE_RelictDelta'],
             'MEASURED EMPTY: every ring tile within 3 hops of the one river mouth (18267) is '
             'AB_MiasmicMangrove/Wasteland, neither in the biome whitelist')
    set_mut('add', 'CoastalAtoll', groups['CoastalAtoll'],
             'former-seabed ring tiles, hilliness<=SmallHills, no river, coast_count 3-5')
    set_mut('add', 'VEE_LoneIsland', groups['VEE_LoneIsland'],
             'former-seabed ring tiles not already CoastalAtoll, coast_count 3-5')

    rb.call('jawa/world_commit', {})
    print('committed pass 4')

    # ================================================================
    # PASS 5 -- THE SHIPPING LANE
    # ================================================================
    set_mut('add', 'VEE_MarineSanctuary', groups['VEE_MarineSanctuary'],
             'Ocean tiles near Boilquay/Deepwater Hold, coast_count 1-5')
    set_mut('add', 'AncientRuins', groups['AncientRuins'],
             'former-seabed ring tiles ("islands"), ungated except AB_MechanoidIntrusion')
    set_mut('add', 'AncientWarehouse', groups['AncientWarehouse'],
             'former-seabed ring tiles not already AncientRuins, biome-locked subset')
    set_mut('add', 'Bay', groups['Bay'],
             'ring tiles near Blackstar Field/Hardpan Yard, biome-locked, coast_count 1-5')

    rb.call('jawa/world_commit', {})
    print('committed pass 5')

    # ================================================================
    # FINAL AUDIT -- ONLY defs that are actually coastSidesRange-gated in
    # BRIEF's own table (never VEE_SaltPlains -- see THE INCIDENT above),
    # `limit` raised past the 30-row default so nothing hides, and every
    # offender cross-checked against THIS SESSION'S OWN written tiles
    # before anything is ever removed -- world_mutators_audit scans the
    # WHOLE PLANET and a pre-existing tile elsewhere is not our business.
    # ================================================================
    land_marine_defs = 'Iceberg,VEE_GravelBeach,VEE_RisingWaters,CoastalAtoll,VEE_LoneIsland,Bay'
    my_tiles_by_def = {d: set(groups.get(d, [])) for d in land_marine_defs.split(',')}
    final_audit = rb.call('jawa/world_mutators_audit', {
        'marineMutators': land_marine_defs, 'limit': 500, 'histogram': False,
    })
    offenders = final_audit.get('offenders', [])
    mine = [o for o in offenders if o['tile'] in my_tiles_by_def.get(o['mutator'], set())]
    not_mine = [o for o in offenders if o not in mine]
    report['final_audit'] = {
        'marineMutators': land_marine_defs,
        'offenderCount': final_audit.get('offenderCount'),
        'offenders_total': len(offenders),
        'offenders_mine': mine,
        'offenders_preexisting_not_touched': not_mine,
    }
    print('FINAL offenderCount:', final_audit.get('offenderCount'),
          '-- mine:', len(mine), '/ pre-existing (not touched):', len(not_mine))

    if mine:
        for off in mine:
            rb.call('jawa/world_mutators_set', {
                'action': 'remove', 'mutators': off['mutator'],
                'tiles': str(off['tile']), 'readBack': 0,
            })
        rb.call('jawa/world_commit', {})
        report['final_audit']['removed_offenders'] = mine
        print('removed', len(mine), 'genuine offenders from this session\'s own writes')

json.dump(report, open(REPORT_PATH, 'w'), indent=1)
print('wrote', REPORT_PATH)
