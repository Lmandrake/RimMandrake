# BRIDGE_PAWN_THOUGHTS_CARAVAN_GAP_1 — `jawa/pawn_thoughts` cannot read a caravan pawn

Surfaced 2026-09-02 trying to live-verify `TravelCompanions` (a
`Thought_Situational` from Caravan Adventures that only evaluates while a
pawn is actually IN a caravan) for `PAWN_FLAVOR_SILENT_NONAPPLY_1`. Formed
a real caravan via `jawa/caravan_create` with 3 quicktest colonists, then
called `jawa/pawn_thoughts` on one of them by both bare id and name —
both refused: `"No spawned pawn matching '<x>'. N pawns are spawned."`
Caravan members are world pawns (de-spawned from the map, tracked via
`WorldObject_Caravan`), and `jawa/pawn_thoughts`'s pawn lookup only
searches spawned map `Thing`s (`FindPawn`, same helper `jawa/list_pawns`
etc. use) — it never checks `Find.WorldPawns` or a caravan's own pawn
list.

## spec

Any `jawa/pawn_*` tool that resolves a pawn by id/name should also try
`Find.WorldPawns.AllPawnsAlive` (or the specific caravan's
`PawnsListForReading`) when the map lookup misses, so a pawn currently in
a caravan (or otherwise off-map: a prisoner in transit, a wounded pawn on
another map, etc.) is reachable the same way. This is squarely
`rimbridge-companion` territory (`JawaBench.BridgeTools`), not a
`rimbridge`-skill driving question.

## verify

- `jawa/pawn_thoughts` (or a shared `FindPawn` helper used by several
  tools — check for one before touching each call site individually)
  finds a caravan-member pawn by id and by name.
- Re-run the actual motivating case: form a caravan of colonists who don't
  know each other well, read `TravelCompanions`'s live stage/text off one
  of them, confirm it reads the Phase-2-approved prose rather than
  vanilla ("Third wheel" etc.) — this is the live proof
  `PAWN_FLAVOR_SILENT_NONAPPLY_1`/`PAWN_FLAVOR_PHASE2_APPLY_1` are still
  owed for their DLC/workshop-mod-owned rows.

## criteria

A caravan pawn's thoughts are readable via the bridge without dissolving
the caravan first, and the `TravelCompanions` live text check above
passes or fails on real evidence (not blocked on tooling).
