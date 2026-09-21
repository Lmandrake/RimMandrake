# BENCH queue decay sweep — evidence only, no rulings

Scope: the 46 PROPOSED items rimflow offers `next --seat BENCH`, minus the 4
items excluded as actively-worked (DESERT_FAMILY_PORT_EXECUTION_1,
TITANOSLIME_SLIME_BIOME_1, BIOME_PAINT_ONCE_AT_THE_END_1,
BRIDGE_SELECT_NONCOLONIST_PAWN_1). 44 items evaluated below.

Status: COMPLETE — all 44 items evaluated.

## DONE

### ECOSYSTEM_PYRAMID_LAW_1
Owner ruled the threshold 50% small-fauna-by-commonality (item file, "## ruling — owner, 2026-09-20", verbatim "50% small"). All 9 failing biome rosters lifted above 50% by wiring/boosting already-ruled small fauna, committed at `2e8eda9db`... actual hash `2e8eda9da` ("ECOSYSTEM_PYRAMID_LAW_1: lift 9 biome rosters to the owner's ruled 50% small-fauna floor"), `validate_patch.py` 0 errors/0 warnings on all 9, deployed via `deploy_custom_mods.py --mod UtinniPatches --apply`, and `infrastructure/state/canon.yml` carries the law under `ecosystem_laws.food_pyramid`. Ledger still shows `state: proposed` (never closed against the ledger) — a rimflow bookkeeping gap, not undone work. **Residual, genuinely still owed**: a measure-backed/selftested checker (item names this itself, `checker_owed` in canon.yml) and live in-game verification (XML-only pass, no restart yet).

### ENVHAZARDS_NEVER_ACTIVATED_1
Item filed at `785100e16` naming the never-activated defect; the very next relevant commit `9bf9ccf4e` "Activate mandrake.rm.environmentalhazards in both mod lists (owner: 'Yes, both lists')" resolved it. `ModsConfig.FULL.LATEST.xml` (618 mods, most recent full snapshot per its own git history at `d38274fb3`/`afb08ef4f`) contains `mandrake.rm.environmentalhazards` (confirmed via `ET.parse`). Decided and applied.

### PYRELANDS_DENSITY_TRIPLE_1
Commit `1d55fa45d` "Pyrelands: plantDensity 3.0 + enforcer that beats the startup rewriter" built `src/RimMandrake/Pyrelands/Source/RM_PyrelandsDensityEnforcer.cs`; commit `ee05d75b6` records "density readback PASS 3.0" — the live verification the item asked for already happened.

### FOUNDERS_EXPORT_TO_REPO_1
Commit `ee8b70911` "the founders now have a repo copy": 6 Jawa colonists + 2 named colony animals extracted as raw Scribe XML against the 617-mod list. Main ask (get the founders into the repo) done. Residual per the commit's own message: "The round-trip re-import is NOT yet proven — README says so."

### STALE_VIVIFIED_WORLDMAP_CITED_1 — see STILL LIVE below (partial fix only).

### DEEPS_FAUNA_MECHANICS_2
Despite being filed as its own BENCH item (because the commit hook refuses a BENCH edit to FOUNDRY-owned `DEEPS_FAUNA_MECHANICS_1`'s file, per the item's own text), the actual code landed 30 minutes after the base build, still tagged with the `_1` name in its commit message: `fad263d00` "DEEPS_FAUNA_MECHANICS_1: grabber hold-and-crush, soulchime stun/soothe, drinker fluid sacks + iron poisoning (C#, built, not deployed)", followed by `d0c11a0f2` "...DEEPS_FAUNA_MECHANICS_2...". All three named mechanics are present in code: grabber crush/rescue on `PostPostApplyDamage` (`RM_CompGrappler.cs`), soulchime LoS trigger + psychic-deaf immunity (`RM_CompProximityPsychicStun.cs:89,93`), drinker fluid-sack gauge + drained-fluids-on-death + hydrocarbon-blood flag (`RM_CompFluidSacs.cs:81,107,133`). Residual: commit message says "not deployed" — deploy/live-verify still owed, matches the item's own `needs: bridge`.

### READ_LINE_REGISTRY_SHARED_1
Commit `556403f99` ("READ_LINE_REGISTRY_SHARED_1: shared read-line ids get a registry and a lint"), dated 2026-09-20 16:37, same-session as this sweep. Built `design/validation_walks/_read_line_registry.md`, `modcheck/readline_registry.py` wired into `modcheck lint`, `DANGLING_CITATION` failure class, covered by `modcheck/selftest_readline_registry.py`. Verified before commit: `floor --all` byte-for-byte unchanged (FlowWorks 13, Graffiti 8, Pits 11 still VALIDATED — proving the shared-line re-hash risk the item warned about didn't fire), `run_selftests` 67/67. Ledger still shows `state: proposed` — same bookkeeping gap as above, not a sign the work is undone.

## INVALIDATED

None found. No item in this batch was contradicted by a later owner ruling.

## SUPERSEDED

None found. No newer item was found covering any of these 44 wholesale (several are correctly sequenced AFTER each other — e.g. `NARRATIVE_DICTIONARY_PILOT_1` before `EVENT_TRACE_PROPS_LIBRARY_1` — which is scheduling, not supersession).

## STILL LIVE

### CANON_DRAIN_1
Total canon drain, gated on "biome-cast wave settled" (fauna round-2 sittings done + flora ruled). CLAUDE.md and the live queue show biome work (DESERT_FAMILY_PORT_EXECUTION_1, BIOME_MOD_SPLIT_EXECUTION_1, DONOR_DEFS_PORT_TO_OURS_1 etc.) still actively mid-flight 2026-09-20 — gate plainly unmet, not stale, just not due yet.

### BACTA_REVIVAL_MECHANIC_1
`src/RimStarWars/Bacta/Source/BactaMod.cs:31,50,125` defines a `revivalEnabled` Settings checkbox ("Revive the recently dead") but it is a dead field — `grep -rln revivalEnabled src/RimStarWars/Bacta/Source/` hits only `BactaMod.cs`, never `CompBactaImmersion.cs`. That comp's only Dead check (`CompBactaImmersion.cs:174`, `if (pawn.health == null || pawn.Dead)`) is a bail-out guard, not a revival path. No `Resurrect`/corpse-freshness code anywhere in Bacta source. Mechanic unbuilt; only a settings stub exists.

### BACTA_TANK_ART_1
`src/RimStarWars/Bacta/Textures/Things/Building/Bacta/PLACEHOLDER.md` (committed, present) states outright: "Every PNG in this folder was generated procedurally (PIL)... None of it is finished art... replace under BACTA_TANK_ART_1." The 6 tank/shell PNGs and the item PNG (`RSW_Bacta.png`) are all placeholders, not the ESB-canon art the item asks for. No visible-pawn overlay art, no droid sprite, no patch/spray icons found.

### BACTA_SIDE_ITEMS_1
`src/RimStarWars/Bacta/Defs/ThingDefs_Buildings/RSW_BactaTank.xml:108` comment: "The facility hook BACTA_SIDE_ITEMS_1 needs: the 2-1B-style medical droid will be..." — a hook is stubbed but no droid ThingDef/PawnKindDef, no bacta patch/spray ThingDefs, and no trader-tag wiring were found anywhere under `src/RimStarWars/Bacta`. Undone.

### ARTPIPE_FACING_COHERENCE_1
Item's own file documents partial completion, dated same-day: the per-facing prompt stamp existed since 2026-09-14 (`artpiped.build_job_prompt()`), and "SHIPPED 2026-09-20" section says `common.load_job()` now refuses a job whose prompt contradicts the facing stamp, covered by a named test and live-queue-verified. But the item's own "⚠️ Still open" line lists 3 remaining pieces: facings derived from ONE master prompt vs 3 independent ones, a validator that catches a `_north` reading as a side-profile clone, and burning down the installed backlog. Not done — meaningfully advanced today.

### RAKATAN_ARCHOTECH_MACHINES_1
Item file states outright: "nothing here is built or ruled yet beyond the archotech equivalence he stated outright" (owner spoke 2026-09-15, recorded for a later design session). No further commits or design docs found. Real, undone, waiting on a design sitting.

### DROID_CANON_LIBRARY_1
`design/RimStarWars/canon_references/DROIDS_INDEX.md` (1757 rows) is built and QA'd, and the owner explicitly ruled the `era` column complete at 2.7% coverage (owner, 2026-09-15) — that sub-part is DONE, not stale. But the item also asks for chassis entries: `find design/RimStarWars/canon_references -iname "droid_*" | wc -l` = **23**, against 25 distinct chassis the item names as ruled scope. 2 chassis entries still owed; item's own "## Droid findings so far" section lists unresolved index errors (wrong canon-droid mappings, continuity flags). Not fully done.

### NORTH_STAR_PIT_PILOT_1
Draft `## north star` section exists in `design/validation_walks/RimMandrake/Pits.md` (12 must-show lines, 1 cannot-show) but is DRAFT, binding nothing, and needs owner validation + wiring `shows=` into `Pits/validation.py`. Confirmed still true: `find . -iname validation.py | xargs grep -l "shows="` returns **zero files** — matches CLAUDE.md's 2026-09-17 measurement that `shows=` appears in 0 of 54 `validation.py` files. Still the falsification test that has never run.

### READ_LINE_REGISTRY_SHARED_1 — see DONE section, listed there instead.

### REACTIVE_SHIP_LIGHTING_1
No item file. `git log --grep="reactive.*light\|ship.lighting\|mood.lighting"` finds only commits about the AtmosphericBase validation-walk north-star process (`c1e67088b`, `5a2798ef7`, `4c8075f65`, `76c910258`, `353f59404`), not about building an actual reactive-lighting mod/mechanic. No `*reactive*light*` files anywhere in the repo. The underlying gap this item names (no mod owns reactive/mood lighting) is still real as far as this sweep can tell — genuinely undone design work, needs an owner sitting per its own `needs: owner`.

### NORTHSTAR_MOTION_FRAMES_1
Correctly deferred, not stale: item's own text quotes the owner's 2026-09-17 ruling to stop chasing this until live play, and says explicitly "Do not close this as stale on that basis; it is deferred by his word, not doubted." Waits on `NORTH_STAR_ATMOSPHERIC_TBD_1` (also proposed, also correctly parked — see below).

### NORTH_STAR_ATMOSPHERIC_TBD_1
No item file (content lives entirely in the queue-rendered summary), which itself quotes the owner: "please stop the north star definition here and file it as TBD... until we can play with it live first." Correctly parked pending live play; not stale, not blocking anything wrongly.

### UNSUBSTANTIATED_SPECIES_ABILITIES_1
Item file states the reverse-audit "has not looked that way yet, so the size is UNMEASURED" — explicitly nothing done. Owner asked for it 2026-09-17. Still open, no later item or commit found doing this audit.

### XENOTYPE_CANON_CORRECTION_1
Item file: "Nothing has been fixed... The owner has not ruled on any of this." Patterns catalogued (wrong-species namers, borrowed heads, etc.) from ~60 species entries, but fixes require generator changes (`gen_races_mod.py`) and an owner ruling on bug-vs-deliberate that hasn't happened. Undone.

### NARRATIVE_DICTIONARY_PILOT_1
Design doc (`design/RimMandrake/narrative_dictionary_design.md`) and implementation plan (`design/RimMandrake/narrative_dictionary_pilot_plan.md`) committed (`8ff4bd8a5` design approved/pilot filed; `86308d312` implementation plan for batch 1). But the plan's own named deliverables do not exist on disk: `src/RimMandrake/Utils/narrative/` and `infrastructure/state/narrative/` are both absent (`find` returns "No such file or directory" for both). Planned, not built.

### PIT_SUPERDEEP_COLLAPSE_1
CLAUDE.md itself (project instructions) states "Ruled and fully specified, **nothing built**" for this exact item. Confirmed: `Building_OpenPit.cs` (`src/RimMandrake/FlowWorks/Source/Pits/Holding/`, last touched `cade628c1`, FlowWorks Phase 1) and `Building_SuperdeepPit.cs`/`RM_SuperdeepCapture.cs` (`.../Source/Superdeep/`, last touched `52e312a15`, FlowWorks Phase 5) both predate the 2026-09-17 collapse ruling this item records — they are the OLD parallel-depth-ladder implementation the item explicitly wants replaced, not evidence the ruling was applied. No commit citing this item ID touches code. Undone.

### FLOWWORKS_DOOR_FAMILY_1
`find src/RimMandrake/FlowWorks -iname "*door*"` returns nothing. No Sluice or SecurityGrateDoor ThingDef/C# exists anywhere in the repo. Undone, exactly as filed.

### DEEPS_FAUNA_REPOPULATION_1
Commit `504ead829` "DEEPS_FAUNA_REPOPULATION_1: 12 alien hydrocarbon life-form proposals for the Lantern Deeps (owner picks pending)" — the proposal portfolio the item asks for exists, but "owner picks pending" in the commit's own message and no later commit found ruling on the picks. Half-done: portfolio built, decision still owed.

### REBOOT_BREAKGLASS_VERIFY_1
Filed `d1b980bf9` 2026-09-19 as the one open follow-up from the Layer 3 remote-control build. `claude-remote-control` skill's `references/incident-log.md` (read to 2026-09-19 entries) documents logins, SSH break-glass, and account-switching tests, but no entry recording an actual Windows reboot test. Item's own text: "waits on... whether it survives the one event that will happen while the owner is away," to be done "at the desk, on a day when losing the fleet for ten minutes is fine" — that day has not been logged. Undone.

### EVENT_TRACE_PROPS_LIBRARY_1
No item file. Item is explicitly scoped by "the gap ledger from NARRATIVE_DICTIONARY_PILOT_1" (i.e. its `GAPS.md`), which per the check above does not exist yet. Correctly un-started, not stale — properly sequenced after the pilot.

### VANILLA_XENOTYPE_REMOVAL_ASSESSMENT_1
Assessment done (FOUNDRY, def dump 621 mods, 2026-09-19): the wiring is nearly uniform, most non-SW xenotypes ride generic faction xenotype sets. Item's own "## What needs him" section is a single un-ruled binary (cut vs. stop-spawning) — no commit found ruling it. Assessment complete; the decision itself is still owed.

### GRASSLANDS_TILES_CSV_STALE_1
Real, unresolved disagreement: `world/ASHKARR_WORLDMAP_tiles.csv` says `ZBiome_Grasslands` carries 222 tiles / `RM_FE_Pyrelands` carries 0, the exact reverse of what the closed item `GRASSLANDS_CAST_DEAD_BIOME_1` measured live. Item's own "## verify" section names the fix (a fresh live `jawa/world_tile_export` diffed against the CSV) and explicitly was not run this pass ("game is up under constraints that forbid driving the bridge for this task"). Not yet resolved; this is a correctly-filed bug about a real CSV/live divergence, not an instance of the zero-tiles-is-expected trap (six cast animals' actual wired biome is at stake).

### BAZAAR_STOLEN_GOODS_PROPERTY_1
Item states it is "RULED IN PRINCIPLE" (owner, 2026-09-20, called it "worth its own awesome design pass to expand") and "owes a full design pass before any build." No design pass commit found. Undone, correctly gated on design work.

### FALLZONE_LOST_CARGO_QUESTS_1
Item states explicitly: "A lead the owner asked to be recorded, not a commitment." No further design or build work found. Correctly parked as a recorded lead, not stale.

### WORLD_REMAKE_FINAL_STEP_1
Deliberately thin by design — item text: "Unwritten on purpose — the remake procedure is authored when the gates above are [met]." Matches the owner's verbatim 2026-09-20 ruling quoted in the item and in CLAUDE.md's "World remake is the last step" note. Correctly waiting on the biome-mod-split + donor-retirement gates, not stale.

### LIVE_ITEM_GLOB_DRIFT_1
MEASURED 2026-09-20: 181 prose files in `items/`, 24 closed-in-ledger-but-not-moved, 8 with no ledger row. Re-measured now: `find infrastructure/state/items -maxdepth 1 -name "*.md" | wc -l` = **219** (grown since, as expected — new items keep filing). No selftest for this found in a grep of `run_selftests.py`-adjacent checks. Real, growing drift; the item's own "Watch out" section is careful (don't hand-edit ledger, don't bulk-delete) — still needs the triage pass and the selftest it names.

### SPECIES_TRAITS_OVER_APTITUDES_1
Owner's open question ("should we... make better traits... than pluses to skills"), filed 2026-09-20 same sitting as six aptitude corrections. No design response or ruling found. Undone, waiting on a design sitting.

### BLUE_DESERT_LIFE_AUTHORING_1
Filed today (`81ba664fe`) from the owner spotting the gap live. `RUT_BlueDesert`'s own def comment confirms zero fauna/zero flora is a gap ("nothing to scale until Swallowers/Burners/Pickers... exist"), matching the item. No build commit found since filing. Real, undone; item itself gates the build behind a design pass first.

### SLIME_GENE_ARCHIVE_BUILD_1
Filed today (`e66284154`). MEASURED: `src/RimMandrake/GelatinousSlime/Defs/GeneDefs/SlimeGenes.xml` contains exactly 1 GeneDef against a 33-target+25-rider owner-accepted list frozen 2026-09-06. No further build commit found. Real, undone — the biome's headline mechanic is placeholder.

### ROT_ROSTER_DEAD_DONOR_NAMES_1
Filed today (`1c903a07c`), explicitly correcting an earlier wrong reconciliation-agent finding ("18 unwired fauna" was backwards — those 17 names are `BMT_*` Biomes!Caverns donor defs not in the active mod list, so they can never spawn regardless of wiring). Needs re-ruling (port or drop), not a wiring fix. No follow-up commit found. Undone.

### DONOR_DEFS_PORT_TO_OURS_1
Filed `85c8d3b22`. Partial progress since: `78b63a979` "census the 66 live donor/port label twins" — a census step done. But the item's own text explicitly forbids starting the actual 300-def port without a plan and an owner sitting ("⛔ Do not start porting 300 defs"), and no such sitting/plan commit was found. STILL LIVE — scoping step done, the port itself not started.

### NONCANON_BEAST_RENAME_1
Filed `85c8d3b22` same sitting as the item above. Substantial progress: `32ecbc8cb` "owner ruled batch 2 - apply all 22 renames" and `e00545d73` record it on disk — batch 2 (16 desert fauna + 7 flora renames, drafted pseudo-Star-Wars names) is drafted/ruled for the DesertPort scope. But the item's own scope is "every non-canon beast" surviving the donor port project-wide, and batch 1 (23 English-compound names) was explicitly **rejected** by the owner per the item's own text ("Batch 1 is the rejected one... still live in `src/RimStarWars/SWBestiary/Defs/DesertPort/`"). STILL LIVE — desert batch 2 ruled/drafted, not yet wired into defs (label+description rewiring is listed as "## On acceptance", future work), and the rest of the roster (non-desert biomes) untouched.

### BIOME_ROSTER_DEAD_SPECIES_REFS_1
Filed today (`ca49354b3`/`4b647e35a`), from the owner's live worry about stripped creatures. Confirms Krayt dragons are fine but finds "23 species entries across 5 live biome defs name mods NOT in the active list." No fix commit found since filing. Real, undone.

### DEAD_BIOME_DEFS_IN_PROSE_1
Filed `130901b25` today. Only the filing commit found — no fix commits since. Real (per its own account, follows `BIOME_BINDINGS_TABLE_STALE_1` which fixed the def→sheet table but not prose). Undone.

### FALL_LINE_ARRIVAL_MECHANISM_1
Spec/criteria written (`4f8f16a2e` "the arrival spec, with the region name corrected"), but the item's own text says the actual delivery mechanism (wreck incident / subregion landmark / generator output for the 17 species) is not yet built, and warns "Do not build this by re-adding rows to any wildAnimals table." Spec exists; mechanism does not.

### STALE_VIVIFIED_WORLDMAP_CITED_1
Partially done: commit `6cb085e3f` fixed `fall_line.md`'s table in place (corrected the "308-tile Fall Line region" claim to the real two-region split, 155+153). But the item's own "## what needs doing" step 4 ("Sweep the other biome sheets under `design/Jawa/worldbuilding/biomes/` for region or biome names that exist only in the vivified CSV") was not done — only one doc was fixed. Its own "## criteria" ("No live design doc names a region or biome the canonical worldmap does not have") is broader than what shipped.

### FALL_LINE_MAJOR_REGION_LABEL_1
Item's own final line: "## state — Blocked only on the bridge. Offline work complete." Diagnosis done (all 71 Ash'karr world features sit at the engine's size floor, MEASURED from `CANONICAL_ASHKARR_START_2026-09-12.rws` via `xml.etree.ElementTree`), fix identified (raise `maxDrawSizeInTiles` on the Fall Line feature), just needs bridge access to apply — matches its `needs: bridge` in the queue. Not stale, genuinely waiting on the game being up.

### BIOME_MOD_SPLIT_EXECUTION_1
Still exactly as CLAUDE.md describes: "specified and blocked on 10 owner questions" (`2a65dbc20`). `7c27de6ab` fact-checked 5 of the verifiable premises under §7 (per this session's own recent-commits list), but no commit found ruling the 10 owner questions themselves. Undone, correctly blocked on `needs: owner`.

### STALE_V24_NAMES_IN_FROZEN_SHEETS_1
Only the filing commit found (`f1635b3a9`, in this session's own recent-commits list: "file the rename that reached 1 sheet of 6"). No fix commit yet. Undone — the V24 rename (Venom Wood→Fuelmere, South Crags→Sootreach, Thornend→Frostvein) still needs applying to 5 of 6 frozen sheets.

## UNKNOWN

None. Every item in this batch had at least one checkable piece of evidence (a file, a commit, or the item's own dated prose) — no item required a guess.

## Items that claim to be blocked on an item that is already closed

**Highest-confidence finding of the sweep:**

### FLOOD_WITNESS_EVENT_1 (IN PROGRESS/BLOCKED, not in this sweep's 44-item scope, but flagged since it's the exact pattern the brief asks to hunt)
Queue's own `blocked:` line: "Design + quest spec done...; waits on **FLOOD_CANYON_BIOME_1** (the mechanism mod, FOUNDRY) and its one production arm-the-flood verb, then quest def build (on FLOOD_CANYON_BIOME_1)."
`rimflow show FLOOD_CANYON_BIOME_1` → **state: `done`** ("Standalone RimMandrake-tier biome mod: periodically flooded canyons — chime warning mechanic, flood events... filed 2026-09-12, owner FOUNDRY"). The gating mod item is closed. Whether the specific "one production arm-the-flood verb" sub-detail is itself done needs a direct look at `FLOOD_CANYON_BIOME_1`'s closing commit/prose — but the block as stated names an already-closed item as the reason for waiting, exactly the `NAMING_SCHEME_EXECUTION_1` pattern CLAUDE.md warns about. Worth an immediate re-check by BENCH.

### Checked and correctly NOT stale (for contrast, so this section isn't read as "everything is broken"):
- `NORTH_STAR_PIT_PILOT_1` cites `MOD_VALIDATION_PIT_PILOT_1` as its predecessor, explicitly noting it "is closed `done` having 'run it green' — that green is the defect this item exists to overturn." Citing a closed item as the reason THIS item exists is correct, not a false block.
- `NORTHSTAR_MOTION_FRAMES_1` / `NORTH_STAR_ATMOSPHERIC_TBD_1` cite each other and are both still open (`proposed`) — no false block.
- Other in-progress/blocked items visible in the queue but out of this sweep's scope (`FAUNA_LORE_DIVERSIFICATION_1`, `ASSIGNMENT_SHEETS_VERDICT_SITTING_1`) cite `BIOME_KITS_PUSH_TO_TEST_1`, `CANON_CREATURE_REGEN_1`, `ROT_SIZE_REJUDGE_APPLY_1`, `COLD_LOAD_RUN_SHEET_4` — all four are still `state: doing`, genuinely open, not closed. No false block found among these.

## Notes on scope

44 of the 46 PROPOSED items were evaluated (2 duplicates of the excluded-4 list removed from the raw queue text). Several items filed 2026-09-20 (same day as this sweep) are correctly STILL LIVE simply because they are hours old, not because anyone is sitting on them.
