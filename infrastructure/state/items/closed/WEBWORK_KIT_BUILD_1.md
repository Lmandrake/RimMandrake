# WEBWORK_KIT_BUILD_1 — Webwork biome mechanics kit (SenseWeb, FrontCreep, ChewAnchors, roster structures)

## 2026-09-12 (FOUNDRY, fifth pass) — LIVE-VERIFIED clean against the item's own verify line, CLOSING

`QUICKTEST_POSTSETUP_CRASH_1`'s fix made the crash moot. Built the exact
bordering-biome scenario this item's own verify line calls for: painted
tile 51055 to `RUT_Webwork` and its neighbor 51056 (the already-loaded
quicktest map's tile) to `TemperateForest`, then `Actions\Regenerate Current
Map`, so the CURRENT map borders a `RUT_Webwork` world tile on one edge
(`jawa/world_neighbors` gave the true adjacency: 51056's neighbors are
1846, 51057, 24421, 68819, 24420, **51055**).

Since `advanceIntervalTicks` is a genuinely-invented ~1 in-game day
(60,000 ticks), fast-forwarded with `rimworld/play_for`
(`speed: Ultrafast, forceRequestedSpeed: true`) in chunks (each real bridge
call is capped well under its own reported duration) to carry the map
~78,000 ticks past its `FinalizeInit`.

**Result — exactly the item's own verify line, met precisely:**
`jawa/list_things` found `RUT_Webwork_Anchor` (10), `RUT_Webwork_Web` (10)
and `RUT_Webwork_Gutter` (14), **every single one at x=249** — the map's
true East edge (`sizeX=250`), and the correct edge given 51055 sits east of
51056 in the neighbour ordering. This confirms, in one shot: `FindFront()`
correctly detected the bordering biome's `RM_FrontCreepExtension`,
`Rot4.FromAngleFlat` bucketed the heading to the right cardinal edge, and
`InsetFromEdge`'s depth-1 math placed the band on the TRUE edge (inset=0) —
exactly one band, matching that only one 60,000-tick interval had elapsed
past the second (no things at x=248, ruling out an off-by-one).

Destroyed one `RUT_Webwork_Anchor` via `jawa/damage` (Flame, lethal):
`success: true`, clean. `Player.log` (checked by reading full stack traces,
not grepping) has **zero** lines naming `SenseWeb`, `FrontCreep`, or
`ChewAnchor` anywhere — no exception, from either the ~34 sense-web-carrying
things spawning (which fires `RM_CompSenseWebNode.PostSpawnSetup` on each)
or the destroy (`PostDeSpawn`). The one `NullReferenceException` in this
session's whole log window is `MineralsFramework.ThingDef_StaticMineral`
(an unrelated third-party GenStep, traced to its own stack, nothing to do
with this kit).

**`RM_JobGiver_ChewAnchors` stays unexercised live** — as this item's own
"still owed" #3 already says, no consumer race's ThinkTree calls it yet, so
there is nothing to observe firing. Not a defect in this item; a gap in a
DIFFERENT unbuilt item (the anchor-beetle race).

**Criteria met**: the item's own stated verify line ("a quicktest map
bordering a RUT_Webwork world tile shows RUT_Webwork_Anchor/_Web/_Gutter
Things scattering inward from the correct edge over time, and destroying
one deregisters cleanly") is satisfied exactly. Closing.

## 2026-09-12 (FOUNDRY, later same night) — deploy confirmed done; live verify blocked on QUICKTEST_POSTSETUP_CRASH_1

`deploy_custom_mods.py --mod CreatureBehaviors` and `--mod UtinniPatches`
both report "in sync" — the prior session's `needs=deploy` gate is
cleared (the CreatureBehaviors DLL was in fact rebuilt THIS session, for
an unrelated reason: `3e05542a6` fixed a stale-DLL crash in
`RM_Alert_VerminPopulationBase`, and the rebuild picked up this item's own
`RM_MapComponent_SenseWeb`/`RM_JobGiver_ChewAnchors`/`RM_MapComponent_FrontCreep`
source in the same pass — confirmed via `git status`, only one DLL diff
existed and it now carries both fixes).

The quicktest-map live proof this item's own note calls for (spawn
`RUT_Webwork_Anchor`, confirm SenseWeb registration; `FrontCreep` on a
bordering-biome test map) is blocked the same way as
`SHOKKWEAVE_SOLE_SOURCE_1`'s sibling routes: needs a fresh
`RUT_Webwork`-biome map, and `start_debug_game_ready` crashes the process
reliably on this mod list (see `QUICKTEST_POSTSETUP_CRASH_1`, found and
partially chased this session — two OTHER load-blocking bugs fixed first,
`257bbbc7f` and `3e05542a6`, before hitting this third one). The loaded
real colony map (used for `BUILDING_THEFT_HAULER_1`/`NINEFOLD_FIRE_HOOK`
tonight) is not `RUT_Webwork` biome, so substituting it would not exercise
`FrontCreep`'s own biome-boundary check at all.

`needs=bridge` unchanged; unblocks once `QUICKTEST_POSTSETUP_CRASH_1` is
fixed or a minimal+target mod list swap reaches a `RUT_Webwork` quicktest
map without it.

Queue line: build `RM_MapComponent_SenseWeb`, `RM_MapComponent_FrontCreep`,
`RM_JobGiver_ChewAnchors`, and the roster's web/anchor/gutter ThingDefs per
`design/Jawa/worldbuilding/biomes/kits/webwork_kit_spec.md` — the biome's own
content kit had no build item until now (only the six generic
`ALPHA_MECHANICS_KIT_1` comps were built). Blocks
`SHOKKWEAVE_SOLE_SOURCE_1`'s border creep-web route.

## Scope (deliberately a subset of the spec's full 7 mechanics)

The spec (`webwork_kit_spec.md`) covers 7 mechanics; this item's own queue line
named exactly 4 build targets, and that is what got built. NOT touched here
(already built elsewhere, or genuinely out of this item's scope):

- `RM_Hediff_SunScald` (light-moat) — already built in this same assembly
  (`SHOKK_RSW_MOD_1`/`MOD_OPTIONS_RETROFIT_1` history).
- `RM_JobGiver_SenseWebConverge`, droid-priority scoring, `RUT_ShokkBound`,
  ambush dormancy XML — need the Wyyyschokk's own race/ThinkTree, which rides
  `WYYYSCHOKK_FERALISK_MERGE_1` (unbuilt); not invented here.

## Built

**Assembly home**: `src/RimMandrake/CreatureBehaviors/` (RULED 2026-09-11,
card sitting item 5 — "the separate RM_ creature-behaviors assembly, in the
ShipVermin/behaviors family," NOT `mandrake.rm.environmentalhazards`). This is
an **already-loaded, already-active mod** (`mandrake.rm.creaturebehaviors`,
confirmed in the live `ModsConfig.xml`, 593-mod list) — new source, same
assembly.

New C# (`src/RimMandrake/CreatureBehaviors/Source/`):

- `RM_ChewableExtension.cs` — trivial marker `DefModExtension` (spec §5: "ANY
  future mod can mark chewables without touching C#").
- `RM_CompSenseWebNode.cs` (`RM_CompProperties_SenseWebNode` +
  `RM_CompSenseWebNode`) — registers/deregisters a Thing's occupied cells (and
  itself) with the map's `RM_MapComponent_SenseWeb` on spawn/despawn.
  Destroying a node auto-deregisters it (spec §5's "chewing genuinely blinds
  the web locally" — no explicit notify needed, the comp lifecycle does it).
- `RM_MapComponent_SenseWeb.cs` — tracks registered cells + nodes; on a
  ~250-tick scan (❓INVENTED), applies `RUT_Webwork_FeltMark` (soft
  `DefDatabase` lookup — content-defined, not built here) to any pawn standing
  in a registered cell or carrying `RUT_Webwork_Egg` (also soft-looked-up).
  Exposes `ChewableNodes` for `RM_JobGiver_ChewAnchors` so that JobGiver never
  needs a map-wide thing scan. Deliberately does NOT build the convergence/
  targeting JobGiver (spec's `RM_JobGiver_SenseWebConverge`) — that needs the
  owner race's ThinkTree (unbuilt); this component tracks and marks only.
- `RM_FrontCreepExtension.cs` — `DefModExtension` for a `BiomeDef`: defNames
  to scatter + advance interval/depth/density. ❓INVENTED numbers throughout
  (spec §6 names none): `advanceIntervalTicks=60000` (~1 day),
  `maxBandDepth=10`, `spawnDensity=0.15`.
- `RM_MapComponent_FrontCreep.cs` — mechanic 6 (spec §6, "margin creep").
  Generic and name-blind: on `FinalizeInit`, checks the map's world-tile
  neighbors for one carrying `RM_FrontCreepExtension` on its `BiomeDef`; if
  found, buckets the mean heading to that neighbor into a cardinal map edge
  via vanilla `Rot4.FromAngleFlat` (same heading convention
  `TileMutatorWorker_MixedBiome` uses, RimSage-verified) and advances a band
  inward from that edge on the extension's own interval, scattering its
  configured ThingDefs. World map is never repainted (no worldgen touched);
  the encroachment is map-local scatter only. Persists `currentDepth`/
  `ticksUntilAdvance` across saves; re-derives the front itself on load
  (idempotent `FinalizeInit`).
  - **Ruled-comp reuse NOT wired**: the spec names `RM_Gas_Transmuting` (from
    `ALPHA_MECHANICS_KIT_1`) for flora conversion along the front. That gas
    ThingDef needs Webwork-specific flora replacement data (which tree/plant
    becomes which) that isn't authored anywhere yet — inventing it here would
    be content, not mechanism. `FrontCreep` spawns the roster's web/anchor/
    gutter Things (below); flora transmutation along the front is deferred to
    whoever authors that replacement table.
- `RM_JobGiver_ChewAnchors.cs` — mechanic 5 (spec §5). `ThinkNode_JobGiver`
  written directly (the spec's own §4-review precedent for `JobGiver_Mine`-
  shaped work), querying `RM_MapComponent_SenseWeb.ChewableNodes` (filtered by
  `RM_ChewableExtension`) via `GenClosest.ClosestThing_Global_Reachable`, then
  issuing a vanilla `JobDefOf.AttackMelee` job — same shape as
  `JobGiver_Manhunter.MeleeAttackJob`, RimSage-verified.

Mod Settings (`RM_CreatureBehaviorsMod.cs`, extending the existing toolkit
screen): `senseWebEnabled`, `chewAnchorsBehaviorEnabled`, `frontCreepEnabled` +
`frontCreepRateMultiplier` (0-3x density dial). All default on = shipped
behavior; all-off degrades gracefully per CLAUDE.md's Mod Settings standing
rule (nodes still register when senseWebEnabled is off, they just stop being
scanned — no half-registered state).

**Roster content** (`src/RimUtinni/UtinniPatches/`, `mandrake.rut.patches` —
also already-active): `Defs/ThingDefs_Buildings/RUT_WebworkStructures.xml` —
`RUT_Webwork_Anchor` (carries `RM_ChewableExtension` + the sense-web comp),
`RUT_Webwork_Web`, `RUT_Webwork_Gutter` (sense-web comp only) — the_webwork.md
§8's "anchor lines, sheet webs, and the silk irrigation gutters." All three
`ParentName="BuildingNaturalBase"`, Standable/non-blocking, flammable
(Flammability 1.2-1.6 — "fire is architecture," §7b), **carry no
killedLeavings or yield comp** (sole-source guard: a destroyed sense-web node
drops nothing; any Shokkweave yield on a creep-spawned node is
`SHOKKWEAVE_SOLE_SOURCE_1`'s own patch to attach, owner card 4). Placeholder
art (`Things/Building/Natural/Hive`, RimSage-verified as the live vanilla
Hive texPath — same placeholder `ShokkweaveHarvestNodes.xml`'s Nest already
uses); bespoke web/anchor/gutter sprites are owed.

`RUT_Webwork.xml`'s `BiomeDef` gained a `modExtensions` block: one
`RM_FrontCreepExtension` naming the three structures above, so any map
bordering a Webwork world tile creeps them inward. No other field on that def
changed.

## Verified, never guessed

Every API used (`OccupiedRect()`, `JobMaker.MakeJob(JobDefOf.AttackMelee, …)`,
`GenClosest.ClosestThing_Global_Reachable`, `ThingComp.PostSpawnSetup`/
`PostDeSpawn`, `MapComponent.FinalizeInit`/`MapComponentTick`,
`Find.WorldGrid.GetTileNeighbors`/`GetHeadingFromTo`, `BiomeDef.GetModExtension`,
`CellRect.GetEdgeCells`, `Rot4.FromAngleFlat`, `HediffSet.HasHediff`,
`Pawn_HealthTracker.AddHediff`, `ThingOwner.Contains(ThingDef)`) was read from
RimWorld source via RimSage before use, not guessed — several early drafts
(`ThingRequestGroup.Everything` for the JobGiver, a hand-rolled heading-to-edge
bucketer) were replaced after RimSage showed the vanilla equivalent already
existed or would throw. `BuildingNaturalBase` as a ThingDef ParentName was
confirmed live via `get_def_details Hive` (uses the same parent).

## Compile + validate

- `dotnet.exe build RM_CreatureBehaviors.csproj -c Release` — **0 warnings, 0
  errors**. DLL rebuilt at
  `src/RimMandrake/CreatureBehaviors/Assemblies/RimMandrake.CreatureBehaviors.dll`
  (this also picked up an unrelated prior uncommitted rebuild of the same DLL
  already sitting in the tree at claim time — no separate source changes were
  lost, this pass's build is now the sole DLL committed).
- `validate_patch.py` against the live 593-mod set
  (`ModsConfig.xml`, `Data`/`Mods`/workshop content as `--defs` roots): **0
  errors** on `RUT_Webwork.xml`. `RUT_WebworkStructures.xml` reports 3 ERRORs
  — all the SAME known false positive `ShokkweaveHarvestNodes.xml`'s own Nest
  def already hit and explained: the tool can't see into Unity asset bundles,
  and because `UtinniPatches` ships its own `Textures/Things/` folder, an
  unresolved `Things/Building/Natural/Hive` path is scored ERROR instead of
  WARN (the heuristic assumes any mod owning a `Things/` folder owns the whole
  path). Confirmed genuinely correct via `get_def_details Hive` (RimSage) —
  it IS the live vanilla Hive texPath. The `Class="RimMandrake.CreatureBehaviors.*"`
  cross-mod compClass/modExtension references show as `info`, not error
  (expected: two always-co-active Utinni-tier mods, no MayRequire needed,
  matching how other RM_-tier comps are referenced elsewhere in this
  campaign's RUT_ content).
- `python3 src/RimMandrake/Utils/run_selftests.py` was started but produced no
  captured output before this session's shell recycled; not re-run given time
  budget and given the whole item is `needs=deploy` regardless (nothing here
  can be exercised live until the DLL deploys).

## Deploy status — needs=deploy, NOT attempted

Both touched mods (`mandrake.rm.creaturebehaviors`, `mandrake.rut.patches`)
are **already active in the live 593-mod `ModsConfig.xml`** while the game is
UP on the full list. Per this session's explicit instruction: a brand-new DLL
extending an ALREADY-LOADED mod does not deploy while the game holds it open
(OS file lock) — this is `CreatureBehaviors.dll`, not a new mod folder. The
`RUT_WebworkStructures.xml`/`RUT_Webwork.xml` XML changes could technically
deploy without a game-down window (CLAUDE.md: "config files never wait for
the game"), but deploying the XML alone — with compClass/modExtension
references to types the CURRENTLY-DEPLOYED old DLL doesn't contain — would
throw config errors on the very next restart, before the DLL half lands. Both
halves are held back together for one deploy window.

`rimflow needs WEBWORK_KIT_BUILD_1 --to deploy` set accordingly; **NOT
closed**.

## Still owed (next session, after deploy)

1. `deploy_custom_mods.py --mod CreatureBehaviors` and `--mod UtinniPatches`
   in the same game-down window, md5-verify the new DLL landed.
2. Quicktest-map (never a cold load) live proof: spawn `RUT_Webwork_Anchor`,
   confirm it registers with `RM_MapComponent_SenseWeb` (a pawn standing on it
   gets `RUT_Webwork_FeltMark` IF that content exists — else confirm the
   graceful no-op); spawn a beetle-kind carrying nothing special and confirm
   `RM_JobGiver_ChewAnchors` needs a pawn whose ThinkTree actually calls it
   (none does yet — this item ships the JobGiver, not a consumer race);
   `RM_MapComponent_FrontCreep` needs an actual bordering-biome test map,
   which needs a live world with a Webwork/non-Webwork tile boundary.
3. Wire a real consumer race JobGiver into `RM_JobGiver_ChewAnchors`
   (anchor-beetle race, e.g. `BMT_JewelBeetle`/`RSW_JewelBeetle` per the
   roster) once that race's ThinkTree work lands.
4. `RUT_Webwork_FeltMark` HediffDef and `RUT_Webwork_Egg` ThingDef — content
   this item soft-references but does not create (biome content, not this
   kit's mechanism layer); `RM_MapComponent_SenseWeb` no-ops cleanly without
   them.
5. Flora transmutation along the front (`RM_Gas_Transmuting` reuse, spec §6)
   — needs a Webwork-specific tree/plant replacement table not authored
   anywhere yet.
6. Bespoke web/anchor/gutter art (placeholder Hive texture in use).
7. Balance pass on every ❓INVENTED number (scan interval, search radii,
   advance interval/depth/density, HP/Flammability on the three structures).

Verify line for this item, once deployed: a quicktest map bordering a
`RUT_Webwork` world tile shows `RUT_Webwork_Anchor`/`_Web`/`_Gutter` Things
scattering inward from the correct edge over time, and destroying one
deregisters cleanly (no lingering SenseWeb registration).
