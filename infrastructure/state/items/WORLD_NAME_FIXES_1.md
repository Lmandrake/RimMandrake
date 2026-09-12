# WORLD_NAME_FIXES_1 — world name fixes (owner 2026-09-12)

## 2026-09-12 (FOUNDRY) — Colony rename done and live; renames needing card picks stay open

Batched with `SARLACC_WORLDMAP_RELOCATE_1` and `VAPOR_PLACEMENT_CLEANUP_1`
(same session, same loaded `CANONICAL_ASHKARR_2026-09-09` save, one Saves
backup + one re-save covering all three — see `SARLACC_WORLDMAP_RELOCATE_1`'s
note for the full freeze-discipline write-up).

**Done — the ruled half**: renamed the player settlement from "Colony" to
**"Zeddo's Salvage Yard"** (owner, verbatim on the filing event). Found it
via `jawa/world_objects_get {def:Settlement, faction:PlayerColony}` (id
255, tile 16869 — `faction:"Player"` returns 0 hits, the live faction
defName is `PlayerColony`, not guessed). Renamed with
`jawa/world_objects_set {ids:255, name:"Zeddo's Salvage Yard"}`,
`jawa/world_commit`, read back clean (`label`/`name` both now "Zeddo's
Salvage Yard").

**NOT done, correctly left open**: the item's own title also carries "Fall
Line Barrens + Scald Spine near-dups and the four Ascendant Helix
settlement renames land here once the owner picks from the proposal
cards" — that half is gated on an owner decision that has not landed
(`needs=decision` set below, not `needs=bridge` — a live pass cannot manufacture
the owner's pick). Whoever picks this up next: check the proposal cards'
resolution first before touching any of those 5 names.

## spec
Rename player settlement 'Colony' to "Zeddo's Salvage Yard" (owner-ruled,
verbatim) — done. Fall Line Barrens/Scald Spine near-dup renames and the
four Ascendant Helix settlement renames: gated on the owner picking from
the proposal cards (`WORLDMAP_FINAL_REVIEW_1`), not yet actionable.

## verify
`jawa/world_objects_get` on the player settlement reads back "Zeddo's
Salvage Yard" — CONFIRMED. Save re-frozen with the Saves-backup discipline
— CONFIRMED (shared with the sibling items this pass).

## criteria
The player settlement carries its new name in the live world and the
re-saved canonical slot. The remaining 5 renames stay filed as
`needs=decision` until the owner's card picks land.
