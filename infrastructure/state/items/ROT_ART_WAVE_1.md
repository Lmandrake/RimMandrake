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

## still pending (19 of 22 + follow-ups)
Every other job in `Transient/rot_art_jobs_20260918.md`'s list of 22 is still
in `infrastructure/artpipe/pending/` behind the rest of the shared queue
(~100 jobs from other items were requeued at the same quota reset). Land each
the same way as it completes: check the manifest/PNG by eye against the
sibling that already landed well (don't assume clean == good — see
AgelessCap above), give it its own folder+texPath if it's currently on a
shared placeholder, `validate_patch.py --live`, deploy, note here.

Also still owed per the filing note (not artpipe jobs, separate follow-up
work): brewing-vessel east+north views once south lands; the
`RUT_LivingFurnaceCap`/`MortalMorel`-vs-`HealingMorel` file-naming mismatch;
whether the `RUT_Gene_Furnaceblood` icon even belongs in artpipe at all
(flagged, not resolved, in the original filing note).

## not closed
1 of 22 landed clean, 1 rejected+requeued, 19 still generating. Revisit as the
daemon's queue advances rather than polling continuously.
