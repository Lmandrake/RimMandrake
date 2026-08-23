## spec
The owner wants to be walked through a BUILDING cherrypick, choosing per
building between **three** states, not two:
  1. **active (buildable)** — stays, player can build it
  2. **active (NOT player-buildable)** — the def stays live so it can spawn on
     maps, in ruins and on enemy sites, but leaves the player's build menu
  3. **inactive / disabled** — cut outright
🔑 State 2 is the interesting one and today's data cannot express it:
`deployed/decisions/decisions_buildings.json` is a flat `cut` list of ~40
entries (mech gestators, band nodes, rechargers, boosters, mortars, wall
turrets, warped obelisks, GravForge, the Singularity Reactor). Two-state.
⭐ State 2 is exactly the shape the forbidden-mods audit already uses: VFE
Insectoids 2's enemy siege turrets are KEPT precisely because they carry no
`designationCategory`, so they spawn enemy-side and never reach the build
menu. So the mechanism is "strip designationCategory", not "delete the def",
and that distinction is what the sheet must capture.
⚠️ The VFE-Insectoids 2 strip ruled in `design/Jawa/mods/forbidden_mods.md`
(3 research + 30 buildables + 5 pherocore recipes) has NEVER been applied —
it is the natural first payload for this sheet.
No buildings review sheet exists; nine other registers do
(`design/Jawa/worldbuilding/review/`). the `review-sheets` skill covers building
one, including pre-filling the decisions so the owner only disagrees.

## verify
EMPTY

## criteria
EMPTY

## notes
**Imported from `queue/DECIDE_ARCHIVE.md`. Its `state:` read, verbatim:**

⛔ CLOSED 2026-08-19 — **OWNER: "Freeze buildings cherrypick, that's huge."**
⇒ The buildings pass is NOT v1. It joins the seven un-run categories under the
2026-08-15 freeze and is `[v2]` *if needed at all*. ⛔ Do not build the sheet, do
not fill the EMPTY `verify:`/`criteria:` — they die with the item.
⚠️ **What this does NOT close, because it was never a cherrypick:** the
VFE-Insectoids 2 strip ruled in `design/Jawa/mods/forbidden_mods.md` (3 research
+ 30 buildables + 5 pherocore recipes) has still never been applied. It is a
`designationCategory` strip on defs we KEEP — the "state 2" mechanism — not a
cut list, so the freeze does not reach it. Left where it is, unscheduled, rather
than smuggled back in under this item.
