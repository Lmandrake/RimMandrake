# FLIER_AFTERNOON_EXPERIMENT_PROVE_STILL_TORSO

GPT's recommended first experiment (section E of `D:\ClaudeWork\rimmandrake\scratch\gpt_flier\gpt_answer.md`),
distilled in `design/RimMandrake/flier_authoring_architecture_2026-10-21.md`. One creature, one afternoon: prove
that layered authoring (one body plate plus wing surfaces, baked offline) gives a still body AND a flap that reads
on the facing we have not solved, **south**.

**Offline only.** No game, no bridge, no live flight test, no flight screenshots (owner ruling: never live-test
flyers without him present). Do not rebuild or install any HELD flier set. Nothing is installed by this item. The
output is a review artifact for the owner.

## Preconditions

- The Uvak master is our own painted art (open owner question 7 in the design doc). Masters: north 2, east 4,
  south 3 (`src/RimMandrake/Utils/art/flyer_cutout_sets/Uvak.json`). The current installed frames are the
  2026-10-20 cut-out rebuild plus `Uvak_recolour.py` and `Uvak_cleanup.py`.
- Keep the canon recolour (`UVAK_WINGS_RESKIN_TO_CANON`) as a separate, deterministic layer step applied to the
  wing layers. Do not let it obscure the geometry comparison.
- Work under `D:\ClaudeWork\rimmandrake\scratch\flier_afternoon\`. Code changes go to `src/RimMandrake/Utils/art/`.

## Deliverables

1. **Completed body plate** (south): the master minus the wings, with every hole a moving wing exposes painted in
   (shoulders and flank under the wing roots).
2. **Complete wing surfaces**: one image per independently moving wing, including any part the body hid.
3. **Reviewed root/seam annotation**: a stationary root and a pinned attachment seam per wing (a membrane joins
   along the flank, not at a point), landmarks with roles (eyes = head; a torso mark), occlusion order. Show it
   as one enlarged master (protected body cyan, wings in distinct colours, seams yellow, handles and envelope)
   with the two extreme poses beside it.
4. **Eight baked frames** at the shipping canvas (`Uvak_Flying_{1..8}_south.png` in the scratch dir; note that
   the installed set has 4. Changing the frame count is the owner's call, not this item's).
5. **Exported-PNG body equality report**: run
   `flier_body_stabilize.py --set <cfg> --src <scratch> --facing south` (the exported-PNG gate re-reads the
   files) and record IDENTICAL, or CHANGED with the pixels named.
6. **Eye/head and shoulder/root overlays**: `flier_body_stabilize.py --lines <dir>` on the baked frames.
7. **Offline animated preview**: one HTML/canvas page that plays the exact PNGs at the shipping timing
   (`flyingAnimationTicksPerFrame`), with a **fixed centre crosshair** and toggleable reference guides (eye line,
   shoulder line, body outline), native-size playback and enlarged nearest-neighbour inspection. **Never crop or
   recentre frames individually.**
8. **Contact sheet** of masks, seams and extreme poses.

## Sequence (timeboxes, not promises)

| Time | Work |
|---|---|
| 0-15 min | East sanity pass: the existing east cut-out through the same pipeline, to prove the compositor and gates |
| 15-60 min | South: inspect and correct body/wing separation; complete the exposed holes |
| 60-120 min | Pinned seams and a few wing controls; up/down extremes |
| 120-165 min | Facing-specific projection (a south stroke must read as lifting toward/away from the camera, i.e. foreshortening, not sideways paddling) and recovery folding; sample eight phases |
| 165-210 min | Export, run the gates, inspect the loop in the preview |
| rest | One targeted correction, or document the fallback |

## criteria (success; all required)

- The complete protected anatomy is unchanged in the actual exported frames (exported-PNG gate IDENTICAL).
- The required head and torso anchors stay fixed (`--lines` LEVEL; also check horizontal endpoint drift by eye on
  the overlay, since the line gate does not yet measure it).
- Attachment seams stay closed (no see-through gap at any root in any frame).
- No clipping, and no per-frame rescaling or recentring.
- The cycle has meaningfully different wing silhouettes (wing-motion gate FLAPS).
- The wraparound (frame 8 -> 1) has no unexplained pose jump.
- The south motion reads as lifting/foreshortening, not sideways paddling. This is judged by the owner in the
  offline preview.

## Fallback

If one source wing cannot make a convincing south stroke:
1. Keep the body and the annotations.
2. Author ONE additional wing-only extreme (with the underside or fold it needs).
3. Deform between the compatible key poses; bake; rerun the same checks.
4. If it still looks like a rubber sheet, move **only the wings** to a small Blender proxy.

Never answer a missing underside by generating another full creature.

NEXT: confirm the Uvak master is our own art (design doc question 7), then run the east sanity pass and build
the south body plate under `D:\ClaudeWork\rimmandrake\scratch\flier_afternoon\`.
