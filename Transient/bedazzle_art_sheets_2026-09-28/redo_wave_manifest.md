# Bedazzle redo wave — owner review 2026-09-29

Queued 2026-09-28 from the four sheet.decisions.json files (blue_desert, cracked_lands, wasteland, cauldron)
via `fill_queue.py --input Transient/bedazzle_art_sheets_2026-09-28/redo_wave_artlist.json`.
**31 job files filed, 0 duplicates refused, 0 row errors.** The artpipe daemon is live and began
claiming jobs from `pending/` immediately (expected — a claim is success, not loss).

Every style_notes carries the owner law verbatim: "Your color palette is too uniform per biome.
Needs more variety." — plus each brief's own intra-biome palette-diversity push.
No job passes `reference=` (improve = restyle described in text; reference triggers reskin-validate).
Job ids use the established `_v2` redo suffix (fill_queue refuses re-use of the done/ ids).

## Status: QUEUED — 13 of 13 subjects, 31 jobs

## Improves (10 subjects, 22 jobs)
| # | Subject | Job id(s) | Notes |
|---|---------|-----------|-------|
| 1 | RM_Vhaulk | RM_Vhaulk_v2_east | east-only repair: frost like N/S, similar legs |
| 2 | RM_Muttavaq | RM_Muttavaq_v2_south | south redone to match N/E identity |
| 3 | RM_FossilSkeleton | RM_FossilSkeleton_v2 | articulated, joined, more alien |
| 4 | RM_Boilhide | RM_Boilhide_v2_{south,east,north} | deadly violet-yellow boils |
| 5 | RM_Grimewing | RM_Grimewing_v2_{south,east,north} | darker, pinker skin, mammal-forward knees |
| 6 | RM_Gristleswarm | RM_Gristleswarm_v2_{south,east,north} | six legs on east + sickly-white flesh all facings |
| 7 | RM_Slagmole | RM_Slagmole_v2_{south,east,north} | less green stone, shovel face, keep claws, rib-back |
| 8 | RM_Sloghog | RM_Sloghog_v2_{south,east,north} | silhouette+palette anchors kept, anatomy pushed alien |
| 9 | RM_Eskith | RM_Eskith_v2_{south,east,north} | five eyes total; side profile shows exactly three |
| 10 | RM_Vexxiss | RM_Vexxiss_v2_{south,east,north} | exterior in the RM_CauldronVent palette (named in notes) |

## Regens (3 subjects, 9 jobs)
| # | Subject | Job id(s) | Notes |
|---|---------|-----------|-------|
| 11 | RM_Seismograph | RM_Seismograph_v2 | "weird, replace" — plain readable instrument, Cauldron kit style |
| 12 | RM_Middenshell | RM_Middenshell_v2_{south,east,north} | full redesign: huge tubeworm, scaled tentacles, accreted shell |
| 13 | RM_Scumslider | RM_Scumslider_{south,east,north} | NEW subject replacing Scumrat's look |

## Decisions recorded
- **Gristleswarm — one full-redo row, not per-facing repairs.** The sickly-white flesh tint
  touches every facing anyway, so a full row (east master, north/south derived via
  ARTPIPE_FACING_COHERENCE_1 §2) is the same 3 jobs but guarantees the six-leg count and
  palette stay coherent across the set. Per-facing repairs would be 3 independent jobs
  with no coherence guarantee.
- **Scumslider collision sweep (2026-09-28): CLEAR.** `git grep -i scumslider` across
  src/ design/ infrastructure/state/ → 1 file, 2 hits, both this ruling's own ledger
  provenance notes (BENCH.jsonl on WASTELAND_BEDAZZLE_SITTING_1 / WASTELAND_RULED_CONTENT_1).
  Sanity probe: `korrum` → 67 files. Queued as plain `RM_Scumslider` (art only — the
  Scumrat→Scumslider def rename is FOUNDRY's ticket, not this wave's).
- **Vexxiss palette pulled from the shipped RM_CauldronVent job** (done/RM_CauldronVent.json):
  bone-white outer mineral rings grading to green-amber inner stain, concentric mineral-ring
  terracing, dark-crust purple-red film sheen, pale glass-crystal accents, condensate beading —
  named explicitly in the v2 style_notes. Hard bans (no eyes, nothing explosive, no glow) kept.
- **Canvases match each subject's original job** (512 for the four colossi Vhaulk/Muttavaq/
  Vexxiss/Middenshell with `oversize_reason` recorded; 256 elsewhere). Priority 70, channel
  codex, rimflow_item_id = each biome's original bedazzle sitting item.
- **Double-queue check before filing:** pending/ and active/ were empty; registry.jsonl has
  no `_v2` entries for any wave subject and no Scumslider; fill_queue's own id_taken guard
  (pending+active+done+failed) reported 0 duplicates.

## Skipped
- **RM_Swale** — regen note stands but placeholder stays; live-reference ticket
  SWALE_CANAL_ART_REFERENCE_1 owns it (owner's own note says placeholder until canal
  screenshots exist). Not queued, per brief.
- **RM_Middenbeetle → Gripper** — rename is FOUNDRY's ticket; owner's note is a rename+name
  ruling, not an art defect. No art queued.
- **RM_Veqma** (cracked_lands improve: taproot visibility) — NOT in this wave's 13-subject
  brief; left for its own routing. Recorded here so it is not lost: owner note verbatim:
  "You should not be able to see the taproot if this is supposed to be the plant in the
  ground. If this is instead the harvested plant it is ok".
- **RM_Tarruq** — keep; note is a sound request, not art.
- All other sheet rows: keep — untouched.

## Files
- Input list: `Transient/bedazzle_art_sheets_2026-09-28/redo_wave_artlist.json`
- Jobs: `infrastructure/artpipe/pending/RM_*_v2*.json` + `RM_Scumslider_*.json`
  (31 filed; any file missing from pending/ was claimed by the live daemon into active/)
