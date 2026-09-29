# Contagion redo wave — owner review 2026-09-29

Queued 2026-09-28 from `Transient/contagion_cast_art_review/sheet.decisions.json`
(6 improve, 1 regen — RM_Ikee — 40 keeps untouched) via
`fill_queue.py --input Transient/contagion_cast_art_review/redo_wave_artlist.json`.
**10 job files filed, 0 duplicates refused, 0 row errors.** The artpipe daemon is live
and may claim jobs from `pending/` immediately (expected — a claim is success, not loss).

Every style_notes carries the owner law verbatim: "Your color palette is too uniform per
biome. Needs more variety." — plus each note's own directive verbatim.
No job passes `reference=` (improve = restyle described in text; reference triggers reskin-validate).
Job ids use the established `_v2` redo suffix.

## Status: QUEUED — 6 improve subjects, 10 jobs; Ikee RESTORED, nothing queued

## Ikee — prior art RESTORED, no job queued
Owner note verbatim: "ERROR! We liked the Ikee from before! Keep the little crawling
single eye with tentacles as before. The Jawa consider it cute. This thing is hideous.
Just a single eyeball with just enough flesh and a few small tentacles to pull itself around."

- **The prior liked render survives on disk.** It shipped for the RSW_Ikee port under
  artpipe job id `RSW_Stareling` (registry.jsonl: queued source
  `DESERT_FAMILY_PORT_EXECUTION_1`, generated+validated pass; noted in
  `src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMisc_Races.xml`:
  "DESERT_PORT_PLACEHOLDER_ART_1: landed artpipe render RSW_Stareling_east/_north/_south").
  Shipping copies: `src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/RSW_Stareling/RSW_Stareling_{east,north,south}.png`
  (artpipe copies in `infrastructure/artpipe/_artsrc/RSW_Stareling_*/`). Visually
  verified: a single large eyeball on a small fleshy body with a few tentacle legs —
  exactly the owner's description.
- **Restored as RM_Ikee's shipping art**: copied the three Stareling PNGs to
  `src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Ikee/RM_Ikee_{east,north,south}.png`
  — the exact texPath `Things/Pawn/Animal/RM_Ikee/RM_Ikee` in
  `src/RimMandrake/Stillsand/Defs/ThingDefs_Races/RM_Ikee.xml` (all three lifeStages).
  That folder did not exist before (the def's own header said "art pending"); no XML touched.
- **The hideous 2026-09-28 render** (job ids `RM_Ikee_{east,north,south}`,
  `infrastructure/artpipe/{done,_artsrc}/RM_Ikee_*`) was never wired into any mod —
  it is left in place in artpipe history (generated art is not disposable), just not shipped.
- **Nothing queued for Ikee.**

## Improves (6 subjects, 10 jobs)
| # | Subject | Job id(s) | Owner note (verbatim) |
|---|---------|-----------|-----------------------|
| 1 | RM_BloodyMess | RM_BloodyMess_v2_{south,east,north} | Add more red goopey transparent jelly holding the thing together, less like a bunch of guts. |
| 2 | RM_Fleshsop | RM_Fleshsop_v2_{south,east,north} | The expression should be one of anger. This is a bioweapon. |
| 3 | RM_Eyebark | RM_Eyebark_v2 | Make it hang droopily downward like a willow. |
| 4 | coalescence_stage2 | coalescence_stage2_v2 | keep more of the gelatinous goop with eyes and random limbs, less of the near body-like emergence of coordinated limbs |
| 5 | coalescence_stage3 | coalescence_stage3_v2 | keep more of the gelatinous goop with eyes and random limbs, less of the near body-like emergence of coordinated limbs |
| 6 | RM_CloudRepulsor | RM_CloudRepulsor_v2 | It should not be shown with the beam in the art... that must be added by the game later when it is on |

## Decisions recorded
- **Canvases and facing sets match each subject's original contagion job** (read from
  `infrastructure/artpipe/done/`): 256 with S/E/N facings for BloodyMess and Fleshsop;
  256 single-image for Eyebark and CloudRepulsor; 512 single-image for the two
  coalescence stages (`oversize_reason` recorded, matching the originals). Priority 70,
  channel codex, rimflow_item_id = CONTAGION_BEDAZZLE_SITTING_1 (the originals' item).
- **Prompts are the originals' prompts with the owner's directive worked in**, invariants
  (silhouette family, canvas, facing set, real alpha, single centered subject) pinned in
  style_notes; the coalescence stages keep the stage-1..3 continuity clause.
- **CloudRepulsor**: beam removed from prompt and style entirely — powered-down emitter,
  at most a faint standby shimmer inside the throat; the game draws the beam at runtime.
- **Double-queue check before filing:** done/, pending/, active/ and failed/ hold no
  `_v2` job for any of the six subjects; registry.jsonl has 0 `_v2` mentions for them;
  fill_queue's own id_taken guard reported 0 duplicates.

## Skipped
- All 40 keep rows: untouched (including RM_Skinflap, whose note is an animation wish,
  not an art defect, and RM_Tebbra_b etc.).

## Files
- Input list: `Transient/contagion_cast_art_review/redo_wave_artlist.json`
- Jobs: `infrastructure/artpipe/pending/{RM_BloodyMess_v2_*,RM_Fleshsop_v2_*,RM_Eyebark_v2,coalescence_stage2_v2,coalescence_stage3_v2,RM_CloudRepulsor_v2}.json`
  (10 filed; any file missing from pending/ was claimed by the live daemon into active/)
- Restored textures: `src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Ikee/RM_Ikee_{east,north,south}.png`
