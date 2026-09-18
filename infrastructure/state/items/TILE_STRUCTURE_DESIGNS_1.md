# TILE_STRUCTURE_DESIGNS_1

Thin item — FOUNDRY decision on spec/verify/criteria, 2026-08-31.

## spec

`design/Jawa/worldbuilding/structure_injection_roster.md` (the content
list) and `design/Jawa/bridge/STRUCTURE_TEMPLATE_ENGINE_SPEC.md` §8-9 (the
engine: rimplace Lua templates, format axis decided, generation axis
staged 🅐→🅑, `GenStep_RimplacePlan` named as the one missing C# piece).

**Scope for this pass, decided by FOUNDRY:**
1. Build `GenStep_RimplacePlan` (`mandrake.rm.injections`, engine tier per
   the naming scheme's engine/content split) — replays a compiled
   rimplace plan at mapgen time. Verify terrain/roof ordering live, per
   the roster's own flag.
2. Author a first batch (3-5 rows) of the 44-row roster as rimplace `.lua`
   templates, per the roster's own §5 "FOUNDRY iteration protocol"
   (batch of 3-5, render sheet, not all 44 blind).

**Collision note:** `src/RimMandrake/Utils/rimplace/plan.py` and
`cli.py` had live uncommitted edits from another window when this item
was picked up (a `compile_flat()` flat-text plan compiler, docstring:
"the flat runtime format GenStep_RimplacePlan reads at mapgen time").
FOUNDRY did not edit either file — built `GenStep_RimplacePlan` to read
that documented flat format from a new, non-colliding location
(`src/RimMandrake/StructureInjections/`) instead of duplicating a JSON
compiler.

## verify

- Offline: the C# compiles clean, and a plan exported by
  `rimplace ... export` round-trips through `RimplacePlan.Parse` with
  every defName present.
- Live: build a test structure on a quicktest map via the new GenStepDef
  wired to a scratch `TileMutatorDef`/debug action, confirm
  terrain→foundation→things(transmitters-first)→roof land in the right
  order and the plan's defnames all resolve — the roster's own flagged
  risk.

## criteria

- `GenStep_RimplacePlan` deployed and proven on at least one existing
  template (`dwelling.lua` or `nursery.lua`) via a live quicktest.
- At least one new roster row shipped as a rimplace template, wired to a
  promise (LandmarkDef + TileMutatorDef + GenStepDef) or whisper
  (territory table row), following the roster's coverage lint (no
  promise without a registered responder).
- The remaining ~40 rows are explicitly left open for further batches,
  not silently declared done.

## 2026-08-31 batch 2 (FOUNDRY) — three more roster rows authored

Per the roster's own §5 protocol (batch of 3-5, offline verify, no live
placement). All lint/verify results independently re-confirmed by
FOUNDRY, not taken on a subagent's word alone (one fork's own summary
was internally confused about which items were done; the actual
`.lua` files and `lint`/`verify` output are the evidence, checked
directly):

- **The Krayt Graveyard** (row 3, RSW) —
  `design/Jawa/templates/krayt_graveyard.lua`. `lint`: 0 findings.
  `verify`: 3/3 defNames found.
- **The Podracer Wreck** (row 4, RSW) —
  `design/Jawa/templates/podracer_wreck.lua`. No "podracer engine"
  ThingDef exists in the stack (verified against the live dump, not
  guessed) — uses `AncientPodCar` (this project's own existing
  `PodCarIsLandspeeder.xml` reskin) as the one intact centerpiece plus
  vanilla `ChunkSlagSteel`/`Steel` scatter. `lint`: 0 findings. `verify`:
  3/3 defNames found.
- **The Hunting Lodge** (row 12, RSW) —
  `design/Jawa/templates/hunting_lodge.lua`. **Caught and fixed a real
  defect**: the template's own footprint requirement (3 bays ≥5 wide
  each + the cold room's power apron) needs 28×18, not the 20×16 first
  tried — `lint` correctly refused with `empty-plan`/`generator-refusal`
  rather than silently under-building. Re-verified clean at 28×18:
  `lint` 0 findings, `verify` 14/14 defNames found.

**Wiring added same pass**: `GenStepDefs_Batch2.xml` +
`TileMutatorDefs_Batch2.xml` in `mandrake.rsw.injections` give all
three (`RSW_KraytGraveyard`, `RSW_PodracerWreck`, `RSW_HuntingLodge`)
the same `extraGenSteps` responder wiring Moisture Farm has —
`validate_patch.py`: 0 errors on the whole content pack (5 files).
Still not "shipped" by the roster's own §5 bar: no letter text in the
gods' register, not placed on any tile (deliberately — a live world-tile
edit, out of scope here, same as Moisture Farm). 40 of 44 rows remain
untouched. Left `doing`.

## STATE 2026-08-31, session end (owner went AFK mid-item)

**Done, offline-verified:**
- `mandrake.rm.injections` (`src/RimMandrake/StructureInjections/`) —
  `GenStep_RimplacePlan` + `RimplacePlan.cs` parser for the flat runtime
  format `rimplace.plan.compile_flat()` emits (added to `plan.py`/`cli.py`
  as an `export` command — see collision note above, now resolved: the
  format landed clean, `selftest` 28/28 still passes). Ordering mirrors
  `compile_calls()`'s live-proven order exactly: foundation → terrain →
  things (transmitters via `ThingDef.EverTransmitsPower` before
  connectors) → roof. Builds clean (0 warnings, 0 errors). API calls are
  cited against decompiled 1.6 source, not guessed (`TerrainGrid.SetTerrain`/
  `SetFoundation`, `RoofGrid.SetRoof`, `GenSpawn.Spawn`, `TileMutatorDef.
  extraGenSteps` → `MapGenerator.cs:158-165`).
- A debug-action proof surface (`StructureInjectionsDebugActions.cs`,
  category `RMInject`) that replays an exported `.txt` plan at the mouse
  cell on the current map — bridge-reachable, same pattern as
  `PitDebugActions`.
- `mandrake.rsw.injections` (`src/RimStarWars/StructureInjectionsSW/`) —
  roster row 1, "The Moisture Farm": `design/Jawa/templates/moisture_farm.lua`
  (lint 0 findings, verify 9/9 defNames found), exported plan, a
  `GenStepDef` + `TileMutatorDef` (`RSW_MoistureFarm`) wiring it in via
  `extraGenSteps` — the actual responder mechanism, not a stub.
  `validate_patch.py`: 0 errors on both mods.
- 🔴 **Self-caught bug**: both mods were first authored as folders named
  `StructureInjections` under two different tiers
  (`src/RimMandrake/...` and `src/RimStarWars/...`) — `deploy_custom_mods.py`
  keys mods by folder BASENAME across all tiers, so the second deploy
  silently overlaid the first mod's `About.xml` in the live `Mods/`
  folder while orphaning its `Assemblies/`. Caught by reading the deploy
  plan output, not assumed clean. Fixed: content pack renamed to
  `StructureInjectionsSW`, the corrupted live folder deleted and both
  redeployed clean, `ModsConfig.xml` updated to the new packageId.
  **Lesson for future mods: folder basenames must be unique across the
  WHOLE `src/` tree, not just within a tier** — worth a line in
  `rimworld-deploy` or `deploy_custom_mods.py`'s own help text.

**Not done — owed to the next restart / a future session:**
- Live proof of `GenStep_RimplacePlan`'s ordering (the roster's own
  flagged risk) — needs a cold load with both mods active; restarts are
  the owner's call. Two ready-made debug actions
  (`Run plan: dwelling_test.txt`, `Run plan: moisture_farm_test.txt`)
  are wired for whoever drives the next load.
- The Moisture Farm is NOT yet a "shipped" roster row by the roster's own
  bar (§5): no letter text in Oomo's register, and not placed on any
  actual Ash'karr tile (deliberately deferred — that is a live world-tile
  edit on the frozen map, bridge + `world_commit`, out of scope here).
- 43 of 44 roster rows are untouched. The roster's own §5 protocol (batch
  of 3-5, render sheet, owner review) still stands for whoever picks this
  up next — this session did not try to force all 44 through solo.

## 2026-09-01 batch 3 (FOUNDRY, fork) — four RUT-tier roster rows authored

Picked up under BELT-mode ("Full belt. Continue. Don't stop."), pure offline
authoring, no bridge/restart touched — a sibling fork was concurrently
driving a live restart for unrelated mods, so ModsConfig and the bridge
were deliberately left alone this pass.

🔴 **This session's `defs.sqlite` capture is scoped to `ResearchProjectDef`
only** (522 rows, no ThingDef/TerrainDef coverage — `rimplace verify`'s own
known-answer self-check against `Human` correctly returns UNMEASURED, not a
false pass). Worked around the same way `validate_patch.py` always resolves
defNames: a throwaway `PatchOperationConditional` probe against the real
on-disk `Data`/`Mods`/`Workshop` XML confirmed every defName used below
exists exactly once, with its source file. This is not weaker than
`rimplace verify` — it is the same authority that command reads from when
the dump IS current.

- **The Oasis Shrine** (row 10, RUT) — `design/Jawa/templates/oasis_shrine.lua`.
  Open-air: spring (`PrimitiveWell`) centered in a paved ring, 4
  offering-bowl stations (`SculptureSmall`), 2 `TorchLamp`. `lint`: 0
  findings. defNames confirmed: `PrimitiveWell` (Dubs Bad Hygiene Lite),
  `SculptureSmall`/`TorchLamp`/`PavedTile` (Core).
- **The Rakatan Trace** (row 9, RUT) — `design/Jawa/templates/rakatan_trace.lua`.
  A sealed `Wall`+`Door` on one footprint edge backing onto NOTHING (no
  room ever declared past it — structurally sealed, matching "nothing
  opens yet"), 2 `SculptureSmall` glyph markers, paved forecourt. `lint`: 0
  findings. defNames confirmed: `Wall`/`Door`/`SculptureSmall`/`PavedTile`
  (Core).
- **The Cistern** (row 19, RUT) — `design/Jawa/templates/cistern.lua`. 7x7
  walled/roofed pump room, `PrimitiveWell` off-center, 2 `Shelf` (caught
  and fixed a footprint-collision lint error first — `Shelf` is 2x1, not
  1x1, spacing corrected), 1 `TorchLamp`. The roster's own "the stair goes
  further down than the pumps need" line is deliberately left as flavor
  only — RimWorld has no basement/multi-level mechanic to model it with;
  disclosed in the template's own note and the review sheet's invented-
  rules panel, not silently dropped. `lint`: 0 findings after the fix.
- **The Toll Gap** (row 13, RUT) — `design/Jawa/templates/toll_gap.lua`.
  7x5 walled/roofed toll house (desk+chair facing the door, 2 `Shelf`,
  `TorchLamp`), flanked by up to 6 `Sandbags` cells narrowing the passage.
  Caught and fixed the same `Shelf` 2x1 collision as the Cistern, plus a
  `TorchLamp`/`DiningChair` cell collision — both spacing errors, not
  design changes. `lint`: 0 findings after the fix.

**Wiring**: new tier mod `src/RimUtinni/StructureInjectionsRUT/`
(`mandrake.rut.injections`, engine-dependent on `mandrake.rm.injections`,
following `mandrake.rsw.injections`'s exact shape) —
`GenStepDefs_Batch3.xml` + `TileMutatorDefs_Batch3.xml` give all four
(`RUT_OasisShrine`, `RUT_RakatanTrace`, `RUT_Cistern`, `RUT_TollGap`) the
same `extraGenSteps` responder wiring as every prior batch.
`validate_patch.py`: 0 errors, 0 warnings on all 3 files. `rimplace
selftest`: 28/28, unaffected.

**NOT deployed, NOT added to ModsConfig this pass** — deliberately, to
avoid racing the sibling fork's concurrent restart on unrelated mods (same
"one bridge driver at a time" discipline). Repo content only; deploy +
enable + the live cold-load ordering proof all ride the next restart,
alongside batch 1/2's still-open live-proof debt.

Review sheet: `design/Jawa/worldbuilding/review/tile_structure_batch3_sheet.html`
(`check_sheet.py`: 0 FAIL/0 WARN/27 ok, all 4 rows pre-filled `ship`, 3
invented premises declared). No decisions file yet — nothing has been
reviewed.

Still not "shipped" by the roster's own §5 bar for any of the 8 rows
authored across all three batches so far: no letter text in any god's
register, none placed on a live tile. ~39 of 44 roster rows remain
untouched. Left `doing`.

## 2026-09-02 batch 4 (FOUNDRY) — three more rows, RSW+RUT

Picked up offline while BENCH held the bridge with the owner chasing
`COLD_LOAD_STALL_INTERMITTENT_1` — pure repo-content authoring, no
deploy, no ModsConfig touch, same "one bridge driver at a time"
discipline batch 3 followed.

- **The Bantha Graveyard** (row 15, RSW) —
  `design/Jawa/templates/bantha_graveyard.lua`. A loose, unbounded
  scatter (no single center-of-menace, unlike the Krayt Graveyard's
  crescent) of `BanthaHorn`/`Leather_Bantha`. `lint`: 0 findings.
  `BanthaHorn`/`Leather_Bantha` confirmed 1 real hit each in the live
  593-mod set (`mlie.starwarsanimalcollection`, `Items_Resource_
  swanimal_Items.xml`) via a `validate_patch.py` `PatchOperationConditional`
  probe — no `Ivory` ThingDef is reachable (`ProcessIvoryBantha`'s own
  product is gated `MayRequire="LegendaryMinuteman.SimpleIvory"`,
  confirmed NOT active: 0 hits in the live `ModsConfig.xml`), so the raw
  horn trophy stands in for the roster's "ivory-scatter" read.
- **The Mynock Roost** (row 18, RSW) —
  `design/Jawa/templates/mynock_roost.lua`. Lightest row this batch, per
  the roster's own "NEW light": chewed `PowerConduit` stubs,
  `ChunkSlagSteel` debris, `Filth_AnimalFilth` grime, no walls. No
  dedicated "mynock nest" ThingDef exists anywhere in the stack (checked
  `mlie.starwarsanimalcollection`'s own Defs tree directly) — represented
  through what the roost leaves behind instead. `lint`: 0 findings, all
  3 defNames confirmed 1 real hit each.
- **The Glass Sea** (row 16, RUT) — `design/Jawa/templates/glass_sea.lua`.
  The batch's only pure-terrain row: `VolcanicRock_Smooth` core (Odyssey,
  glassy/Beauty+2) with a rough `VolcanicRock` edge ring for a natural
  fade, plus a sparse `ChunkSlagSteel` scatter added purely because the
  engine's own lint rule 9 ("a plan that places nothing is a bug")
  correctly cannot distinguish a deliberate terrain-only template from an
  author forgetting to build anything — declared as an invented premise
  on the review sheet, not silently added. `lint`: 0 findings, both
  Odyssey terrain defNames + `ChunkSlagSteel` confirmed 1 real hit each.

A tool bug found and worked around, not fixed: `rimplace`'s Lua `rng`
table exposes only `int`/`chance`/`pick`, no `value()` — `mynock_roost.lua`
first threw `attempt to call a nil value (field 'value')` at `lint` time;
rewritten to nested `rng.chance()` calls. Worth a `rimplace` doc line for
whoever authors the next batch.

**Wiring**: `GenStepDefs_Batch4.xml` + `TileMutatorDefs_Batch4.xml` added
to both existing tier mods (`mandrake.rsw.injections` for the two RSW
rows, `mandrake.rut.injections` for Glass Sea) — same `extraGenSteps`
responder shape every prior batch used. `validate_patch.py` against the
live 593-mod dump: 0 errors, 0 warnings on both mods' full file sets (7
files SW, 4 files RUT). `rimplace selftest`: 28/28, unaffected.

Review sheet: `design/Jawa/worldbuilding/review/tile_structure_batch4_sheet.html`
(`check_sheet.py`: 0 FAIL/0 WARN/27 ok, all 3 rows pre-filled `ship`, 4
invented premises declared). No decisions file yet — nothing has been
reviewed.

**NOT deployed, NOT added to ModsConfig this pass** — deliberately, same
discipline as batch 3, to avoid touching shared game state while BENCH/
the owner were mid-diagnosis. Repo content only; deploy + enable + the
live cold-load ordering proof all ride the next restart, alongside
batches 1-3's still-open live-proof debt.

Still not "shipped" by the roster's own §5 bar for any of the 11 rows
authored across all four batches so far: no letter text in any god's
register, none placed on a live tile. ~36 of 44 roster rows remain
untouched. Left `doing`.

## 2026-09-02 batch 5 (FOUNDRY) — three more RUT rows, after COLD_LOAD_STALL_INTERMITTENT_1 resolved

Owner confirmed the cold-load-stall alarm was a false positive (idle main
menu misread as a hang, closed `COLD_LOAD_STALL_INTERMITTENT_1` as not-a-bug —
see `idle-menu-looks-like-load-stall` memory). BENCH still held the bridge
for other work, so this pass stayed offline/repo-only, same discipline as
every prior batch.

- **The Monument** (row 8, RUT) — `design/Jawa/templates/monument.lua`. One
  `SculptureGrand` (stuffed `BlocksGranite`) centered on a fully paved
  plaza, a few `ChunkGranite` rubble pieces at its base for "half-buried."
  `lint`: 0 findings. `SculptureGrand`/`BlocksGranite`/`ChunkGranite`
  confirmed 1 real hit each in the live 593-mod set.
- **The Dead Beacon** (row 14, RUT) — `design/Jawa/templates/dead_beacon.lua`.
  A 5x5 walled/roofed lamp-room, one `StandingLamp` centered and
  deliberately left UNWIRED to any power source — "relighting it is a
  CHOICE" read mechanically as staying cold until a future player action
  powers it, not a new comp/hediff. `lint`: 0 findings at 7x7 export size;
  correctly refuses (not silently under-builds) below its 5x5 minimum.
  `StandingLamp` confirmed 1 real hit.
- **The Broken Ring** (row 20, RUT) — `design/Jawa/templates/broken_ring.lua`.
  Terrain-led like `glass_sea.lua`: an off-center patch of
  `AncientMegastructure` (Odyssey) as the fused hull segment itself, not a
  prop sitting on ordinary ground, with `Steel`/`ComponentIndustrial`/
  `ChunkSlagSteel` scrap densest directly over the hull. `lint`: 0
  findings. All 4 defNames confirmed 1 real hit each.

All defNames sourced from vanilla (RimSage-indexed) and independently
cross-checked via a `validate_patch.py` `PatchOperationConditional` probe
against the full live 593-mod set — 6/6 real, exactly one hit each.

**Wiring**: `GenStepDefs_Batch5.xml` + `TileMutatorDefs_Batch5.xml` added to
the existing `mandrake.rut.injections` mod — same `extraGenSteps` shape
every prior batch used. `validate_patch.py` on the whole mod (now 6 Defs
files + About): 0 errors, 0 warnings. `rimplace selftest`: 28/28,
unaffected.

Review sheet: `design/Jawa/worldbuilding/review/tile_structure_batch5_sheet.html`
(`check_sheet.py`: 0 FAIL/0 WARN/27 ok, all 3 rows pre-filled `ship`, 3
invented premises declared). No decisions file yet — nothing has been
reviewed.

**NOT deployed, NOT added to ModsConfig this pass** — same discipline as
every prior batch. Repo content only; deploy + enable + the live cold-load
ordering proof all ride the next restart, alongside batches 1-4's still-open
live-proof debt.

Still not "shipped" by the roster's own §5 bar for any of the 14 rows
authored across all five batches so far: no letter text in any god's
register, none placed on a live tile. ~33 of 44 roster rows remain
untouched. Left `doing`.

## 2026-09-02 batch 6 (FOUNDRY) — one more RUT row, full-belt/AFK

Owner went AFK mid-session ("Full belt mode. Go as far as you can. Bench
has the bridge right now.") — continuing solo, offline/repo-only, same
discipline as every prior batch since BENCH still holds the bridge.

- **The Imperial Waystation** (row 21, RUT) —
  `design/Jawa/templates/imperial_waystation.lua`. A 9x6 walled/roofed
  prefab: an administrative desk (`Table1x2c`/`DiningChair`/`TorchLamp`)
  near the door, three stocked shelves along the back wall (`Steel`/
  `ComponentIndustrial`/`MedicineIndustrial`). "loot and statecraft hooks;
  pursuit heat rises on looting." **Caught and fixed a real footprint bug
  first try**: `lint` reported a `DiningChair`/`Table1x2c` collision —
  `Table1x2c` is 1 wide x 2 TALL, not 1x1 as its short name suggests; the
  chair moved beside it instead of below it. `lint`: 0 findings after the
  fix. Checked `AncientIndustrialShelf` as a more "Imperial ruin"-flavored
  substitute first, but its own def says "offers nothing of value"
  (`isInert=true`, `claimable=false`) — contradicts this row's own
  "INTACT stores" framing, so plain functional `Shelf` was used instead.
  All 7 defNames confirmed 1 real hit each in the live 593-mod set.

**Two rows deliberately SKIPPED this pass, not silently dropped**:
- Row 11, The Kiln — the roster's own gating column marks it "contested
  per sacred-sites" (an Ohm-vs-Sh'kaar dispute). Reads as needing an owner
  ruling before authoring, not a FOUNDRY call to make solo, especially
  unattended.
- Row 5, The Junkers' Field — its own gating line names a
  "coastal_mesa-style authored pass" (the mapsynth pipeline), a different
  tool from every other row in this program so far. Out of scope for a
  rimplace-template batch; would need its own scoping pass.

**Wiring**: `GenStepDefs_Batch6.xml` + `TileMutatorDefs_Batch6.xml` added
to `mandrake.rut.injections` — same `extraGenSteps` shape every prior
batch used.

Review sheet: `design/Jawa/worldbuilding/review/tile_structure_batch6_sheet.html`
(`check_sheet.py`: 0 FAIL/0 WARN/27 ok, 1 row pre-filled `ship`, 2 invented
premises declared, including the two skips above named in the brief). No
decisions file yet — nothing has been reviewed.

**NOT deployed, NOT added to ModsConfig this pass** — same discipline as
every prior batch. Repo content only.

Still not "shipped" by the roster's own §5 bar for any of the 15 rows
authored across all six batches so far: no letter text in any god's
register, none placed on a live tile. ~32 of 44 roster rows remain
untouched (2 of those explicitly held for an owner call, not just unpicked).
Left `doing`.

## 2026-09-02 (FOUNDRY) — code review of batches 4-6, two real findings fixed

Owner asked for proactive code review of tonight's offline work. Ran
`/code-review high` against the two new SelfTest `Program.cs` files and all
7 batch-4/5/6 `.lua` templates. The SelfTest files checked out clean
(`PickWinner`/`Specificity` confirmed byte-for-byte against `ClaimEngine.cs`,
`BandFor`/`Adjust`/`ResetOnLaunch` confirmed against `GameComponent_
ColonyVisibility.cs`, `GenDate.TicksPerDay` confirmed 60000). Two real
findings against the templates, both fixed:

- **`monument.lua`** had no minimum-footprint guard, unlike every sibling
  template — on `rect.w == 1` its own bounds clamp pushed the 2x2
  `SculptureGrand` centerpiece to `rect.x - 1`, ONE CELL OUTSIDE the
  footprint, which `ctx:place` silently refuses rather than draws: the
  plaza and rubble chunks would still build around a colossus that was
  never placed. Added the same `ctx:refuse` minimum-footprint guard
  `dead_beacon.lua`/`imperial_waystation.lua` already use. Re-linted at
  1x1 (clean refusal), 2x2 (minimum valid, clean), and 16x16 (production
  size, 0 findings, export byte-identical to before the fix — the guard
  never engages at any size this row is actually meant to run at).
- **`mynock_roost.lua`**'s three scatter chances (0.10/0.20/0.40) are
  `elseif`-chained (structurally required — only one thing can occupy a
  cell), which compounds them into real per-cell rates of 10%/18%/28.8%,
  not the 10/20/40% the literals suggest — a future editor tuning one
  branch would silently shift every later one's actual density too, with
  no line anywhere near the edit showing why. Not a behavior bug (the
  shipped density is what was intended and tested); added a comment
  stating the actual compounded math so the next edit isn't surprised by
  it. Export re-verified byte-identical to before.

Both re-exported, `rimplace selftest` re-run (28/28), both mods' `Templates/`
`.txt` diffed to confirm no change at the sizes already wired/committed —
this was a defensive/clarity fix to code that had not yet caused a wrong
result, not a rollback of anything shipped.

## 2026-09-09 (FOUNDRY) — coverage lint built, precise state established, no new templates

Picked up during a full-mod-list cold load in progress on unrelated work
(BENCH holding the bridge for `BIOME_ENRICHMENT_POISON_FOREST_1`) — pure
offline pass, no bridge/ModsConfig touch, per this dispatch's own
instruction. Re-read the whole item history and the roster before writing
anything, per standing lesson (queue items decay).

**Built**: `src/RimMandrake/Utils/structure_roster_lint.py` — the
coverage-lint mechanism the item's criteria has asked for since 2026-08-31
and no prior batch built. Checks, per roster row: promise → does
`design/Jawa/templates/<slug>.lua` exist AND does some `GenStepDefs*.xml`
in that row's tier mod reference `Templates/<slug>.txt`. Roster rows are
hardcoded in the script (name/tier/slug/status), not parsed from the
markdown prose — the roster isn't machine-structured and mis-parsing free
text would be worse than a human-checked table. Run: `python3
src/RimMandrake/Utils/structure_roster_lint.py`.

**Precise coverage, run 2026-09-09** (supersedes every "~N of 44 rows
remain" line above — those were never rows, only promises, and were
undercounting by one: row 22 The Homestead was built by a DIFFERENT item,
`INHABITED_AUGMENTATION_BUILD_1` (commit `ade756fc`, abode/homestead/
compound wired in `mandrake.rut.injections`), and no prior session here
credited it):

- **Promises: 16/22 covered** (template + wired responder, both verified
  present on disk): #1 Moisture Farm, #3 Krayt Graveyard, #4 Podracer
  Wreck, #8 Monument, #9 Rakatan Trace, #10 Oasis Shrine, #12 Hunting
  Lodge, #13 Toll Gap, #14 Dead Beacon, #15 Bantha Graveyard, #16 Glass
  Sea, #18 Mynock Roost, #19 Cistern, #20 Broken Ring, #21 Imperial
  Waystation, #22 Homestead.
- **6 promises are real, declared gaps — not mine to fill blind**:
  - **#5 The Junkers' Field**, **#11 The Kiln** — already correctly
    identified and skipped in batch 6 (needs the coastal_mesa mapsynth
    tool / an owner ruling on the Ohm-vs-Sh'kaar contest, respectively).
    Re-confirmed still unbuilt.
  - **#2 The Sarlacc** — roster asks for "responder polish (warning
    totems ring the pit)" onto the *existing* `sw_Sarlacc`/`sw_SarlaccLair`
    pair. Checked: that mutator's def lives in a Workshop mod, not this
    repo, and its actual pit geometry has never been inspected here — I
    have no dump/RimSage access to it this pass (bridge busy on another
    item's mapgen work, not free to query defs against). Ringing an
    unmeasured pit shape is a real design/measurement gap, not a blind
    fill.
  - **#6 The Dead Crawler**, **#7 The Signal Mast**, **#17 The Ashfall
    Battery** — the roster names these ("three interior decks" / "comms-
    console room" / "fuel-farm room") without a concrete layout anywhere
    in any design doc. Same rule prior batches applied to underspecified
    rows (Kiln, Junkers' Field): do not invent the content, leave open.
- **Whispers: 0/22 — a missing SUBSYSTEM, not 22 small gaps.** Checked
  directly (`grep -rl whisper src/ design/`): no territory table, no
  weighted-selector GenStep, no landing-letter hook, no incident/quest
  wiring keys off any of the 22 whisper names or their god-country column
  anywhere in the repo. The roster's own mechanism sketch (§0b:
  `GenStep_RandomSelector` for whisper variety) was never built out. This
  is a full engine-plus-22-distinct-mechanics build (a strongbox event,
  a migration, a hostile-pair spawn, a timed knocking incident, etc. —
  each is its own design, not a template fill) and was out of every prior
  batch's scope too; it belongs as its own scoped pass, not something a
  single offline dispatch should attempt uninvited. Flagging explicitly
  because no prior state note in this file ever gave whispers an honest
  number — they were silently absent from every "~N of 44" line above.

**VERIFY (terrain/roof ordering) — offline re-confirmed, live proof still
owed.** Re-read `src/RimMandrake/StructureInjections/Source/
GenStep_RimplacePlan.cs` in full: `ApplyPlan` runs CLEAR → FOUNDATION →
TERRAIN → THINGS (`OrderByDescending(EverTransmitsPower)`, transmitters
spawn before connectors) → RUN → ROOF → PAWN, matching both the roster's
§0b requirement and the live-proven `rimplace.plan.compile_calls()` order
the code comments cite line-for-line. This is the same order the item's
own `verify` section asks for. Did **not** attempt a live quicktest this
pass — the bridge was held by another FOUNDRY window running unrelated
mapgen work and the dispatch for this item explicitly said not to touch
it; the live ordering proof (build a test structure on a quicktest map,
confirm no clipping/wrong roof) remains owed exactly as every batch since
2026-08-31 has recorded, not newly discovered as missing.

**Found, not touched**: `mandrake.rut.injections` — the mod holding 10 of
the 16 covered promise rows plus Homestead — is deployed on disk
(`C:\...\RimWorld\Mods\StructureInjectionsRUT` exists) but is **absent
from the live `ModsConfig.xml`** (`mandrake.rm.injections` and
`mandrake.rsw.injections` are both present and active; `mandrake.rut.
injections` is not, checked by direct grep against the live file). None
of RUT's 10 covered rows can generate in the current game until it's
enabled — an activation gap, not a content gap. Left alone: enabling a
mod mid-cold-load on an unrelated item's active load is exactly the
cross-window collision this dispatch said to avoid; it rides the next
restart alongside the still-open live-ordering proof.

**No new templates authored this pass** — every remaining promise is a
declared gap (tool/owner/design), and the whisper subsystem is out of a
single dispatch's scope. Nothing was invented to pad the count.

**Coverage as of this pass: 16/22 promises (73%), 0/22 whispers, 0
coverage-law violations** (no promise ships with only a template or only
a responder — `structure_roster_lint.py` confirms this mechanically now,
not by re-reading batch notes by hand). Left `doing` — not close-eligible:
6 promise gaps need an owner ruling or a design pass, the whisper engine
doesn't exist, and the live ordering proof is still owed.

## 2026-09-12 (FOUNDRY, AFK full-belt) — whisper batch 1: engine built, 3/22 rows wired

Owner AFK for the night ("go as far as you can, keep subagents going").
Picked up exactly where the 2026-09-09 pass left off: the whisper
subsystem was 0/22, correctly flagged as "a missing SUBSYSTEM, not 22
small gaps... belongs as its own scoped pass." This pass IS that scoped
pass, kept deliberately small per the same "batch of 3-5, smaller
complete beats large broken" discipline every promise batch used.

**What "whisper" turned out to require, precisely** — re-read
`structure_injection_roster.md` §0b/§3/§4 and `sacred_sites_pass_1.md`
§1a/§1b in full before writing anything:

- The roster's own §0b names the mechanism: vanilla `Verse.
  GenStep_RandomSelector` (RimSage-confirmed field shape:
  `List<RandomGenStepSelectorOption>`, `RandomElementByWeight`, runs the
  winner's own `genStep`). **No new C# is needed for the roll itself** —
  this is different from what the promise half needed
  (`GenStep_RimplacePlan` was the one new class promises required).
- The structural difference from a promise: a promise gets a BRAND-NEW
  `TileMutatorDef` for the owner to hand-place on one tile. A whisper
  rolls from "the territory table... god-country × biome" — it must ride
  an EXISTING TileMutatorDef that is already the tile's territory, patched
  (`PatchOperationAdd` onto `extraGenSteps`) rather than authored fresh.
  This is why the mechanism sat unbuilt: most whisper conditions in §3 are
  BIOME-level or ARC-band conditions ("nightside," "any wild band," arc
  ranges), and `TileMutatorDef.extraGenSteps` (`TileMutatorDef.cs:26-28`,
  `MapGenerator.cs:155-175`) is the ONLY hook this architecture has — there
  is no equivalent field on `BiomeDef`. A whisper only has somewhere to
  attach when its own roster line names an actual mutator.
- The one legal exception needing new C#: WHISPER #12 "Never Was" ("Ishko's
  authored-nothing... genuinely nothing injected") needs an option that
  does nothing, which vanilla's selector cannot express on its own —
  `GenStep_Whisper_NoOp.cs` (15 lines, `mandrake.rm.injections`, builds
  clean, 0 warnings) is that one option.
- The roster's own "trust law" (whisper announces itself in the landing
  letter) is explicitly OUT of this item's scope —
  `sacred_sites_pass_1.md` §5 itself names that engine hook as separate,
  unbuilt, future work ("files as its own item when the owner calls it").
  Not attempted here; `GenStep_Whisper_NoOp` logs its pick so that future
  hook has something to read without touching this class.

**3 of 22 whisper rows wired this pass**, each verified via a live
`validate_patch.py` probe against the real, active 593-mod set (`--defs`
Data+Mods+Workshop) — chosen specifically because each has a
RimSage/probe-CONFIRMED real mutator to anchor on, not because they were
easy to invent:

- **#12 Never Was** (Ishko) → patched onto vanilla `Cavern`
  (`sacred_sites_pass_1.md` §1b: "any Cavern-class mutator underground" is
  named as HIS territory explicitly). `validate_patch.py`: 1 match in
  Odyssey `TileMutators_Natural.xml`. No template — the no-op class is the
  whole responder. **Declared limitation, not hidden**: with only one
  option wired in this selector so far, it fires every time Cavern
  generates, not "RARE" as the roster frames it — a future batch adding
  more Ishko/Cavern whisper options at a higher relative weight is what
  actually makes it rare.
- **#20 The Rootstock** (roster tags it Oomo; `sacred_sites_pass_1.md`
  §1b's own biome-class table reads `DryLake` as ZIZZIK's instead — a real
  conflict between the two design docs, declared, not silently resolved
  one way) → patched onto vanilla `DryLake`. `validate_patch.py`: 1 match,
  same Odyssey file. `design/Jawa/templates/rootstock.lua`: a cracked-
  lakebed floor (`DryLakeBed`) with a density-graded `Plant_ShrubLow`
  scatter standing in for "dormant seedbank" (no dedicated ThingDef
  exists). **Scope declared**: static content only — the roster's own
  "blooms after any rain/water event" trigger is a comp/event this pass
  does not build, same discipline Dead Beacon's unwired lamp and the
  Cistern's flavor-only stair already used.
- **#18 The Choir Wind** (Ozzik, "monument reads") → patched onto OUR OWN
  `RUT_Monument` (PROMISE #8's mutator, `TileMutatorDefs_Batch5.xml`) —
  this whisper only rolls where that promise has already been placed on a
  tile by the owner's pen, same live-placement debt every `RUT_Monument`
  content already carries. `design/Jawa/templates/choir_wind.lua`: 4
  `SculptureSmall` resonant markers ringing the plaza edge, reusing the
  same substitute-prop discipline `oasis_shrine.lua`/`rakatan_trace.lua`
  established (no "wind chime" ThingDef exists). **Scope declared**: static
  markers only — the mood/grief-pressure mechanic is not built.

**19 of 22 whisper rows remain `MISSING-MECHANISM`, honestly** — most have
no nameable TileMutatorDef to attach to (nightside biome bands, arc
ranges, "any wild band"), and most of their CONTENT is its own
incident/quest/hediff/timer design (a strongbox+debt event, a hostile-pair
spawn, rhythmic knocking on a timer, a claim-map chain hook) — not a
template fill, matching exactly the standard the promise batches already
applied to Kiln/Junkers'/Dead Crawler/Signal Mast/Ashfall Battery. Nothing
invented to pad the count.

**`structure_roster_lint.py` extended** (not rewritten) to check the
whisper half mechanically instead of hardcoding "0/22, no mechanism": a
whisper row now checks template (if content-bearing) + a `GenStepDef`
wrapping `GenStep_RandomSelector` referencing it (or `GenStep_Whisper_
NoOp` for a no-op row) + a `Patches/*.xml` operation naming both the
anchor mutator and that GenStepDef. Run 2026-09-12: **PROMISES 16/22
covered, WHISPERS 3/22 covered (19 MISSING-MECHANISM, 0 lint failures
among rows claiming done)**, exit 0.

**Build**: `GenStep_Whisper_NoOp.cs` added to `StructureInjections.csproj`,
built via the Windows-native `dotnet.exe` per the csproj's own comment —
`Build succeeded, 0 Warning(s), 0 Error(s)`. `rimplace selftest`: 62/62
(unaffected — this pass touched no engine logic, only new content).

**NOT deployed, NOT added to ModsConfig** — same discipline as every
promise batch; `mandrake.rut.injections` remains absent from the live
`ModsConfig.xml` exactly as the 2026-09-09 pass found it, unrelated to and
unchanged by this pass (not this dispatch's job to fix, no restart
touched). Deploy + enable + live-fire proof of all 3 whisper rows (does
`Cavern`/`DryLake` actually roll the selector; does the no-op genuinely
inject nothing) rides the next restart, alongside every promise batch's
same still-open live-proof debt.

**Running tally**: 16/22 promises, 3/22 whispers, engine mechanism for
whispers now exists and is proven wired (not just designed). Left
`doing` — nowhere near "genuinely all 22 whispers," which was never a
realistic bar for one pass per this item's own dispatch instructions.

## 2026-09-17 (FOUNDRY, BELT-mode fanout) — whisper batch 2: 2 more rows, one real cross-item finding, one lint fix

Re-derived state first per standing lesson (queue items decay): re-ran
`structure_roster_lint.py` before touching anything — still exactly
16/22 promises, 3/22 whispers, 0 lint failures, unchanged since
2026-09-12. Re-read `sacred_sites_pass_1.md` §1a/§1b in full before
picking rows, per the dispatch's own method.

**Went through all 19 MISSING-MECHANISM whisper rows against the
territory table looking for a nameable, CONFIRMED anchor** (never trusted
the stale `defs.sqlite`, capture 2026-09-12 — a `validate_patch.py`
`PatchOperationConditional` probe against the live 632-active-mod set,
`--defs` on the real Data/Mods/Workshop roots, is the authority used
throughout):

- **#2 The Listening Dark** (Ishko, nightside) — the roster's own line
  names the anchor explicitly: "(Hollow/Caves mutators)". Both confirmed
  real: `Hollow` (Odyssey, `TileMutators_Natural.xml`, 1 match) and
  `Caves` (Core, `MapGeneration/TileMutators.xml`, 1 match) — neither
  carries an `<extraGenSteps>` element in vanilla (checked directly in
  both source files), so both patches Add a whole new element to the
  `TileMutatorDef` node, same shape as Cavern/DryLake in
  `WhisperBatch1.xml`. **Built**: `design/Jawa/templates/listening_dark.lua`
  — a small static nook (2 `Shelf`, 1 `TorchLamp` — the roster's "free
  hidden base") plus one `SculptureSmall` marker standing in for
  "something already listens" (no watcher/eavesdropping ThingDef exists;
  same substitute-prop discipline every prior batch used). The cave
  network itself is native to the anchor mutators, not authored here.
  `lint`: 0 findings. No AI/threat mechanic built — declared, same
  discipline as Choir Wind/Rootstock.
- **#22 The Sarlacc Sign** (RSW, sarlacc-adjacent) — anchor
  `sw_SarlaccLair` (`Mlie.StarWarsAnimalCollection`, requires
  `Ludeon.RimWorld.Odyssey` on its own def), confirmed real (1 match,
  `SW_Buildings_Natural.xml`) — this is PROMISE #2's own adopted mutator,
  already the shipped precedent per the roster's §0. 🔴 **Unlike Hollow/
  Caves/Cavern/DryLake, `sw_SarlaccLair` ALREADY carries an
  `<extraGenSteps><li>sw_SarlaccPit</li></extraGenSteps>` in the mod's own
  source** (checked directly, not assumed) — the patch Adds into that
  EXISTING list, same shape Choir Wind's `RUT_Monument` patch already
  used, not the "whole new element" shape. **Built**:
  `design/Jawa/templates/sarlacc_sign.lua` — 3-5 `SculptureSmall` markers
  scattered unevenly along the footprint edge standing in for "edge-of-map
  burrow signs" (no burrow/totem ThingDef exists). This exact idiom
  ("ring it with SculptureSmall warning totems x3-5 unevenly") is
  independently specified for this same roster row in
  `structure_procedural_spec.md` §8.11 (`beast_lair.lua`'s own sarlacc
  variation) — confirms it as an already-graded design choice, not
  invented here. "Small livestock vanish near edges" (the active
  predation mechanic) is NOT built — declared, same discipline as every
  static-only whisper. `lint`: 0 findings.

**3 candidates investigated and explicitly rejected, not silently
skipped**:
- **#11 Static Ghosts** (Ohm country) — `sacred_sites_pass_1.md` §1b names
  `AB_MechanoidIntrusion` as Ohm's territory. Probed it directly: **0
  matches** as a `TileMutatorDef` xpath (`validate_patch.py` guard test:
  "test xpath matches 0 nodes"). Confirmed why by reading Alpha Biomes'
  own source: `AB_MechanoidIntrusion` is a **BiomeDef**
  (`Biomes_MechanoidIntrusion.xml`, and used as a `wildBiomes` dictionary
  key elsewhere), not a `TileMutatorDef` — it has no `extraGenSteps` hook
  to patch (§0b's own stated architecture limit: "there is no equivalent
  field on BiomeDef"). Real, confirmed negative finding, not an
  assumption.
- **#1 Something Buried** / **#16 The Prospector's Bones** (Rekko) —
  Rekko's territory per `sacred_sites_pass_1.md` §1a/§1b is `Ruins`-class
  landmarks. Checked: `Ruins` and `AncientQuarry` are **LandmarkDefs**
  (`Odyssey/Defs/TileMutators/Landmarks.xml`), not `TileMutatorDef`s —
  same architecture limit as Static Ghosts, confirmed by reading the
  source directly rather than assumed from the name. Both rows also lack
  a single specific anchor (#1 says "any"), and both are already claimed
  by `structure_procedural_spec.md` §8.14 (`cache.lua`, "roster whisper #8
  The Debtor's Cache, #1 Something Buried") under the sibling item
  `INHABITED_AUGMENTATION_BUILD_1` — building a competing mechanism here
  would duplicate, not fill, the gap.
- **#15 Quicksand Veins** — anchor `AB_QuicksandPits` (Alpha Biomes)
  IS confirmed real (1 match), but the roster's own line names no god and
  no content beyond what the anchor mutator already does natively
  ("mass-triggered natural hazard cells" is `AB_QuicksandPits`'s own
  vanilla behavior) — wiring it would mean either inventing unstated prop
  content or reusing `GenStep_Whisper_NoOp` with its hardcoded "Never Was"
  log line mislabeling a genuinely different row. Left `MISSING-MECHANISM`
  rather than force either.
- **#21 The Sleeper's Knock** (RUT, Rakatan traces) — anchor
  `RUT_RakatanTrace` (our own promise mutator) is real and buildable
  (same shape as Choir Wind → `RUT_Monument`), but the roster's own line
  names ZERO physical vocabulary — "rhythmic knocking from below on a
  timer; stops if answered wrongly" is 100% an audio/timer mechanic with
  nothing to place. Placing an invented marker prop here (unlike Choir
  Wind, whose line explicitly says "wind... sings", giving a real
  substitution target) would be inventing content the roster never
  described. Left `MISSING-MECHANISM`, honestly, same discipline as
  Dead Crawler/Signal Mast.

**🔴 Real cross-item finding, not touched**:
`design/Jawa/worldbuilding/structure_procedural_spec.md` (Fable-drafted,
BENCH-graded 2026-09-05) records the owner's verdict on
`REVIEW_tile_structures_21` the same night: *"A LOT more work is
required... these are pretty horrible... try much harder on them all and
not accept any rooms yet."* Neither this item's own 2026-09-09 nor
2026-09-12 pass (both of which explicitly re-read the whole item history
first) ever surfaced this. Resolved before treating it as a live
blocker: it is NOT a blanket rejection of this item's own track. The
much-harder R1-R5 rework is tracked by a **separate, sibling item**,
`INHABITED_AUGMENTATION_BUILD_1` (filed 2026-09-05, same day), which owns
`structure_procedural_spec.md` §8's 14 heavier archetypes end-to-end
(14/14 built+wired, 0/14 placed as of its own 2026-09-12 note) —
confirmed by reading both items' full history, not inferred. This item's
lightweight promise/whisper templates (markers, small nooks, terrain
dressing) are a distinct, still-valid, still-continuing track the owner
has not blocked. Also confirmed **no wiring collision**: `beast_lair.lua`
(§8.11, INHABITED's own build) uses a brand-new `RSW_BeastLair` mutator
for hand-placement, never patches `sw_SarlaccLair`'s `extraGenSteps` — so
this pass's Sarlacc Sign whisper and INHABITED's sarlacc-flavor beast lair
option coexist without either overwriting the other. Worth a line for
whoever next touches either item, since the omission cost real
investigation time this pass.

**Lint script extended** (not rewritten): `structure_roster_lint.py`'s
`WHISPERS` table only supported one mutator per row; #2's own roster line
names two ("Hollow/Caves"). `whisper_patch_wires_mutator` now accepts a
tuple and requires a patch for EVERY named anchor, not just one — a row
naming two anchors that only wired one would previously have reported
`covered` on a partial build; it cannot now.

**Wiring**: `Defs/GenStepDefs_Whisper_Batch2.xml` + `Patches/
WhisperBatch2.xml` (new, `mandrake.rut.injections`) for Listening Dark;
`Defs/GenStepDefs_Whisper_Batch1.xml` + `Patches/WhisperSarlaccSign.xml`
(new — RSW tier's first whisper files, `mandrake.rsw.injections`) for
Sarlacc Sign. `validate_patch.py` against the whole `Defs/`+`Patches/` of
both tiers, live 632-mod set: **59 files, 0 errors, 6 warnings** — 5
pre-existing (unrelated `DarkTower`/`VaultDungeons`/`WarLab` texPath
warnings, and the same "class not resolved from load set" info already
accepted on `WhisperBatch1.xml`), 1 new: `GenStep_RandomSelector` flagged
WARN (not info) on the RSW file specifically because `mandrake.rsw.
injections` ships no `Assemblies/` at all — a validator heuristic gap
(it has no vanilla-class allowlist), not a real defect: `GenStep_
RandomSelector` is the same confirmed-vanilla class `mandrake.rut.
injections`'s own Batch1/Batch2 files already reference bare, without
incident, since 2026-09-12. `rimplace selftest`: 62/62, unaffected.

**NOT deployed, NOT added to ModsConfig this pass** — same discipline as
every prior batch; owner was actively testing something live in-game
during this pass per the dispatch, so the bridge/ModsConfig/deploy were
never touched. `mandrake.rut.injections` remains absent from the live
`ModsConfig.xml` exactly as found 2026-09-09, unrelated to and unchanged
by this pass.

**Coverage after this pass: 16/22 promises (unchanged), 5/22 whispers
(up from 3/22), 0 coverage-law violations.** 17 whisper rows remain
`MISSING-MECHANISM`, honestly — most still have no TileMutatorDef anchor
at all (confirmed for 3 more this pass) or are pure incident/timer/audio
mechanics with no physical vocabulary to place. Nothing invented to pad
the count. Left `doing` — 6 promise gaps still need an owner ruling or a
design pass, most whisper rows still have no mechanism, and the live
mapgen-ordering proof (owed since 2026-08-31) is still open.

## 2026-09-18 whisper batch 3 (FOUNDRY, belt mode, subagent) — 2 more rows wired

Re-derived state first, per standing lesson (queue items decay): re-ran
`structure_roster_lint.py` before touching anything — confirmed still
exactly 16/22 promises, 5/22 whispers, 0 lint failures, unchanged since
2026-09-17. Re-read the whole item history, `structure_injection_roster.md`
in full, and `sacred_sites_pass_1.md` §1a/§1b/§4 in full before picking
rows, per the dispatch's own method.

**Went through every remaining `MISSING-MECHANISM` whisper row looking for
a nameable, CONFIRMED anchor** — never guessed a defName; every candidate
below was either read directly out of a live Data/Odyssey/Core source file
or confirmed via a `validate_patch.py` `PatchOperationConditional` probe
against the real, active 634-mod set (`--defs` Data+Mods+Workshop, live
`ModsConfig.xml`):

- **#5 Soft Ground** (Ta'Baa/Ishko, dunes) — the roster's own gating names
  the anchor directly: "dunes." Probed several dune-shaped defName guesses
  (`Dunes`, `AB_SandDunes`) rather than assuming either — `Dunes` came back
  **1 match** (`Data/Odyssey/Defs/TileMutators/TileMutators_Natural.xml`),
  confirmed by direct read: `biomeWhitelist: ExtremeDesert`, no
  `<extraGenSteps>` element of its own (only `preventGenSteps`). **This is
  the first whisper row this program has anchored on a vanilla BASE-GAME
  mutator** (every prior anchor was Odyssey-modded content, our own
  promise mutator, or a specific named mod's def) — the Add targets the
  TileMutatorDef node itself, same shape as Cavern/DryLake/Hollow/Caves.
  **Built**: `design/Jawa/templates/soft_ground.lua` — scattered
  `SculptureSmall` "warning cairn" markers across the whole footprint (6%
  density, floor of 1), the same substitute-prop discipline every prior
  whisper batch used (no "cairn"/"sink cell" ThingDef exists). **Scope
  declared, and it is a real engine gap, not just an authoring one**: the
  roster's own line is "natural sink-cells that behave as unrated pit
  covers... free kill-zone" — there is no pit mechanism in the engine to
  wire this to at all. `PIT_SUPERDEEP_COLLAPSE_1` is RULED (a pit is a
  SUPERDEEP cell, spikes only) but explicitly "nothing built" per that
  item's own record, so the active hazard cannot be built until that item
  ships engine-side, not merely until someone gets to it. `lint`: 0
  findings.
- **#17 Iron Rain** (Zizzik/Sh'kaar, ring-adjacent) — anchor
  `RUT_BrokenRing` (our own PROMISE #20 "The Broken Ring" mutator,
  `TileMutatorDefs_Batch5.xml`), confirmed by direct read of the repo's own
  file, same "ride our own promise's mutator" shape WHISPER #18 The Choir
  Wind already used for `RUT_Monument` — not live-probed via
  `validate_patch.py` because `mandrake.rut.injections` remains absent
  from the live `ModsConfig.xml` (declared since 2026-09-09; a probe of
  our own not-yet-enabled mod's own def would correctly report 0 matches,
  the same non-issue Choir Wind's own note already accepted). **Built**:
  `design/Jawa/templates/iron_rain.lua` — scattered `ChunkSlagSteel` (8%
  density) and loose `Steel` piles (5% density) across the footprint,
  guaranteed non-empty on the smallest legal size; both defNames confirmed
  real by direct read of `Data/Core/Defs/ThingDefs_Buildings/
  Buildings_Ancient_Indoors.xml` and `Buildings_Exotic.xml`. **Scope
  declared**: the roster's own line is "periodic small debris falls all
  stay" — this places the STATIC aftermath (debris that already fell and
  stayed, "free steel" made literal) only; the ongoing periodic-fall
  behavior is a GameCondition/repeating-incident this pass does not build,
  same class of gap as Rootstock's rain-trigger and Choir Wind's mood
  mechanic. `lint`: 0 findings.

**5 candidates investigated and explicitly rejected, not silently
skipped**:
- **#10 The Hollow Below** (vault-adjacent) — anchor would be
  `RUT_RakatanTrace` (PROMISE #9's own mutator, same "ride our own
  promise" shape used above), and no collision was found against
  `VAULT_DUNGEON_BUILD_1` (checked directly: that item builds six
  hand-placed KCSG `StructureLayoutDef` sites at fixed tile IDs, a wholly
  different mechanism from a mapgen-rolled whisper — no shared file, no
  shared defName). The real conflict is internal to this item instead:
  `rakatan_trace.lua` (PROMISE #9's own responder, already shipped) reads
  in full as "a sealed door and forecourt only... nothing opens yet" — it
  is already, explicitly, the sealed-door object. WHISPER #10's own line
  ("a cavern under the map with a sealed door... the knock comes on the
  third night") would place a SECOND sealed door on the exact same anchor
  mutator, duplicating rather than adding to the promise's own content.
  Left `MISSING-MECHANISM` rather than force a redundant second door;
  worth a line for whoever next touches this row — the fix is probably a
  design change to the promise's own forecourt (make the existing door
  the hollow's door), not a new object.
- **#4 The Wrong Spark** (Zizzik, broken places) and **#3 Old Reasons**
  (Rekko→Ishko, junker reads) — both rows' whisper-table lines name no
  specific mutator, only a god-country. Checked Zizzik's and Rekko's
  territory in `sacred_sites_pass_1.md` §1b/§1a directly: Zizzik's is
  `Wasteland` (a biome-class read, same architecture gap already confirmed
  for Ohm's `AB_MechanoidIntrusion` in batch 2 — no `TileMutatorDef`
  equivalent exists on a `BiomeDef`) plus the same `AB_MechanoidIntrusion`
  halo already rejected; Rekko's is `Ruins`/`AbandonedColonyOutlander`/
  `AbandonedColonyTribal`, all three explicitly **LandmarkDefs** per §1a's
  own table, same architecture limit already confirmed for #1/#16 in
  batch 2. Neither has an `extraGenSteps` hook to patch. Left
  `MISSING-MECHANISM`, honestly, same discipline as every prior "no
  nameable anchor" rejection.
- **#7 The Sun's Anvil** (Sh'kaar, arc<74), **#9 The Glimmer Field**
  (terminator), **#14 The Feud** (any wild band) — all three are arc-band
  or "any wild band" conditions, the exact class §0b's own architecture
  note already names as having "nowhere to attach unless the roster names
  an actual mutator." None of the three roster lines names one. Probed one
  candidate anyway rather than assuming the gap from prose alone
  (`AB_MycoticJungle`, the terminator's own defining biome per
  `sacred_sites_pass_1.md` §4 — a plausible #9 anchor): **0 matches**, and
  its own tile-count framing in that doc ("1,874 of 1,939 tiles at arc >
  82") reads as biome coverage, not mutator coverage, consistent with it
  being a `BiomeDef` like `AB_MechanoidIntrusion`. Also probed `Volcano`,
  `LavaField`, `Scarlands`, `AB_TarPits`, `AB_PyroclasticConflagration` as
  candidate Sh'kaar-territory anchors for a possible #19 Mirage Twin fit —
  all 0 matches (wrong guesses, not confirmed absent — the real Alpha
  Biomes/Geological-Landforms defNames were not chased further past one
  round of probing, since none of these rows' own roster lines names a
  specific mutator either). Left all `MISSING-MECHANISM`.

**Lint script updated** (not rewritten): `structure_roster_lint.py`'s
`WHISPERS` table rows #5 and #17 flipped from `"no-mechanism"` to
`"done"` with their slug/mutator filled in — no new checking logic needed,
the existing `check_whisper` mechanism (template + selector GenStepDef +
patch-onto-named-mutator, all three files independently re-verified
present on disk) already covers this shape. 🔴 **Caught and fixed a
same-session collision**: the first edit to this file was silently
overwritten on disk between the edit and the next lint run — the
system's own stale-file notice caught it, the file was re-read, and the
edit was reapplied and reconfirmed present before proceeding, per the
shared-worktree lesson (four seats, one checkout). `git diff --stat`
confirmed the final change is exactly 2 lines, nothing else touched.

**Wiring**: `Defs/GenStepDefs_Whisper_Batch3.xml` + `Patches/
WhisperBatch3.xml` (new, `mandrake.rut.injections`) for both rows, plus
`Templates/soft_ground.txt` and `Templates/iron_rain.txt` (rimplace
`export`, both baked at 8x8 — refuses below 4x4). `validate_patch.py`
against the whole `Defs/`+`Patches/` of `mandrake.rut.injections`, live
634-mod set: **0 errors, 0 warnings** on both new files (the two new
`PatchOperationConditional` probes each report 1 match — `Dunes` in
Odyssey's own `TileMutators_Natural.xml`, `RUT_BrokenRing` in our own
`TileMutatorDefs_Batch5.xml`). `rimplace lint` clean (0 findings) at 6x6,
8x8 and 20x20 for both templates; refusal confirmed firing at 3x3 for
both (`generator-refusal` + `empty-plan`, matching every prior template's
minimum-footprint convention). `rimplace verify`: **UNMEASURED** — the
local `defs.sqlite` capture is stale relative to today's capture
directory, the same gap every prior batch in this item has hit and worked
around the same way; defNames were instead confirmed via direct reads of
the live Data/Core/Odyssey source and the `validate_patch.py` probes
above, not asserted from memory. `rimplace selftest`: 62/62, unaffected —
this pass touched no engine/sandbox logic, only new content plus two
lint-table rows.

**NOT deployed, NOT added to ModsConfig this pass** — same discipline as
every prior batch; `mandrake.rut.injections` remains absent from the live
`ModsConfig.xml` exactly as found 2026-09-09, unrelated to and unchanged
by this pass. No bridge time used this pass — every check above is
offline (rimplace + validate_patch.py against on-disk source), matching
the dispatch's own "no blind live placement" instruction.

**Coverage after this pass: 16/22 promises (unchanged), 7/22 whispers (up
from 5/22), 0 coverage-law violations.** 15 whisper rows remain
`MISSING-MECHANISM`, honestly — most still have no `TileMutatorDef` anchor
at all (a `BiomeDef`/`LandmarkDef` architecture gap confirmed for 5 more
rows this pass) or are pure incident/timer mechanics with no physical
vocabulary to place; one (#10) has a real anchor but would duplicate
already-shipped promise content. Nothing invented to pad the count. Left
`doing` — 6 promise gaps still need an owner ruling or a design pass, most
whisper rows still have no mechanism, and the live mapgen-ordering proof
(owed since 2026-08-31) is still open.

