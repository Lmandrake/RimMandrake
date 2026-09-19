## spec
Standing owner instruction: "there should always be at least one agent
regenerating graphics." Wave 1 (`ART_REGEN_WAVE1_WIRE_IN_1`) just finished 7
creatures. This item queues the next legitimate batch from the same source —
`design/Jawa/worldbuilding/review/round2/decisions_propagated.json`
(828 rows, MEASURED, from the 2026-09-10 fauna/flora sitting under
`ASSIGNMENT_SHEETS_VERDICT_SITTING_1`) — `art: "redo"` rows that are (a)
already decided and (b) need no further design call.

**NOTE on `creature_art_register.decisions.json`**: `CREATURE_ART_REVIEW_SHEET_1`
closed 2026-09-11 stating that file "was never reviewed and must not be
consumed." This item does NOT use it as a decision source (its "replace"/
"redraw" rows for Gorilla/Enhydriodon/GR_Catbear/BMT_SandPillar/etc. are
stale prefill, superseded).

Of the 34 `redo` rows in `decisions_propagated.json`, minus the 7 already
done (Kreetle, Horax, AA_ShadowCharger, AA_Thunderox, Fambaa, Dragonsnake,
Zakkeg):

- **Excluded by the standing carve-out** (biome reassignment / rename /
  open design call, route to BENCH/owner instead):
  `AA_ShockGoat` (open biome choice + rename), `Gundark`, `Aiwha`,
  `GR_Chickenhorse`/`GR_Chickenlizard`/`GR_Chickenspider`/`GR_Needlechicken`/
  `GR_Rabbitchicken` (Helix-faction placement, unresolved), `JRWBeelzebufo`
  (rename+redefine).
- **Excluded — `decision: "out"` (cut from the game for real per the
  2026-09-10 homeless-disposition sitting)**: `BMT_BiliousVarog`,
  `BMT_ShatterjawBeetle`, `GR_FleshFlies`, `GR_Mechachicken`, `GR_Squirralope`.
  Generating art for a creature ruled OUT is wasted work.
- **Excluded — conservatively, `decision: "move"` (a biome reassignment,
  even though the target biome is already named in the note)**: `AA_Radyak`
  ("Poison Forest"), `BMT_CrystalCrab` ("crystal caverns"), `BMT_SandPillar`
  ("cracked land"), `DA_BeardedTroll` (Wildsteam territory). Left for
  BENCH/owner per the letter of the carve-out rather than assumed safe.
- **Queued this wave — `decision: "in"`, no biome move, no rename, a plain
  art brief**:
  - `AA_Frostmite` (Alpha Animals) — propane-lakes note: "the propane lake
    life should be utterly strange."
  - `GR_Spidercat` (Vanilla Genetics Expanded) — wasteland note: "Spindley
    alien-like spidercat thing."
  - `VAEWaste_Megatardi` (Vanilla Animals Expanded — Waste Animals) —
    wasteland note: "Canyon Crawler scrapes along eating everything."
  - `Insectomorph` (Star Wars Animal Collection, canon SW creature — no
    rename per the redo-semantics doctrine, gather reference online) —
    note: "ridable mount associated with the Drug, found near Hutt
    settlements | NINTH-ROSTER: faction fauna" (disposition already
    settled at the homeless-disposition sitting, frozen 2026-09-10).

12 jobs filed (4 creatures x 3 facings south/east/north, 512x512 transparent,
codex channel) via `fill_queue.py`, matching wave 1's job shape.

## verify
Each creature's 3 facings land in `infrastructure/artpipe/done/` with
`worker_status: ok`. Wiring into Textures/ is a separate step (see
`ART_REGEN_WAVE1_WIRE_IN_1`'s pattern) — not this item's job.

## criteria
12/12 jobs complete (done or a clean, explained failed), daemon left running
so it keeps draining the queue unattended.
