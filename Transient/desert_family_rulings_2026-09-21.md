# Desert family port — owner rulings 2026-09-21 — progress

Item: `infrastructure/state/items/DESERT_FAMILY_PORT_EXECUTION_1.md`

## Status: DONE

## Re-measured counts (mine, not the item's)
- Droid entries live in any desert biome `wildAnimals` today: **0** (checked
  `RUT_Desert.xml`, `RUT_BlueDesert.xml`, `RUT_ExtremeDesert.xml`, `RUT_AridShrubland.xml`
  for both donor and `RSW_DW_OuterRim_*` names).
- Vanilla/Biotech plant rows still live in any desert biome `wildPlants` before this pass:
  **3** (`Plant_Bush`, `Plant_HealrootWild`, `Plant_Ripthorn`, all only in
  `RUT_AridShrubland.xml`) — not 5; `Plant_ShrubLow` was already replaced and `Rat` was
  already removed from ambient tables by an earlier, same-day ruling.
- `RSW_MossBeetle` art jobs pre-existing: **3 of 3 facings PASS**, but for
  `RSW_MossBeetleLarvae` only (a different life stage than the adult). 0 existed for the
  adult (`RSW_MossBeetle`) or `RSW_MossBeetlePupa`.

## A. MossBeetle comes back — DONE
- [x] Def already ported/live: `RSW_MossBeetle` (adult), `RSW_MossBeetleLarvae`, `RSW_MossBeetlePupa`
  all exist in `src/RimStarWars/SWBestiary/Defs/BiomesTeamPort/ThingDefs_Races/RSW_BiomesTeamPort_Races.xml`.
  No def authoring needed.
- [x] Searched existing art:
  - `RSW_MossBeetleLarvae` ALREADY HAS approved art: `deeps_mossbeetlelarvae_v2_{east,north,south}`
    in `infrastructure/artpipe/done/`, all validated PASS, registered under source
    `DEEPS_FAUNA_VERDICTS_1`. Owner regen note (2026-09-19, deeps sheet): "Slender,
    maggot-like bodyplan, pale yellow liquids and pale blue exterior, oozing and curling
    along the tunnels." Approved again 2026-09-20 in `Transient/lantern_deeps_strange_life_2026-09-20.decisions.json`
    (`fauna_mossbeetlelarvae`: approve). Since the def is shared across biomes, this art
    stands — NOT requeued.
  - `RSW_MossBeetle` (adult) and `RSW_MossBeetlePupa`: NO existing job anywhere
    (registry.jsonl, done/, _artsrc/, pending/, failed/) — confirmed by grep, only
    Larvae jobs exist. These were never queued (the item's art census explicitly
    excluded MossBeetle from the "safe to queue" list pending this ruling).
- [x] Filed 6 new jobs via `fill_queue.py` (source `DESERT_FAMILY_PORT_EXECUTION_1`),
  south/east/north for both: `desertportb_mossbeetle_*`, `desertportb_mossbeetlepupa_*`
  — now sitting in `infrastructure/artpipe/pending/` for the daemon.

## B. 7 Droid Depot droids leave this item — ALREADY DONE, no new item filed
- [x] Checked all 3 desert biome XML files (RUT_ExtremeDesert/RUT_Desert/RUT_AridShrubland)
  for the 7 droid defNames (both donor names and the absorbed `RSW_DW_OuterRim_*` names) —
  ZERO matches. `git log -S` traced this: `EXTREME_DESERT_UNRULED_VERMIN_1` (2026-09-20,
  same day, ~6h after the blanket "replace all" ruling) already pulled all 7 droids + `Rat`
  out of ambient `wildAnimals` on an owner ruling that they are Fall-Line arrivals, not
  ambient fauna.
- [x] Found the item that already owns their disposition: `FALL_LINE_ARRIVAL_MECHANISM_1`
  (filed to BENCH same day, still open, unclaimed) — it already lists the exact 7 droids
  by name, already says "not build this by re-adding rows to any wildAnimals table", and
  already quotes the owner's ruling. Filing a second item would fork the same disposition.
- [x] Added the owner's fresh 2026-09-21 verbatim quote ("They get injected by the wreckage
  thing. Not the random spawn of the biome.") to `FALL_LINE_ARRIVAL_MECHANISM_1.md` as
  reinforcement, cross-referenced from `DESERT_FAMILY_PORT_EXECUTION_1.md`.

## C. 5 vanilla/Biotech rows replaced by our own defs — DONE for 3, already-done for 1, CONFLICT flagged for 1
- [x] Re-measured against live biome XML (not the frozen decisions sheet):
  - `Plant_ShrubLow` — already replaced by `RUT_Fuzz` (earlier work). No action.
  - `Rat` — not wired ambient anywhere (see B, Fall-Line ruling). Re-adding it as ambient
    would contradict that same-day ruling. **Flagged as a conflict, not resolved** — noted
    in both items, left for the owner/FALL_LINE_ARRIVAL_MECHANISM_1.
  - `Plant_Bush`, `Plant_HealrootWild`, `Plant_Ripthorn` — genuinely still live, only in
    `RUT_AridShrubland.xml`.
- [x] Authored `RUT_Grellbush`, `RUT_WildHealroot`, `RUT_Grellspine` in
  `src/RimUtinni/AshkarrFlora/Defs/ThingDefs_Plants/RUT_AridShrublandVanillaReplacements.xml`
  — stats/plant mechanics pulled from the live def dump (measure sql), desert temperature
  tolerances re-authored directly (the existing patch is keyed to donor defNames).
- [x] Rewired `RUT_AridShrubland.xml`'s `wildPlants` to the 3 new defNames, same commonalities.
- [x] `RUT_WildHealroot` keeps label "wild healroot" — `PlantNames_Ashkarr.xml` (owner,
  2026-09-05) already ruled that word is not an Earth-name violation; this pass only moves
  def ownership off vanilla.
- [x] Filed art jobs `rut_grellbush`, `rut_wildhealroot`, `rut_grellspine` (none existed).
- [x] `validate_patch.py` run on both files: biome file OK 0 errors; new plant defs file
  FAILS only on missing texPath (expected/pending-art, same state `RUT_Fuzz.xml` is in
  today for the same reason).

## Re-measured counts
(TBD)

## Commit
de67541e0, pushed to main.
