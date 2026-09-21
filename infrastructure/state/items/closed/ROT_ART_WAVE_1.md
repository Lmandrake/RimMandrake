# ROT_ART_WAVE_1 — land the 22 rot artpipe jobs

Full job inventory and rationale: `Transient/rot_art_jobs_20260918.md`. Blocked
since 2026-09-19 on the codex weekly meter (97% used, `WEEKLY_STOP`); owner reset
the quota 2026-09-19 ~20:20Z and the daemon is actively working through the
combined backlog (100+ jobs from several items sharing the queue), so this lands
incrementally as jobs complete rather than in one pass.

## landed (1 of 22)
- **RUT_EuphoricCrown** — `rut_euphoriccrown_v1` (rich amber/gold painterly
  render, matches the established style). Given its own texPath
  `RotSporeKit/Things/Plant/EuphoricCrown` (folder-per-plant, matching the
  RustPuff/Seadew convention already used elsewhere in this mod — texPath is
  the FOLDER, `Graphic_Random` loads every file inside it), file placed at
  `Textures/.../EuphoricCrown/EuphoricCrown_A.png`. Previously shared the
  `VioletWimple` placeholder with an unrelated plant (`RUT_RotSporeKit_Flora.xml`'s
  actual VioletWimple species) — that plant's own texPath is untouched, only
  `RUT_EuphoricCrown`'s pointer moved. `validate_patch.py --live`: 0 errors.
  `deploy_custom_mods.py --apply`: 2 files, VERIFIED in sync.

## rejected on quality, regen filed (1 of 22)
- **RUT_AgelessCap** — `rut_agelesscap_v1` landed but the render is a flat
  gray/white line-sketch with no color fill or shading, compared directly
  against `rut_euphoriccrown_v1` from the same batch (a real, richly-colored
  painterly render) — a bad generation, not a style choice; `validator` and
  `legibility` were both `skipped` in its manifest (no automated QA ran on it,
  since new-art jobs have no reference to check against — this was a human-eye
  catch). **Not deployed.** Filed `rut_agelesscap_v2` (pending), same prompt
  with color/shading explicitly demanded, `style_notes` documenting why v1 was
  rejected. Land it the same way once it completes: folder
  `RotSporeKit/Things/Plant/AgelessCap`, texPath update on `RUT_AgelessCap`
  (currently on the shared `CrimsonCap` placeholder, also shared with
  `RUT_FurnaceCap` and an unrelated Flora species — same folder-per-plant
  pattern as EuphoricCrown above).

## landed 2026-09-20 (remaining 15 of 22 non-colliding + collision resolution)
All 22 jobs are now in `infrastructure/artpipe/done/` (queue fully drained).
This item's own 22 collided on 7 defs with `ROT_FLORA_FAUNA_VERDICTS_1` STEP
5's separate 58-job `rot_*_v2` regen wave (same def, art generated twice by
two different items) — landed together in one pass, full detail in
`ROT_FLORA_FAUNA_VERDICTS_1.md`'s STEP 5 log:

- **15 of 22 landed as this item's own art** (no wave-2 collision):
  `RUT_LiveIngredient_{AgelessCap,RegenerantVeil,EuphoricCrown}`,
  `RUT_BrewingVessel` (south only — east/north still owed), `RUT_Tea_{AgeReversal,
  Bioregeneration,Pleasure}`, `RUT_Symbiont_{Quickflesh,Nightwake,Sheenblood,
  Mycoid}`, `RUT_LivePrep_ToxicInjection`, `RUT_LivingFurnaceCap` (moved off the
  shared `RUT_MortalMorelPlant` item texPath onto its own
  `RotSporeKit/Things/Item/Crops/LivingFurnaceCap` folder), `RUT_GrownFurnace`,
  `RUT_Gene_Furnaceblood` icon (flat UI-icon style, not painterly — landed as
  filed, still an open question whether this belongs in artpipe at all).
- **6 of 22 lost the collision** (`RUT_AgelessCap`, `RUT_RegenerantVeil`,
  `RUT_EuphoricCrown`, `RUT_FalseFruit`, `RUT_FurnaceCap` plant, `RUT_PaleMoss`)
  — the wave-2 `rot_*_v2` re-ruled regen deployed instead; this item's own
  `rut_*_v1` renders for these 6 (plus `rut_agelesscap_v2`, this item's own
  quality-regen of AgelessCap) are superseded, not deployed.
- **1 of 22 won on quality, then lost to a clean regen** (`RUT_PaleTree`): the
  wave-2 collision winner `rot_paletree_v2` was rejected (flat achromatic
  render, no color fill — same defect class as `rut_agelesscap_v1` below).
  `rut_paletree_v1`'s real painterly art was deployed as the interim; the
  daemon cleared `rot_paletree_v3` the same session and it replaced the
  interim with the final re-ruled art.

`validate_patch.py` (full-list ModsConfig snapshot): 0 errors. Deployed and
verified in sync (RotSporeKit, UtinniPatches, SWBestiary). Contact sheet for
owner review: `Transient/rot_art_landed_20260920/index.html`
(`D:\Luke\dev\Rimworld\Transient\rot_art_landed_20260920\index.html`).

Still owed (unchanged from the original filing note): brewing-vessel east+north
views once a matched reference set is wanted; whether `RUT_Gene_Furnaceblood`
belongs in this pipeline at all.

## closed
22 of 22 landed or deliberately superseded by a re-ruled regen. See
`ROT_FLORA_FAUNA_VERDICTS_1.md` for the collision-resolution detail.

The 4 rejected/failed wave-2 renders are NOT owed — all four `_v3` regens
(`rot_paletree_v3`, `rot_greylady_v3`, `rot_agariluxprime_v3`,
`rot_recurvedstropharia_v3`) cleared the daemon the same session and their
textures are on disk, VERIFIED 2026-09-20: `infrastructure/artpipe/pending/`
and `failed/` hold no `rot_*_v3` job, and each one's PNG is present
(`.../RotSporeKit/Things/Plant/PaleTree/PaleTree_A.png`,
`.../Plant/GreyLady/GreyLadyGrown/GreyLadyGrown_A.png`,
`.../UtinniPatches/Textures/RotSpecies/AgariluxPrime.png`,
`.../RotSpecies/RecurvedStropharia.png`).
