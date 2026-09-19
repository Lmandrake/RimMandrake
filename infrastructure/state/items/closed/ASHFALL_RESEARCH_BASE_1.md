## spec

Discovered mid-pass while continuing `ANCIENT_WAR_LAB_1` (2026-09-18): the
propane lake's own doc carries a 2026-09-12 plot-sitting amendment
(`design/Jawa/worldbuilding/biomes/the_propane_lakes.md` §8, "AMENDMENT
2026-09-12 (plot sitting, owner verbatim)") that is **not reflected anywhere
in `ANCIENT_WAR_LAB_1`'s own build spec or history**, and the dungeon that
amendment names — the Ashfall Research Base, "the Spire" — has **no queue
item at all** despite having its own full design doc,
`design/Jawa/worldbuilding/ashfall_research_base.md`.

The ruling, owner verbatim (propane_lakes.md §8): after the war lab's crater
event, the lab's intact shielding stays **LOCKED**. The only way in is the
**Rakatan command codes**, held on an isolated system inside **the Spire**
(the Ashfall Research Base's landmark name — "a mysterious [structure in the]
mountains... That's the local name for it"). The codes "CANNOT be granted by
the cathedral... were never ceeded to the cathedral"
(`ashfall_research_base.md` §6) — they are seized at the Spire or not at all.

⇒ **The war lab is a two-key dungeon**: the crater event (`WAR_LAB_CRATER_HOOK_1`)
opens the ground; the Spire's codes open the door. Neither
`ANCIENT_WAR_LAB_1` nor `WAR_LAB_CRATER_HOOK_1` currently build or even
mention this lock — both currently treat "reachable only via the submerged
route" as the sole access gate, with no representation of a post-crater
locked door requiring an item/quest-flag from a second, unbuilt dungeon.

`ashfall_research_base.md` also establishes: it is NOT the war lab (explicit,
§2 — "Not a lab improvised in a panic like the war lab, else say the Ashfall
Research Base"); it was the Rakatan surface-level command center; the dungeon
shell, the landmark, and "the codes-as-prize build" were all ruled clear to
proceed (§6, lines 166-170) — nothing in that doc blocks starting this.

## Owed

- Read `design/Jawa/worldbuilding/ashfall_research_base.md` in full (not just
  §6) before building anything — this item has not done that pass yet.
- Author the Spire as its own KCSG dungeon, same precedent as
  `VAULT_DUNGEON_BUILD_1`/`SCALD_DARK_TOWER_1`/`ANCIENT_WAR_LAB_1` (a
  `gen_*_layout.py` generator, not hand-authored XML — see
  `src/RimUtinni/StructureInjectionsRUT/Source/WarLab/gen_war_lab_layout.py`
  for the pattern this project now expects).
- Author the "Rakatan command codes" as a quest-item/quest-flag the war lab's
  locked shielding checks for — this is the missing mechanism connecting the
  two dungeons; neither `ANCIENT_WAR_LAB_1` nor `WAR_LAB_CRATER_HOOK_1` build
  it today.
- Reconcile: does the war lab's shielding lock apply only AFTER the crater
  event (as the amendment states), or does it also explain the pre-crater
  "submerged route only" access `ANCIENT_WAR_LAB_1`'s own criteria already
  demand? Not yet answered by either item.

## Watch out

- Do not duplicate `ANCIENT_WAR_LAB_1`'s own dungeon — the Spire is a
  separate site (surface-level command center, not underwater).
- `WAR_LAB_CRATER_HOOK_1` owns the crater/ignition mutation; this item owns
  the Spire dungeon and the codes-as-key mechanism only. The actual "locked
  door" check inside the war lab belongs to whichever item finishes the war
  lab's own gate — likely a small addition to `ANCIENT_WAR_LAB_1` or
  `WAR_LAB_CRATER_HOOK_1` once the codes item exists, not duplicated here.
- Filed `needs=offline` — the dungeon shell, landmark, and codes-item
  authoring are all offline file work, same as the war lab's own first pass.
