## spec
§4 of the design. The displaced pool is a `GameComponent`; any cast being
instantiated draws from it BEFORE generating anyone new, and that one ordering
rule is the whole recurring-character effect.
Debug actions: `Absorb roster into pool` · `Report displaced pool` ·
`Draw 3 from pool`.

## verify
absorb 3, save, quit to desktop, reload, `Report displaced pool` -> the same 3
with the same `ThingID`s, reasons and origins. Then `Draw 3 from pool` -> 3
distinct pawns returned and the pool left empty.

## criteria
🔑 the real one, and it needs two places of one faction: raid a cast, leave,
land on a second place of the same faction, and at least one person there is a
survivor of the first — same name, and RimWorld's own opinion system already
knows what the player did to him.
⛔ **There is no morality system in this mod and there must never be one.** If
anything in play reads as a karma score, a reputation number or a "the world
disapproves" popup, that is a defect — report it as one.

## notes
**from:** BUILD, 2026-08-20, `f0a9f6c`. Depends on `ROSTER_SOAK_100_DAYS_1` passing.

**Imported from `queue/CHECK.md`. Its `state:` read, verbatim:**

blocked on content — no `InhabitedPlaceDef`/`InhabitedCastDef` instances exist
yet, so there is no second place to land on. The save/load half above is
runnable now.
