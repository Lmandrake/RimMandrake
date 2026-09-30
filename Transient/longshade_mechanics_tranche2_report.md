# LONGSHADE_BEDAZZLE_MECHANICS_1 — tranche 2 report

Status: LANDED, tranche 2. The item stays open for its quicktests and the smoke-calendar haze. 2026-09-29. Nothing deployed or live-tested.

## Substrate read
- Patch graph: `RM_ShadePatchGraph` (patches, rims, distToShade field, edges) and `RM_MapComponent_ShadeGrid.PatchGraph`; dash job `RM_ShadeDash` via `RM_ShadeHop.MakeDash`; `RM_DashMath` for ranges. Reused, not copied.
- Shade gear: `RM_Parasol` (`RM_CompProperties_ShadeGear`, wearer mode), read through `RM_SunHeatMath.GearDepth` for the Long Carry's reach test.
- Sarlacc: `CompSarlaccSwimmer` (reserve, rooting, tranche-1 take sign), `RSW_SarlaccAnchored`. The swimmer runs Anomaly's `Devourer` think tree, which has a `Devourer_PreWander` insert tag (RimSage) — the road job giver goes there.
- Engine (RimSage): `BiomeDef.extraGenSteps` is concatenated by `MapGenerator.GenerateMap`; `Plants` GenStep is order 900, `Animals` 1200; `Designator_Uninstall` accepts an unowned building when `building.alwaysUninstallable`; `ConsumeLeap_Devourer` range 9.9, max prey body size 2.5; `Ability.GetJob(target, dest)`.
- Crawler terminus: `RSW_GenStep_DeadCrawler`'s plan (`dead_crawler.txt`) through `GenStep_RimplacePlan.anchorThingDef`.

## Art check (mirrak, wrecks, kill-sign decals)
Searched `infrastructure/artpipe/{done,_artsrc,pending,active}` in the LIVE tree (`D:\Luke\dev\Rimworld`; the worktree only has the committed `pending/` copies). Probe: `hawkbat` 18 hits in done+_artsrc. All eight renders this item queued are FINISHED (`done/*.manifest.json` status ok, PNGs in `_artsrc/`, RGBA with real alpha, looked at):
`RM_Mirrak_{south,east,north}` (256), `RM_Filth_DisturbedSand`, `RM_Filth_DragMark` (256), `RM_WreckedCart` (256), `RSW_CrawlerTreadWreck`, `RSW_WreckedSkiff` (512x256). Wired this tranche (see below).

## Part 3 — Swimmer's road (RSW, `mandrake.rsw.sarlacc`)
- `RSW_SwimmerRoad` IncidentDef (Misc, earliest day 20) + `RSW_IncidentWorker_SwimmerRoad`. Gate: biome defName list in `RSW_SwimmerRoadExtension` (`RM_LongShade`), Creature Behaviors active, a patch graph present (sun heat on, heat kind not ambient), a ring of at least 8 soft rim cells, and **`RSW_MapComponent_SwimmerRoad.fired` — set when it fires, never cleared: one per map, ever.**
- Target = the patch with the most rim cells on diggable, unfloored terrain (the "largest dew ring on soft sand"), aimed at the patch cell nearest its centroid; re-picked only if that patch disappears. Entry = the soft-ground edge cell farthest from it (12 tries) that can reach it.
- `RSW_JobGiver_SwimmerRoad` in the Devourer tree's `Devourer_PreWander` slot (the swimmer runs Anomaly's Devourer tree): (1) leap (`ConsumeLeap_Devourer`, the shipped ability) at flesh standing on a dew line (rim cell or open cell within one diagonal of shade) in range + line of sight — droids are never taken; (2) else the next hop by Dijkstra over the patch graph, issued as the shared `RM_ShadeDash` (walk to rim, pause 90–240 ticks, sprint); in the open it dashes to the nearest shade; with no chain it walks the gap to the ring.
- Rooting: the component's 250-tick check roots it (`CompSarlaccSwimmer.RootAtDewRing`, new, reuses the shipped rooting) once it is inside the target patch within 2.9 cells of the centre and not digesting. Every wild animal in that patch is sent out at once (a `RM_ShadeHop.TryFindHop` dash to a neighbouring patch, else a vanilla flee) and a letter names the rooting and the count that fled.
- Signs: a swallow now also lays `RM_Filth_DisturbedSand` (new kit filth, art wired) where it went under, on top of tranche 1's churned sand and message. The swimmer's inspect pane shows its water reserve.
- Tier/deps: Sarlacc gains a soft `loadAfter` on Creature Behaviors and a compile reference to its DLL. All CB-typed code sits in `RSW_SwimmerRoadLogic`, reached only after `ModsConfig.IsActive("mandrake.rm.creaturebehaviors")`.

## Mirrak roster row (part 2 follow-on)
Art wired to `D:\Luke\dev\Rimworld\src\RimMandrake\LongShade\Textures\Things\Pawn\Animal\RM_Mirrak\RM_Mirrak_{south,east,north}.png`; `RM_Mirrak` added to `RM_LongShade` wildAnimals at **0.05** (the dakkra's weight, the other rare ambusher — a first value, not a ruling); `AnimalExotic` trade tag (the old comment held it back only for art). Its seizure now lays `RM_Filth_DragMark` (1 decal). About.xml: 22 native creatures.

## Kill-sign decals (kit, Creature Behaviors)
`RM_Filth_DragMark` and `RM_Filth_DisturbedSand` (`CreatureBehaviors\Defs\ThingDefs_Misc\RM_KillSigns_Filth.xml`), `BaseFilth`, `Graphic_Random` over their folders (the `Filth_BlastMark` shape). Mirrak → drag mark; swimmer → disturbed sand (by name, falls back to `Filth_Sand`).

## Part 4 — Crawler Road
- `RM_GenStep_CrawlerRoad` (LongShade DLL, `RM_LongShadeMapgen.cs`), order 950 (after Plants 900, before Animals 1200), named only in `RM_LongShade.extraGenSteps`.
- Link spacing = 0.8 × a baseline human's one-way sun budget (the §6 ring arithmetic with the Human race def: `RM_SunHeatMath` + `RM_DashMath`, ring budget 0.035), capped by the animals' `maxDashCells` so herds can use the road too, clamped 6–24 cells.
- "Widest gap": the patch graph is built (from the grid's own layers, own terrain/edifice walk mask — the path grid and rooms are not settled mid-generation) with edges no longer than that spacing; patches are grouped into islands; the road crosses the shortest open stretch between the two biggest islands (rims sampled to 300 each). No road when the shade network is already whole or the gap is under 1.5 spacings or over 160 cells.
- Links cycle through `linkDefs` on clear Light-affordance ground within 4 cells of each stop. RM tier: `RM_WreckedCart` (2x2, shadow height 0.8). RSW tier (`mandrake.rsw.injections`, patched in with `PatchOperationConditional`): `RSW_WreckedSkiff` (4x2, 1.0) and `RSW_CrawlerTreadWreck` (4x2, 1.3), plus `terminusStep` = `RSW_GenStep_CrawlerRoadTerminus`: the shipped `dead_crawler.txt` plan through `GenStep_RimplacePlan.anchorThingDef`, centred on a transient `RM_CrawlerRoadTerminus` marker the road spawns at its last stop and destroys after.
- Every wreck: `staticSunShadowHeight` (the grid's caster scan and the rendered shadow), deconstructible for its costList, **minifiable and uninstallable while unowned** (`building.alwaysUninstallable`). Stripping or moving one opens a hop longer than a dash, so the shade-hop AI stops crossing there; reinstalling one (or pitching a shade tent) mends it. No new AI: the herd-stops-at-the-gap behaviour is tranche 2 of SOLAR_HEAT's existing edge-range rule.

## Part 5 — Long Carry
- `RM_GenStep_SunGraves`, order 960, same gate. Graves go where the walk to the nearest shade `d` satisfies bare-human ring < 2d ≤ parasol ring (the parasol's depth read from `RM_Parasol`'s own `RM_CompProperties_ShadeGear` through `RM_ShadeGear.DepthOf`), i.e. **reachable out-and-back only with shade gear**. If the sun is too mild for gear to matter, they go ≥ 40% of the ring cap out. 1–3 graves, 20+ cells apart.
- Each: a dessicated `Drifter` in their gear, a dessicated `Dromedary` beside, a spilled load (silver 80, 2 components, 4 herbal medicine, 20 pemmican — first values), and a vanilla `Novel` half the time. 🔴 Lore and salvage only; nothing points anywhere (gnomon line CUT).

## Mod Settings (all default on)
- Long Shade: "The Crawler Road" and "The Long Carry (sun graves)", both labelled MAP GENERATION.
- Sarlacc: "Swimmer's road incident" and "Rooting empties the patch".

## Verification
- `dotnet build` Release: `Sarlacc.csproj` 0 errors, `RM_LongShade.csproj` 0 errors. Both DLLs committed with `.srchash`. Creature Behaviors C# untouched (defs + textures only).
- All 10 touched/new XML files parse; `RM_LongShade` wildAnimals parsed as elements: 22, last `RM_Mirrak`.
- `run_selftests.py`: 77/79 — the known `selftest_deployed_biome_refs` failure, `bridgetools/selftest_tool_metadata` unmeasured. Same as the tranche-1 baseline.
- Nothing deployed, nothing run in the game.

## Remaining / needs art, audio or an owner call
- **Quicktests (all unverified in game):** swimmer road on a Long Shade map — incident fires once, swimmer hops rim to rim, leaps at dew-line prey, roots at the ring, tenants flee, never fires again on that map; that a faction-less Devourer-tree pawn generates and behaves (it was only ever spawned by debug before); Crawler Road placement on real terrain, the terminus plan landing in the gap, uninstall/reinstall of an unowned wreck; graves' band on a real map and the mapgen-time grid recompute.
- **Mirrak haze behaviour** — waits on the unbuilt smoke calendar (seam: `RM_MapComponent_PinnedSun.ShadowLengthFactor`).
- **Not built, each needs a ruling or more content:** the swimmer visibly slowing as its water drops (reserve now shown on the inspect pane only); hardpan/paved-floor moat the swimmer cannot cross (needs `RM_Hardpan`, review slate #6); the wet, darkened dew line at a rooting (needs a decal — art); the crawler's dormant droid crew (§6.4, RSW/Utinni content); a `RSW_WreckedLandspeeder` link (the landspeeder is Core's `AncientPodCar` reskinned, non-minifiable, so it is not in the road); hitchhiking animals running to a parasol-bearer's shade (the patch graph still ignores parasol shade — SOLAR_HEAT tranche 2's known gap).
- **Audio:** the swimmer's under-sand grinding and the wrecks' ticking metal (§6.3/6.4 "What you hear") — no audio pipeline.
- **Owner-tuned numbers:** mirrak weight 0.05, incident base chance 0.6 / earliest day 20, road spacing factor 0.8, grave load, grave count.
