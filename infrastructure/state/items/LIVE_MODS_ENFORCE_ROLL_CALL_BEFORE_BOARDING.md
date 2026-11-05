# LIVE_MODS_ENFORCE_ROLL_CALL_BEFORE_BOARDING

Owner, 2026-11-05: *"Yes. Do a deep design pass in the concept though to make sure it's well reasoned, then a skeptical
blind review pass, then file it as an expedited ticket. Include all the past queue items we're experiencing that have
modlist issues as their listed reason for failing."* Expedited by the Conductor.

Design: `design/RimMandrake/live_mods_filing_check_2026-11-05.md` (d531b91676). Blind review (GPT, given only the doc and
code): `design/RimMandrake/live_mods_filing_check_2026-11-05.blind_review.md` — verdict **ship with changes**. The review
is binding on scope: build the minimal scope below, not the doc's full §5.

## spec

Minimal scope (blind review "Recommended minimal scope"):
1. ONE shared name resolver for `live-mods:` / `live-deploy:` entries (repo folder, dotted/composed folder, workshop
   packageId), replacing `is_package` / `split_names`; verified alias normalization (folded biome sources →
   `RimMandrake.Biomes`).
2. Unknown name → refused with an actionable message (what it looked like, nearest known names), at proof-write/filing
   AND in `mod_gap`/`batch_gap` before a slot.
3. Per-rider validation BEFORE the batch union: a bad rider drops only itself; the leader and valid riders still ride.
4. Static need inference ADVISORY only: a warning with evidence (file:line), never an auto-write into a proof.

Out of scope (deferred by the review, file separately only if the measured result asks for it): auto-writing needs,
broad defName/namespace indexing, save-header mandates, post-failure writes, `live-tier:` / `live-absent:` (that is
`LANE_TIER_WIRE_A_WHOLE_LIST_LOAD`'s lane, incl. two riders where one needs X and one forbids X).

Review cautions to honour: the `--absent RUT_PaleMoss` pattern means a uniquely-owned defName is NOT proof of need;
an inline `# auto:` comment on a `live-mods:` line would parse as mod names (`relentless_live_round.py:108`);
`build_shas` already has a cited-build fallback (`:277`); `modlist_swap.py` adds only immediate deps (`:269`).

## verify

- Selftests (`run_selftests.py --only relentless_needs` plus the touched live_round/game tests), including the review's
  cases: defName only in an absence assertion → zero additions; leader + valid rider + invalid rider → both valid ride;
  missing index / transitive dep / repeated run idempotent.
- Replay over the census below with proof text AND scripts at the historical sha (no hindsight leakage): report how many
  R4 (wrong name/format) and R1 (outside mod omitted) cases the resolver refuses or warns on before the slot.

## criteria

- Every census item in R4 is refused before a slot in replay; every R1 item gets a warning or refusal; zero false
  refusals on the last 50 PASS proofs.
- After landing, one week of runs.jsonl: count of runs failing on a mod-list cause, against the census baseline.
  The review found the doc's totals inconsistent (29 vs 31 distinct IDs; 58 vs 57 item-games): recount the baseline
  from runs.jsonl first and state it.

## Census — the queue items with a mod-list failure reason (from the design doc §2, verbatim)

## 2 Census

The census was built from four instruments:

1. `D:\ClaudeWork\rimmandrake\livemods_design\census_runs.py` over `/home/mandrake/rm/relentless/live/runs.jsonl`. The log has 855 rows: 466 UNMEASURED, 146 REFUSED, 117 PASS, 92 FAIL and 34 null. They span 38 distinct `game` values (cold loads), dated 2026-11-02 to 2026-11-05.
2. `/home/mandrake/rm/relentless/store/items/*/state.json`, which holds 941 states: 647 done, 97 retired, 104 blocked, 46 game and 26 held.
3. `git log -p -- infrastructure/state/live_proofs/`. It shows 53 proof files whose `live-mods` line changed, and 26 changes that were retrofits to an existing line rather than present at creation.
4. A narrow ledger scan, which found 32 ids.

Sanity probes:

- The first slot script reported 0 for every item in "games before retrofit". That zero was a query bug: the diff hunk markers `@@` collided with the commit marker I had chosen. With a unique marker the script finds 26 retrofits and non-zero counts, and the total of 38 games matches a direct `set(game)` count.
- The pattern search was checked against a case known by hand. TIDAL_LOCK's "Type not found AlienWorlds.PlanetTypeManager" rows are found.
- The masked cases (R2-folded) were checked in the other direction. Their rows really do lack any mod-absence text, so a pattern search cannot find them. They count only through the git retrofit that repaired them.

Column definitions:

- **Games**: distinct cold loads in which the item's row carried an explicit mod-list cause.
- **Pre-fix**: non-PASS games before its last retrofit. This counts masked failures. It is an upper bound, because some of those failures had other causes as well.

### R1: the proof omitted a needed mod that lies outside its build (12 items)

| Item | State | Short reason | Dates | Games | Pre-fix |
|---|---|---|---|---|---|
| TIDAL_LOCK_FIX_PRESET_NAME_WAS_MISSING | retired | Type not found AlienWorlds.PlanetTypeManager; 7f.alienworlds unnamed (the code comment says about 20 runs) | 11-02..03 | 4 | - |
| SETTLEMENT_VERBS_WAVE_1 | held | the RimProperty DLL lacked the type the proof calls | 11-03..04 | 3 | 3 |
| GRAVSHIP_PEACEFUL_SETTLEMENT_LANDING_1 | done | KeelHoist and UtinniPatches (MayRequire) unnamed | 11-03 | 2 | 0 |
| CANON_MATERIALS_BUILD_1 | done | mandrake.rsw.armoury lacking from the running load | 11-04 | 2 | - |
| ART_OVERRIDE_FAMILY_SCRIPT_1 | game | donor mods (Webwork, Scarlands, sarg.alphamemes, VE genetics) unnamed; retrofitted twice | 11-03..05 | 7 | 6 |
| TAOZIN_SPLIT_BUILD_ONE_WORM_BECOMES_TWO | game | +EnvironmentalHazards and Stillsand, retrofitted 44 min after creation | 11-03 | 3 | 0 |
| TITANIC_BODYSIZE_TEST_RACE_1 | game | neku.largepawns and HugeThingsTestRaces; retrofitted twice | 11-02..05 | 1 | 1 |
| WORLD_NULLTEX_FLOOD_HUNT_STACKLESS_SO_FAR | game | MenuShell needs arandomkiwi.rimthemes, and NullTexTrace was unnamed; retrofitted twice | 11-02..05 | 4 | 5 |
| HEAVY_TEXTURES_MEASURE_REAL_VRAM | game | workshop dependencies unnamed; masked as proof_or_site | 11-05 | 0 | 3 |
| WARSCAR_HOSPICE_DESERTERS_1 | checking | "the deploy plan does not cover Scarlands" | 11-03..05 | 6 | - |
| MODCHECK_DONOR_ENVIRONMENTS_1 | retired | Armoury dependencies and WreckedMachines | 11-02..03 | 1 | - |
| HORRORS_RAIDING_FACTION_1 | held (proof_weak) | +AshkarrWeatherSuite | 11-05 | 0 | 1 |

There were also low-evidence retrofits, made with no failing row seen: HEADS_VERIFY_SHRUNK_TO_FIT_THE_HATS (+StarWarsPatches, 39 min after creation), SPECIES_TRAITS_OVER_APTITUDES_1 (StarWarsRaces; 2 rows read "VERDICT UNMEASURED"), OWN_PRESET_WIDEN_PYRELANDS_JOINS_IN, MASS_VALIDATION_LADDER_1 and RIVER_SITE_REBUILD_FOR_FOURTEEN_MODS.

### R2: the subject mod was not derived from the build (8 items)

`mods_of(sha)` counts only shippable files. A proof-only or harness-only build therefore derives no subject mod. A folded source (Stillsand, Wastes, WeepingStones, TheSump) belongs to the composed `RimMandrake.Biomes`, and in these cases that mod was not named.

| Item | State | Short reason | Dates | Games | Pre-fix |
|---|---|---|---|---|---|
| RAIL_WALK_PROVE_NOBODY_WALKS_OFF_ANYWAY | game | Type not found RM_FallRails; FlowWorks unnamed | 11-05 | 1 | 1 |
| GRAFFITI_NORTHSTAR_GREEN_FULL_1 | game | "Graffiti not in the running load" | 11-02..04 | 8 | 0 |
| PROOF_HARNESS_BUILD_SAVELOAD_TRIPLET | blocked | GimmeSomeSlack not in the load | 11-04 | 2 | - |
| STILLSAND_DUNE_GALE_LIVE_1 | held | RimMandrake.Biomes unnamed; the rows read MISSING / proof crashed | 11-03..05 | 0 | 3 |
| STILLSAND_SAND_SWIM_REMAINDER_1 | game | same as above | 11-03..05 | 0 | 3 |
| WASTELAND_LIVE_SUITE_FAILS_ACC_BIOMES_1 | game | same as above; "modcheck wrote no results" | 11-03..05 | 0 | 3 |
| WEEPINGSTONES_HANDLER_VANISHES_1 | game | same as above | 11-03..05 | 0 | 3 |
| SUMP_GLASSWALK_SPEED_RATIO_1 | game | RM_GreySea / RimMandrake.Biomes | 11-05 | 0 | 1 |

GSS_SLICE_FIX_EDGE_OVERSHOOTS_BUDGET and GSS_BUILD_FIX_SLICE_GROWS_WITH_CORDS are both done. Each was retrofitted with GimmeSomeSlack before it lost a game.

### R3: the name was present, but staging read a stale copy (1 item, already fixed)

WATER_DEPTH_RESKIN_HE_LOOKS_FIRST: staging read the proof file as it stood at the build sha. This was fixed in 941ec4ff05, which reads the books' current file through `_mods_text`, and in 20b6b34ba4.

### R4: a wrong name or format (5 items)

| Item | State | Short reason | Games |
|---|---|---|---|
| WATER_DEPTH_RESKIN_HE_LOOKS_FIRST | game | `RimMandrake.FlowWorks`, a packageId-looking name that matches no folder, where `FlowWorks` was meant | 0 |
| GENERATOR_MODS_PROVE_INERT_AFTER_CREATION | blocked | the line named a modlist file instead of folders (914c3b0be1) | (R6) |
| OLLOPOM_BEAUTY_VERIFY_DEPLOYED_NOT_SEEN | game | named CreatureBehaviors, a folded source, where RimMandrake.Biomes was needed | 2 (1 pre-fix) |
| OPS_CHURN_DIAGNOSE_TITANIC_WYZE_DMPL | (ops) | one rider's `RimMandrake.FlowWorks` held the whole batched load | - |
| OPS_CHURN_DIAGNOSE_OLLOPOM_JLHV_AJHK | (ops) | a dotted folder name was read as a packageId | - |

### R5: a deploy defect, not a naming problem

The symptom is "no readable packageId in deployed About.xml". It hit ART_OVERRIDE (Scarlands), HORIZON_CARAVAN_VANILLA_REFUSES_1 (done; Stillsand), OLLOPOM and TIDAL (CreatureBehaviors), and TAOZIN (EnvironmentalHazards). A naming check would not have prevented any of these. It belongs with the deploy check.

### R6: the proof needs an exact tier, or needs a mod to be absent (3 items)

| Item | State | Short reason | Games |
|---|---|---|---|
| VITALS_OVERHEAD_MEASURE_FULL_LIST_TOLL | held | WRONG_TIER: 42 mods running against the ratchet_pilot's 20..26; blocks on LANE_TIER_WIRE_A_WHOLE_LIST_LOAD | 2 |
| STILLSAND_RETURN_REMAINDER_1 | held | "DBH not loaded on this tier"; its RM-tier clause needs Utinni to be ABSENT | 2 |
| GENERATOR_MODS_PROVE_INERT_AFTER_CREATION | blocked | "reload needed: list holds 7f.alienworlds… lacks oblitus.mylittleplanet, boots.sensiblefactions" | 5 |

### R7: a fixture save records mods the list lacks (2 items)

`save.missing_mods` fired for ATMOSBASE_PROOF_FIX_UNLIT_LEAVES_DARK_LAMP (held, 2 games) and for the ASHKARR save in GENERATOR_MODS.

### R8: out of scope (about 21 items)

The existing pre-slot gate already catches these, and none of them is a naming defect:

- the item's own build was not enabled or not deployed (11 items, e.g. FLAME_STATUES_MOD_BUILD_1, BRONZIUM_DROP_1, STILLSAND_GLASS_CHAIN_REMAINDER_1);
- a stale DLL (2 items: DRAWBRIDGE_WINCH…, PIT_LIP_OCCLUDER…);
- "changed since the built commit" (8 items, e.g. CRACKEDLANDS_FULL_RENAME_1, SUMP_TAR_FIRE_NETWORK_1).

The pre-Relentless ledger (2026-09) shows the same class: BIOME_DEFNAME_MIGRATION_WAVE_1 (missing_mod), BACTA_TANK_CORE_1 and GREENTIDE_RM_MOD_BUILD_1 ("NOT enabled").

### Totals by root cause

| Cause | Items | Explicit games | Pre-fix masked games | A filing check would catch it? |
|---|---|---|---|---|
| R1 omitted external mod | 12 (+5 low-evidence) | 33 | 19 | yes, when the proof code names the mod (types, `--mod`, defNames); 3 of 12 only through dependency closure |
| R2 subject not derived | 8 (+2 caught early) | 11 | 14 | yes: script path, folded-source map, proof imports |
| R3 stale proof copy | 1 | 0 | 0 | no (already fixed in staging) |
| R4 wrong name or format | 5 | 2 | 1 | yes: name resolution is the cheapest win |
| R5 deploy defect | 5 | (shared) | - | no (deploy check) |
| R6 exact tier or absence | 3 | 9 | - | only with a new declaration (§6) |
| R7 save fixture's mods | 2 | 3 | - | yes: read the save header |
| **R1-R7** | **31 distinct** | **about 57 item-games** | **about 34** | |

Distinct cold loads that contained at least one non-PASS row from an R1-R7 item: R1 27, R2 19, R4 6, R6 5, R7 3. The union is **35 of 38**. Most loads are batched, so that is a measure of how widespread the problem is. It is not a count of lost loads (see §8).

