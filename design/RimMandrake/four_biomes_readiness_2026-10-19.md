# Four biomes readiness: Pyrelands, Leaning Scrub, Cauldron, Contagion (2026-10-19, offline)

The owner asked to *"ensure the four biomes are mature and ready"*. He then corrected which four:
**Pyrelands, Leaning Scrub (`RM_LeaningScrub`, with its world-carrier twin `RUT_AridShrubland`),
Cauldron and Contagion.** This audit was done offline only: no game, no bridge, no `--apply`.
Everything that needs the game is in the run-sheet at the end.

Verdicts: **PASS** (measured and holds), **FAIL** (measured and does not hold), **UNMEASURED** (no
instrument run). Every count below comes from a parse or a tool, never a grep count. Tile counts
are not used: they are not evidence, because the planet is painted once at the end.

## The table

| check · how measured | Pyrelands | Leaning Scrub | Cauldron | Contagion |
|---|---|---|---|---|
| **BiomeDef complete**: parsed with `xml.etree`. Checked `animalDensity`, `plantDensity`, `workerClass`, and that `wildAnimals`/`wildPlants` are element-form | PASS: aD 2.1, 9 animals and 2 plants on the def | PASS: aD 1.8, 19 animals and 30 plants. Twin `RUT_AridShrubland` aD 1.8, 40 and 10 | PASS: aD 0.8, 15 and 16 | PASS: aD 3.0, 23 and 13 |
| **Patch-added roster**: `UtinniPatches/Patches/WildAnimals_<Biome>.xml` parsed. Xpath targets the RM_ def, the add is guarded by FindMod/Conditional, and every added kind has a PawnKindDef | PASS: 7 added | PASS: 38 added | PASS: 7 added | PASS: there is no patch, and none is needed because the roster has no RSW_ rows |
| **Every roster row has a def**: all `src/**/*.xml` parsed into (tag, defName). Animals need ThingDef + PawnKindDef, plants need ThingDef. Sanity probe: `RM_Reefback` was found | PASS | PASS (`Plant_Brambles` is vanilla Core) | PASS for ours. The 2 `AM_Dryad_*` rows are Alpha Memes kinds behind `MayRequire="sarg.alphamemes"` | PASS |
| **Art**: `biome_census.py` followed by `texture_regen_audit.py`. Roster rows classed by the ledger SHA | PASS by ruling (*"Biome art never blocks"*, 2026-10-18): 11 REGEN, 7 UNPROVEN | PASS by ruling: 66 REGEN, 5 UNPROVEN, 13 DONOR (mostly RSW twins), 4 PLACEHOLDER. The 4 PLACEHOLDERs are RSW plants that share `Things/Plants/AB_Aaklac` | PASS by ruling: 31 REGEN, 4 UNPROVEN, 3 DONOR | PASS by ruling: 35 REGEN, 1 DONOR (`RM_RustPuff`) |
| **World-map texture**: the `texture` path resolves to a PNG in the mod | PASS | PASS | PASS | PASS |
| **Donor references**: `donor_retire_census.py refs --json`, filtered to the four mods | PASS after this audit's fix (see below) | PASS: 0 rows | FAIL (minor): `sarg.alphamemes` sits in About `loadAfter` and on 2 roster rows, and `vanillaexpanded.vgeneticse` in `loadAfter`. Neither mod is in `retired_mods.json` yet, and evictions are stopped, so these were left alone | PASS: 0 rows |
| **Mod Settings**: `settings_audit.py` | PASS: OK, masters declared | PASS: OK. Note (6): the master switch cannot grey its dependents, filed as `SCRUB_SETTINGS_WIRE_MASTER_CANNOT_GREY` | PASS: OK | PASS: OK |
| **Selftests**: `run_selftests.py --only` with 20 files (mod-local plus `Utils/selftest_<mod>_{fuzz,lint}.py`) | PASS 4/4 after the fix (it was FAIL 1/4, see below) | PASS 5/5 | PASS 5/5 | PASS 6/6 |
| **Functional script exists** (`<Mod>/validation.py`) | PASS | PASS | PASS | PASS |
| **North-star bars**: `modcheck floor --all` | PASS: VALIDATED, 20/20 bars, *bar met* | FAIL: DRAFT, 0 bars (the owner validates the bars) | FAIL: DRAFT, 0 bars | FAIL: DRAFT, 0 bars |
| **DLL matches its source**: `dll_source_stamp.py check` | PASS: MATCH (FireEcologyHook, and PyrelandsMechanics in RimUtinni) | PASS: MATCH | PASS: MATCH | PASS: MATCH |
| **Code review**: `code_review_status.py check` on every tracked `.cs`/`.py`/`.xml` in the mod (re-measured 2026-10-22) | 85 CLEAN / 1 DIRTY (`selftest_pyrelands_site.py`, edited in review) | 95 CLEAN / 0 DIRTY | 66 CLEAN / 0 DIRTY | 96 CLEAN / 1 DIRTY (`validation.py`, edited in review) |
| **Deployed = repo**: `deploy_custom_mods.py --compose biomes` dry run | FAIL: drift (world texture) | FAIL: drift (BiomeDef, plants, races, 2 patches, textures) | FAIL: drift (BiomeDef, races, textures) | FAIL: drift (defs, textures) |
| **Direct Sun**: no per-biome heat kind is owed (owner, 2026-10-19: *"no biome-specific heat, no biome-specific sun"*) | n/a | n/a | n/a | n/a: `CONTAGION_HEAT_JUDGE_SUN_KIND_UNSAID` superseded by `DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES` |
| **No vanishing without a sign**: read every `Destroy`/`DeSpawn` on a pawn in the mod's C# | PASS: none on pawns | PASS: only inside proof cleanup | PASS: none | PASS: the Coalescence absorbs only wild members of its own unfinished kind, with a dust puff and a growth message |

## Fixed tonight

- **`src/RimMandrake/Pyrelands/selftest_pyrelands_site.py` had passed before and failed tonight.**
  The two states:
  - Before: the test asserted that *"alphabiomes NOT excluded (hard dep of mandrake.rm.biomes)"*,
    and its fake install made `mandrake.rm.biomes` depend on `sarg.alphabiomes`.
  - After `76415b816`: the owner retired Alpha Biomes on 2026-10-18 (`retired_mods.json`), so
    `resolve_tier` correctly refused that invented dependency.
  - A parse of every composed entry's About.xml shows that none depends on `sarg.alphabiomes` now.
    The test's picture of the install was stale, not the code.
  - The fix drops the invented dependency and replaces the stale assertion with two real ones:
    `alphabiomes` is a retired donor, and the tier refuses it if a dependency pulls it back.
  - The stale comment in `src/RimMandrake/Utils/modset_builder.py` that claimed the hard
    dependency is corrected. Commit `2f7f5c6ec`.

## Not fixed offline

- **Northstar bars** for Leaning Scrub, Cauldron and Contagion. Agents write and approve the
  scripts, but the hash-bound bars are the owner's. The scripts exist (`validation.py`).
- **Code review**: done 2026-10-22 (FOUNDRY helper, full-file reviews of every DIRTY `.cs`/`.py`/`.xml`): two
  files stay DIRTY because the review itself edited them (see the table).
- **Art**: accepted as-is by the 2026-10-18 ruling. The non-REGEN rows above are a record, not a
  blocker. RSW twin re-art is `CANON_CREATURE_REGEN_1`.

## Morning run-sheet (live). Bridge holder, game down first where marked

1. **Game down:** run `deploy_custom_mods.py --compose biomes`, read the plan, then `--apply`. Two
   things to check before applying: the dry run shows 134 drift lines overall, and 2 TheSump `-`
   lines that are in the game but not in the repo. Check the latter against the morning deploy plan
   (`b63be5870`) before deciding on `--prune` or `--pull`. This deploy must land before any row
   below can mean anything.
2. **Pyrelands:** `PYRELANDS_GREEN_MINIMAL_1`, then `PYRELANDS_GREEN_FULL_1` (fresh full-list
   mapgen on a scratch save). FireHawk flight is **owner-present only**: it is the last open line of
   `PYRELANDS_SHIP_READINESS_1`.
3. **Leaning Scrub:** `LEANING_SCRUB_SITE_BUILD_LEANS_ONE_WAY` (saved site), then
   `LEANING_SCRUB_FIRST_SCRIPT_1`, `LEANINGSCRUB_ENRICHMENT_QUICKTEST_1`,
   `LEANINGSCRUB_SWEETLINE_VISITORS_1`, `LEANINGSCRUB_VISSLER_ARM_SCAVENGERS_1`, and unblock
   `LEANINGSCRUB_MECHANICS_BUILD_1`. `LEANINGSCRUB_VENOMVINE_SITTING_1` is a sitting with the owner.
4. **Cauldron:** `CAULDRON_YIELD_LIVE_RERUN_1`, `CAULDRON_ENRICHMENT_LIVE_PROOF_1`,
   `CAULDRON_ENRICHMENT_VISUALS_1`, `CAULDRON_VENT_ENRICHMENT_HOOKS_1`, then unblock
   `CAULDRON_MECHANICS_BUILD_1`.
5. **Contagion:** `CONTAGION_SITE_BUILD_SKY_STAYS_CALM` (saved site), then
   `CONTAGION_ARMS_UNTANGLE_SITE_ALREADY_SICK`, `CONTAGION_FIRST_SCRIPT_1`,
   `CONTAGION_RULED_CONTENT_1`, then unblock `CONTAGION_MECHANICS_BUILD_1`.
6. **Owner:** validate the north-star bars for Leaning Scrub, Cauldron and Contagion once their
   runs are green (`modcheck floor --all` then reads VALIDATED).

## Bonus: terminal biomes (first, mistaken reading of "the four")

Before the correction, the audit started on the TerminalBiomes mod: `RM_TheScald`, `RM_TheChill`
(the former Propane Lake), `RM_TwilightSea` and `RM_GreySea`, plus `RM_ChillCrater`, the event-only
aftermath biome. What was measured:

- Every `wildAnimals`/`wildPlants` row and every `fishTypes` catch on all five defs has its def.
  The rare-catch makers exist too.
- `animalDensity` is set on the four seas. On `RM_ChillCrater` it is 0, which is deliberate: the
  header says it is placed only by the in-game event.
- The terminal, sea-shore and diving selftests ran 9/9 PASS. That includes
  `selftest_sea_catch_alive.py` (fishables alive in the depths) and `selftest_sea_floor_no_rain.py`.
- The art, donor, settings and live checks for this set were not run. They are UNMEASURED.
