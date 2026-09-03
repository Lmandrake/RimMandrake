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
