# INHABITED_TILEMUTATOR_NO_ENTRY_1

Found 2026-09-03 while building `INHABITED_STOCK_ONTO_MAP_AND_FATE_1` — a second,
independent reachability gap discovered on the way, same shape as
`INHABITED_SETTLEMENT_MAPPARENT_GAP_1` but on the OTHER of the mod's two intended
entry routes.

## spec

The Inhabited mod's own class comments describe two routes onto a map: a proper
`WorldObject_InhabitedSettlement` (blocked by `INHABITED_SETTLEMENT_MAPPARENT_GAP_1`
— it isn't a `MapParent`, so `Inhabited_SettlementMapGenerator` never runs), and a
wilderness route via a `TileMutatorDef` that fires `GenStep_ComposeSettlementDistrict`
/ `GenStep_InhabitedStock` (order 900/910) on an ordinary map tile.

**Checked by grep across `src/` and `deployed/`: no `TileMutatorDef` anywhere in the
build set names any of this mod's GenSteps.** The four mutator files that exist
(`StructureInjectionsSW`, `StructureInjectionsRUT`) don't reference this mod at all.

⇒ Neither route currently executes. The whole Inhabited settlement mechanism —
294 authored characters, the roster lifecycle fixes, the stock/fate wiring — compiles
clean and has never once run in a real map generation, because nothing calls it.

## verify

Author (or find, if one was meant to exist and got dropped) a `TileMutatorDef` that
fires this mod's GenStep(s) on a wilderness tile, deploy, and confirm via Player.log
or a debug action that `GenStep_ComposeSettlementDistrict`/`GenStep_InhabitedStock`
actually ran on a real map generation — not just that they compile.

## criteria

At least one route (wilderness mutator, or `INHABITED_SETTLEMENT_MAPPARENT_GAP_1`
resolving) actually reaches this mod's map-gen code in a live game.

## Partial live progress (2026-09-04, FOUNDRY, minimal-list quicktest)

**Deploy check first:** the "stale Assemblies/Inhabited.dll and GenStepDefs
(missing RM_InhabitedStock)" blocker recorded on the queue was already stale —
`deploy_custom_mods.py --mod Inhabited` reports in sync, and an md5 check
confirmed the deployed `Inhabited.dll` is byte-identical to the repo copy,
`RM_InhabitedStock`/`Inhabited_Cast` GenStepDefs are deployed too. No deploy work
was actually needed.

**Wiring confirmed non-crashing:** added `RM_InhabitedPlace` (this item's own
TileMutatorDef fix) to an empty world tile via `jawa/world_mutators_set` +
`world_commit`, then generated a real map there via `jawa/world_tile_map_generate`
— succeeded cleanly, 71 pawns, no exception. Rules out an engine-level wiring
defect: the mutator's `extraGenSteps` get concatenated into the step list and run
without crashing.

**"Does the cast/stock actually spawn" NOT conclusively proven live.** No
`[RimMandrake.Inhabited] put N of...` (GenStep_InhabitedStock's success line) or
any other mod log line appeared on that first map — expected, because per
`GenStep_InhabitedCast.cs`'s own doc comment a `WorldObject_Inhabited` must ALSO
sit on the tile with a real `placeDef` for either GenStep to do anything (both
silently no-op with zero logging otherwise, confirmed by reading both GenStep
source files in full). Set that up properly the second time — used this mod's own
debug actions (`Actions\Create place at current tile` + `Actions\Stuff roster (3
pawns)`, both plain `Action` type, no interactive picker needed) to get a real
`Inhabited_Place` object with a rolled 3-pawn roster (`Player.log`: "created Test
place... archetype RM_InhabitedPlace_Scrapyard", "roster... now holds 3"), moved
it with the mutator onto a fresh tile via `jawa/world_objects_set`, and called
`world_tile_map_generate` again.

**Blocked on a bridge tool defect, not this mod.** That second
`world_tile_map_generate` call — the SECOND call to that tool in one session, at a
DIFFERENT tile than the first — silently failed to create a new map while
reporting fabricated success (`wasAlreadyGenerated: false`, plausible-looking but
different pawn/thing counts). Cross-checked independently: `rimworld/get_game_info`
`mapCount` never grew past 2, and `jawa/map_info` (reads `Find.CurrentMap`
directly) showed the "current" map was still the FIRST test's tile, not the
second one. **Recorded in `skills/rimbridge/references/traps.md`** as a new
finding — this tool cannot be trusted for a second distinct-tile call per
session, full evidence there.

## What's actually still open

Narrower than before: not "does this route get reached at all" (now answered:
yes, cleanly), but specifically "does `InstantiateCast`/`DumpOnto` actually place
the roster and stock once a properly-configured `Inhabited_Place` is present at
generation time." Needs either a fixed/reconnected `world_tile_map_generate`, a
freshly restarted bridge session (clears whatever internal state made the second
call misbehave), or forming a real caravan and walking it onto the tile (the
actual vanilla trigger mechanism, heavier but not tool-dependent).
