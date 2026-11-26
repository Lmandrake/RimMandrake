# BOUNDARY: area-sampled squash poses and a kept belly in the flyer cut-out bake, with their checks, Design Version 0.1.0

Code: `src/RimMandrake/Utils/art/flyer_cutout.py` (`area_rows`, `bend`, `source_master`, `pale_body`, `split`, `build`)
and `src/RimMandrake/Utils/art/flyer_eye_checks.py` (`alias`, `ref_bend`, `installed_rows`, `belly`, the SQUASH row).
Items: `RIMMASTER_AUDIT_CUTOUT_EASTS_THIRTEEN_SHARE_SQUASH_NOISE` and
`RIMMASTER_FIX_PORG_WINGS_RIP_BELLY_ACCEPTED_FROM_STILLS`, written 2026-11-26 by work bundle
WB-game-flight-20261126-154837. Tests: `src/RimMandrake/Utils/art/selftest_flyer_cutout_area.py`.

The owner saw "strange static-like noise" on FireHawk's east wing on 2026-11-07
(`skills/rimworld-sprite-facings/references/flyer_truth_set.md`, Bird A). Cause: `bend()` samples each output pixel
once, so a pose squashed under |sy| 0.5 skips source rows. `alias` measured it: FireHawk east 34, and 11 of the 13
other cut-out sets with such poses 9 to 35; frames he called good read under 4.

The owner called the live Porg (Bird G) "terrifying ... some of the white flesh appears to rip away from the body"
(2026-11-07). Cause: its wing polygons hold belly pixels, so a lifted wing carries them; `belly` read 461 and 348 in the
south wings. `keep_pale` keeps body-pale pixels in the plate.

## ACCEPTS (the only inputs this is built for)

- **a-cut-out-config.** A `flyer_cutout_sets/<Set>.json` whose facings carry `master` and `wings` with `poses`
  (`[deg, scale, sy]`) or a `cycle`. A facing may set `"area": true` and a `"source"`
  (`{"path": repo path, "rev": git revision or null, "pad": px, "opaque_from": alpha, optional}`), and
  `"keep_pale": {"min_value": V, "max_sat": S}`.

## DOES NOT SURVIVE (not promised)

- **a-translate-or-layer-bake-facing.** `alias` skips a `translate` facing and a `layer_bake` facing
  (`flier_layer_bake.py` draws those); it says nothing about them.
- **a-source-that-moved.** A `source` with `rev` null reads the working tree: if that static is redrawn, BAKED goes red
  until the set is re-baked. That is the signal, not a defect.
- **squash-in-scale.** Only the vertical squash is area-sampled. A pose that shrinks the wing by `scale` far under 1
  still samples once per pixel. No set does that below 0.6 today.

## PROMISES

- **keep-pale-keeps-the-belly-in-the-plate.** With `keep_pale`, the pale pixels joined to the protected body leave the
  wing layer and stay in the plate; no brown wing pixel moves.
- **a-wing-layer-carrying-belly-is-red.** `belly` reads RED (exit 1) for a wing layer holding over `BELLY_MAX` body-pale
  pixels, GREEN with `keep_pale`, and UNMEASURED (exit 2) with no frames to read.

- **a-facing-without-area-bakes-as-before.** With `area` absent or false, `bend()` takes one sample per pixel, so every
  set that does not opt in bakes byte-identically to the bake before `area` existed.
- **a-squashed-pose-with-area-reads-every-row.** A finely striped wing squashed to |sy| 0.1 reads ALIAS RED when point
  sampled and GREEN with `area`.
- **the-squash-row-honours-area.** `audit --config` reads SQUASH GREEN for a facing with `area` on, and RED with the
  frame and sy named for one without.
- **build-re-bakes-from-the-recorded-source.** `build` on a facing with `source` bakes from that master, and the frames
  equal `compose_facing` of `source_master`; `opaque_from` makes pixels at or over that alpha solid, and no others.
- **the-baked-row-reads-the-shipped-frames.** Frames equal to the area bake of the recorded source read BAKED GREEN;
  one changed pixel reads BAKED RED and names the frame.
- **a-facing-it-cannot-read-is-unmeasured.** A facing whose master frame is not in `--src` reads UNMEASURED and exits 2,
  never GREEN.

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
