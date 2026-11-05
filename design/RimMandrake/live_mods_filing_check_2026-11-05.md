# Live-mods filing check: a deep design pass (2026-11-05)

Status: DESIGN ONLY. No code has changed. Owner direction (Mandrake, 2026-11-05): add a check, at filing or proof-write time, that a proof names every mod it needs, and auto-infer a missing name when the proof code reaches into a named mod. His words: "Yes. Do a deep design pass in the concept though to make sure it's well reasoned."

Review shape: this is an INCOMPLETE 3x2. Pass 1 and the re-measure were done in this seat, and the census numbers were recounted from raw data (runs.jsonl, the item store, and git history). The blind ChatGPT consult and its critique were not run in this sitting, so §9 lists the questions that a second pass should test.

Scratch evidence (a program reads it): `D:\ClaudeWork\rimmandrake\livemods_design\`, holding `slots.txt`, `runs_hits.json`, `ledger_narrow.txt`, `lp_log.txt`, `census_runs.py` and `PROGRESS.md`.

## 1 Problem

A Relentless live proof (`infrastructure/state/live_proofs/<ITEM>.txt`) declares its mods on `live-mods:` and `live-deploy:` lines. Several pieces of code read those lines:

- `relentless_live_round.live_mods()` parses them.
- `is_package()` decides whether a name is a folder or a packageId.
- `RoundFx.mods_of(sha)` adds the mods that the built commit's shippable files touch.
- `mod_gap()` compares the plan against the running load before a slot is spent.
- `batch_gap()` unions the mods of every rider in a batch.
- `relentless_game` stages the load with `modlist_swap.py --enable`.

The semantics are "the list must include these mods and may include others".

When a proof fails to name a mod it needs, nothing notices before the load. The proof then fails in game, usually as "Type not found", "MISSING …", "modcheck wrote no results" or "proof crashed". `envcause` recognises only some of those shapes, so the item cycles through game slots until a human reads the proof, adds the name by hand and the item re-queues. Repairs of this kind were landed in commits 21cff8ca92, 7d0378ef59 and 20b6b34ba4 and lesson 9cb4978ede. Each cold load on the full list takes about 15 minutes.

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

## 3 Is the concept right?

The owner's two parts were (1) a filing-time check and (2) auto-inference from the proof code. Five findings from the census contradict or reshape the premise.

1. **"Auto-infer from the build" is the wrong source.** In R2 the build derived nothing, because the build was proof-only or because the mod was a folded source. Needs have to come from the proof's own code and its fixtures, plus the item's subject. They cannot come from the diff. The owner's wording, "when proof code reaches into a named mod", was already right on this point.
2. **The failures are mostly not visible after the fact.** Seven of the 20 R1/R2 items were never classified as a mod problem. Their rows read proof_or_site, "MISSING", "proof crashed" or "modcheck wrote no results". A post-hoc inferrer built on `envcause` would miss them. That is why the check has to be static and has to run before the load.
3. **Name validity is a separate and bigger cheap win.** R4 (5 items) and part of R2 are cases where a name was written but did not resolve to a loadable folder. This needs no inference, only resolution against `folders()`, packageIds and the folded-source map. Resolution should refuse. Inference should only write or warn.
4. **"May include others" is false for some proofs.** R6 needs mods to be absent and needs an exact tier. A check of "names every mod it needs" cannot express those needs. The proof has to declare its tier (§6).
5. **R3 and R5 are not naming problems.** A filing check must not claim them. R3 is already fixed, and R5 belongs with deploy.

So part (1) is right but has to be widened to cover resolution and fixtures as well as completeness. Part (2) is right if it means inferring from the proof's code and writing only single-owner hits. It is wrong if it means inferring from the build diff or from failure text.

## 4 Alternatives considered

**A. A post-hoc inferrer.** Extend `envcause` so that a failed run names the missing mod and writes it into the proof. Rejected as the primary mechanism, for three reasons. It still spends the first game. It is blind to the 7 masked items. And a "Type not found" can come from a stale DLL (R8) as easily as from a missing mod, so writing on that signal is risky. **Kept** as a cheap secondary pass: when the text is "Type not found X" and X resolves statically to exactly one mod that is missing from the list, write that mod in.

**B. Always load the full list.** Rejected. It costs about 15 minutes against about 22 seconds per cold load. It breaks exact-tier proofs. And it hides mod interference, which is the very thing some proofs measure.

**C. Require a human-curated `live-mods` line, with dependency closure only.** Close the declared names over `About.xml` `modDependencies` and `loadAfter`/MayRequire. This catches the workshop-dependency cases (HEAVY_TEXTURES, WORLD_NULLTEX's rimthemes, MODCHECK_DONOR's Armoury dependencies). It misses R2 and all of R1 where the first name was never written. **Kept as one component** of D.

**D. A static needs resolver over the proof, run at proof-write time and again before the slot. This is the chosen design.**

**E. A dry-run quicktest on a minimal list before the slot.** Load the proof's declared list at about 22 s and check that the types resolve. Rejected for now. It still needs a game process and the bridge lock, and it duplicates what static resolution gives for nearly all of the census. It could return later, as the tie-breaker for an ambiguous result from D.

## 5 Chosen design: a needs resolver with two gates

### 5.1 What it reads

`needs(item)` returns a set of `(mod, evidence, confidence)` from six static sources, ordered by trust:

1. **Declared lines.** `live-mods:` and `live-deploy:` exactly as `live_mods()` parses them.
2. **Fixture saves** named by the proof (`*.rws`). Read their `<modIds>` / `<modNames>` header. This source is authoritative and catches R7.
3. **CLI arguments.** `--mod X`, `--mods`, and site or scenario JSON that names mods (e.g. `northstar/review/scenarios/*.json`, the modcheck `--mod` argument).
4. **Script location.** A proof or validation script under `src/<Tier>/<Mod>/…` needs `<Mod>`. A folded source maps through `modlist_swap.about()` to its composed mod, so Stillsand becomes RimMandrake.Biomes. This catches R2.
5. **Code references.** Bridge or static-call types and namespaces (`AlienWorlds.PlanetTypeManager`, `RimProperty.*`), resolved through a namespace-to-assembly-to-mod index built from deployed `Assemblies/*.dll` metadata. Also defNames with prefixes (`RM_`, `RSW_`, `RUT_`, or donor defNames), resolved through the existing def dump. Only an unambiguous single owner counts as `sure`.
6. **Dependency closure.** Over 1 to 5, using the About.xml `modDependencies` (hard) of the resolved mods. MayRequire and `loadAfter` count as `soft`.

The subject mods from `mods_of(sha)` are unioned in, as they are today.

Every name is normalised by one function, `resolve(name)`. It returns `folder | packageId | folded→composed | UNKNOWN`, uses the same rules as `is_package` (a dotted name that is a real folder counts as a folder), and prints the canonical folder. Today's `is_package` and `modlist_swap.split_names` should call this one resolver, so that the gate and staging cannot disagree.

### 5.2 Where it lives

The core is one pure module: `src/RimMandrake/rimflow/relentless_needs.py`. It is called from three places.

- **Proof-write and filing time** (`rimflow` file/proof steps, plus a `live_proofs` lint in `run_selftests`). It runs offline with no game and costs well under a second per proof. This is the owner's point (1).
- **The pre-slot gate** (`mod_gap` and `batch_gap`). It runs the same function over the books' current proof file, the one `_mods_text` reads. That catches proofs edited after filing, and batch riders.
- **Optionally, a post-fail write** (alternative A), limited to a single-owner `Type not found`.

### 5.3 What it refuses, writes, and warns

| Finding | Filing / proof-write | Pre-slot gate |
|---|---|---|
| A declared name resolves to UNKNOWN (no folder, no packageId, no folded map) | **refuse** | **refuse this rider only**: drop it from the batch, keep the load for the others (fixes the TITANIC_WYZE whole-load hold) |
| A declared name is a folded source | **rewrite** to the composed mod, and log it | rewrite |
| A `sure` need is missing (fixture save, script path, CLI `--mod`, single-owner type or defName) | **auto-write** to the `live-mods` line, with a `# auto: <evidence>` comment, and commit with the proof | auto-write into the books' copy, re-plan the batch, and record a note on the item |
| A hard `modDependencies` need is missing | auto-write | auto-write |
| A `soft` or ambiguous need (multi-owner type, MayRequire only, generic defName) | **warn** in the filing output and on the item | warn; do not block |
| A need that conflicts with a declared `live-absent:` | refuse | refuse the rider |
| The mod is needed but undeployed or stale | (out of scope: the existing deploy gate) | existing gate |

The auto-write rule needs one owner, one source of evidence named in the comment, and a name that resolves. Anything less only warns. The aim is that a false positive costs a warning line and never a held item.

### 5.4 Failure modes

| Failure mode | Effect | Mitigation |
|---|---|---|
| False negative: a need reached only through dynamic strings (reflection by name, `DefDatabase.GetNamed(var)`) | Unchanged from today: the proof fails live | Post-fail pass A |
| False positive: a defName defined by several mods (a patch in one mod, the def in another) | Enabling an extra mod only adds load time | It never auto-writes on its own; it warns |
| A stale index (dll/def dump older than the build) | Wrong owner | Key the index on the deploy fingerprint. If it is stale, auto-write degrades to warn. It must never refuse on the index alone |
| Interference: an inferred extra mod changes the behaviour a proof measures | A wrong PASS or FAIL | A proof that is sensitive to extras declares `live-tier: exact` (§6), and the resolver then never writes; it only refuses or warns |
| Books and build copies disagree | R3 again | Read the books' copy only, the same source staging reads |

## 6 Exact-tier proofs (LANE_TIER_WIRE_A_WHOLE_LIST_LOAD)

"Must include, may include others" is kept as the default. The design adds two optional declarations:

- `live-tier: <name>` (for example `ratchet_pilot`, `full`, `rm`). The list is that tier's modlist, plus the declared and `sure` needs. The resolver then checks that every need is either in the tier or explicitly added. An added need that turns the tier into something else is refused: under `live-tier: exact <name>` no additions are allowed at all. VITALS (WRONG_TIER, 42 running against 20..26) and GENERATOR_MODS (a modlist name written into the mods line) become declarations instead of failures.
- `live-absent: <mods>`. These mods must not be loaded. Staging already only enables. The staging side of absence belongs to LANE_TIER_WIRE_A_WHOLE_LIST_LOAD, which owns whole-list swaps. Until that work lands, the gate refuses a rider whose `live-absent` holds a mod in the planned load, and holds the rider before the slot instead of after it (STILLSAND_RETURN_REMAINDER_1, which needs Utinni absent).

The resolver never auto-writes into an exact-tier proof. Batching puts exact-tier riders on a load of their own, because they cannot be unioned. `batch_gap` must partition by tier before it unions.

## 7 Verification plan

### 7.1 Selftests (offline, under `run_selftests.py --only relentless_needs`)

- Resolve: `FlowWorks` gives a folder, `RimMandrake.Biomes` gives a folder (it is dotted), `mandrake.rm.biomes` gives a packageId, `CreatureBehaviors` and `Stillsand` give RimMandrake.Biomes (folded), and `RimMandrake.FlowWorks` gives UNKNOWN.
- Source fixtures, one per source. A proof script under `src/RimMandrake/Stillsand/` needs RimMandrake.Biomes. A `.rws` fixture header gives its modIds. A proof calling `AlienWorlds.PlanetTypeManager` resolves to 7f.alienworlds through a stub assembly index.
- Policy: a `sure` need is auto-written with an evidence comment, an ambiguous one warns, an UNKNOWN refuses, `live-tier: exact` never writes, and a `live-absent` conflict refuses.
- Batch: an UNKNOWN on one rider drops that rider only, and two tiers split into two loads.
- Instrument check: on a proof that is already complete, the resolver reports zero missing **and** at least one need found by each source it claims to read. A zero produced by a blind index fails the test.

### 7.2 Historical replay

Check out each item's proof file as it stood **before** its repair commit (from `lp_log.txt`), run `needs()` offline, and compare the result with the names the human later added.

| Item | Expected hit | Source | Action |
|---|---|---|---|
| TIDAL_LOCK_FIX_PRESET_NAME_WAS_MISSING | 7f.alienworlds | code type | auto-write |
| SETTLEMENT_VERBS_WAVE_1 | RimProperty | code type / namespace | auto-write |
| GRAVSHIP_PEACEFUL_SETTLEMENT_LANDING_1 | KeelHoist, UtinniPatches | defNames / MayRequire | KeelHoist auto-write, Utinni warn |
| ART_OVERRIDE_FAMILY_SCRIPT_1 | Webwork, Scarlands, sarg.alphamemes, VE genetics | donor defNames in the override script | auto-write the single-owner ones, warn on the rest |
| TAOZIN_SPLIT_BUILD_ONE_WORM_BECOMES_TWO | EnvironmentalHazards, RimMandrake.Biomes | defNames / folded | auto-write |
| TITANIC_BODYSIZE_TEST_RACE_1 | HugeThingsTestRaces, neku.largepawns | defNames, dependency closure | auto-write |
| WORLD_NULLTEX_FLOOD_HUNT_STACKLESS_SO_FAR | arandomkiwi.rimthemes, NullTexTrace | closure of MenuShell; script path | auto-write |
| HEAVY_TEXTURES_MEASURE_REAL_VRAM | its workshop dependencies | closure | auto-write |
| MODCHECK_DONOR_ENVIRONMENTS_1 | Armoury dependencies, WreckedMachines | closure, `--mod` | auto-write |
| HORRORS_RAIDING_FACTION_1 | AshkarrWeatherSuite | defName (weather) | auto-write or warn |
| RAIL_WALK_PROVE_NOBODY_WALKS_OFF_ANYWAY | FlowWorks | code type RM_FallRails | auto-write |
| GRAFFITI_NORTHSTAR_GREEN_FULL_1 | Graffiti | scenario JSON / `--mod` | auto-write |
| PROOF_HARNESS_BUILD_SAVELOAD_TRIPLET, GSS_* | GimmeSomeSlack | script path / CLI | auto-write |
| STILLSAND_DUNE_GALE, STILLSAND_SAND_SWIM, WASTELAND_LIVE_SUITE, WEEPINGSTONES_HANDLER, SUMP_GLASSWALK | RimMandrake.Biomes | script path + folded map | auto-write |
| OLLOPOM_BEAUTY_VERIFY_DEPLOYED_NOT_SEEN | CreatureBehaviors → RimMandrake.Biomes | resolve | rewrite |
| WATER_DEPTH_RESKIN_HE_LOOKS_FIRST | `RimMandrake.FlowWorks` | resolve | refuse |
| GENERATOR_MODS_PROVE_INERT_AFTER_CREATION | modlist name in the mods line | resolve, then `live-tier` | refuse, with a message pointing to `live-tier:` |
| ATMOSBASE_PROOF_FIX_UNLIT_LEAVES_DARK_LAMP | the save's modIds | fixture | auto-write |
| VITALS, STILLSAND_RETURN | (no hit) | needs a declaration | refuse until `live-tier` / `live-absent` |

Pass bars:

- At least 17 of the 20 R1/R2 items are hit before repair, with the right mod.
- All 5 R4 items are refused or rewritten.
- There are zero auto-writes of a wrong mod across the replay.
- A negative control finds zero `sure` additions across the 25 newer proofs that were complete at creation (`NEW` rows in `slots.txt`), and any warnings are listed.

WARSCAR_HOSPICE_DESERTERS_1 and CANON_MATERIALS_BUILD_1 are deploy-plan or running-load cases. They are replayed against the pre-slot gate, not the filing gate.

## 8 Cost and benefit in game slots

**The cost being removed.** R1, R2, R4 and R7 together show about 49 item-games with an explicit mod-list cause, plus about 34 masked non-PASS item-games before the repair, of which some had other causes as well. Most loads are batched. A rider's failure costs its share of a load (about 15 min on the full list) and its re-queue, and it holds the whole load only when the gate refuses that load (the TITANIC_WYZE case). Charging each item-game as a share across the 35 affected loads gives a working figure of about 10 to 15 load-equivalents (about 2.5 to 4 hours of game time) over 3.5 days, plus 20 hand repairs at roughly 10 to 30 agent-minutes each. This figure is an estimate. The item-game counts are measured, but the share per load is assumed.

**The expected saving.** If the replay meets its pass bar (17 of 20 and 5 of 5), the filing gate removes about 85% of that cost. The remaining residue is dynamic references, which alternative A can take after one game.

**The build cost.** One module of about 300 to 400 lines plus selftests, and an assembly-namespace index rebuilt with each deploy. Adding the check to filing costs less than a second per proof. There is no game cost.

**The cost of false positives.** An extra enabled mod adds load time (seconds to a minute on a minimal list) and risks interference only for proofs that would be expected to declare `live-tier: exact`.

## 9 Open questions

1. Is `live-tier:` / `live-absent:` acceptable as a proof-file declaration, or should the tier live on the rimflow item? This is the boundary with LANE_TIER_WIRE_A_WHOLE_LIST_LOAD, which should own whichever is chosen.
2. Auto-write at filing commits a change to the proof file. Should the human or agent filing it see a diff first, or is the `# auto:` evidence comment enough? The recommendation is the comment, plus a line in the filing output.
3. Should the namespace index come from deployed DLLs (current, but needs a deploy) or from the repo's `.csproj`/source (always available, but misses workshop mods)? The recommendation is the deployed DLLs, with workshop folders included.
4. Should the post-fail write (A) ship in v1 or wait for the replay residue? The recommendation is to wait.
5. The second-model pass (ChatGPT, blind then critique) was not run in this sitting. It should test whether the namespace-to-mod index is reliable enough to auto-write on (false-positive risk), and whether `live-absent` belongs here or in the tier lane.
