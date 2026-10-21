# Flier authoring architecture (2026-10-21)

Source: an outside review by GPT of the whole flier problem: brief, `flier_body_stabilize.py`, the audit and the
engine facts. Full answer (45 KB): `D:\ClaudeWork\rimmandrake\scratch\gpt_flier\gpt_answer.md`, with the brief
beside it (`brief.md`). This doc keeps what we act on. GPT's claims about OUR code came from reading, not running,
so each was checked against the code before being repeated here (see "Claims checked").

Related: `design/RimMandrake/flier_frame_registration_audit_2026-10-20.md` (the audit and the six rebuilds),
`skills/rimworld-modding/references/flight.md` (engine mechanics). Owner rulings that bind all of this: flight
art is a whole-body flip-book, never a Spastic render tree. **Never live-test a flyer's flight without the
owner present, and never try to capture images of flight** (CLAUDE.md).

## Decisions taken

1. **Keep the whole-body flip-book as the shipping format, and author it from layers.** Each facing has ONE
   body plate, plus the wing surfaces extracted from it, composited procedurally and baked offline into the
   numbered frames. Our `flyer_cutout.py` rebuild already does this; we extend it rather than replace it. Layered
   *authoring* does not conflict with the "not a wing layer" ruling, which is about *runtime delivery*.
2. **Body stability is a construction invariant, verified on the exported PNGs.** It is not something the
   stabilizer achieves. A new bake must show the protected body byte-identical in the files the game loads, after
   every post-build step (e.g. `Uvak_cleanup.py`). Built 2026-10-21 as the exported-PNG gate in
   `src/RimMandrake/Utils/art/flier_body_stabilize.py`.
3. **Registration and stabilization are salvage and audit tools.** Use them on legacy or independently
   generated frames. They are never the mechanism that makes a new set consistent. A rigid transform cannot repair
   a different drawing.
4. **Arbitrary anatomy gets a small reviewed annotation per facing, not a universal detector.** The annotation
   says what is rigid, which surfaces move, where they attach, and what covers what (data model below). 18
   three-facing sets come to about 54 reviewed annotations, which is tractable. A universal detector is a
   research project.
5. **Two independent gates per facing: a still body AND a real flap.** A body-only gate passes a set of
   identical copies (the Beldon lesson). Built 2026-10-21 as the wing-motion gate.
6. **Estimator failure is uncertainty, not a finding.** If ECC fails or too few features match, the result is
   UNMEASURED. APPEARANCE CHANGED is reserved for residual evidence (built 2026-10-21).
7. **Difficult facings may use two or three approved wing-only drawings** (for example a folded or underside
   pose), with the body reused throughout. A missing underside is never fixed by generating another whole
   creature.
8. **Uvak recolouring works on the wing LAYERS, then re-bakes.** It does not detect "red wing pixels" in each
   final frame.

## Rejected

| Option | Why rejected |
|---|---|
| Independent full-body generation of each frame, then registration | Every frame is a new drawing. Registration cannot restore exact eyes, shoulders or shading. Legacy salvage only. |
| A universal anatomy / eye / wing-root detector | Cannot see hidden roots and cannot label an unfamiliar part. The dark-spot eye detector already picked horns and crests on our painted heads. |
| A runtime shader flap (vertex displacement or inverse-warp fragment shader) as the next step | It only moves where the computation runs; the authoring problem (missing undersides, seams, occlusion) stays. Revisit only after the same deformation works as an offline bake. |
| A full rigged 3D creature per species | High cost per creature and it loses the approved painted look. If a membrane will not read, the fallback is a 3D proxy for the **wings only**. |
| Video or diffusion generation as the production path | Useful for exploring poses only: anatomy drift, bad loops, alpha and flicker. |

## Open questions for the owner (plain language)

1. **How big does a flier look on your screen at your usual zoom?** A one-pixel wobble matters a lot on a tiny
   sprite and not at all on a big one, so our "still enough" limits should be set at that size.
2. **May a wing pass in front of the body for a frame,** as long as the body underneath never moves? If yes, a
   near wing covering the chest on the downstroke is fine. If no, wings must be kept clear of the body, which
   limits the flap.
3. **How much hand-marking per facing are you OK with?** Roughly a few minutes per facing to mark the rigid body,
   the wing joins and the eyes, checked on one enlarged picture with the two extreme wing poses beside it.
4. **May we draw two or three extra wing-only pictures for hard views** (wings folded, or seen from underneath)?
   The body would stay the same picture.
5. **What exactly fell short in the six rebuilt sets?** The body moving, the wings looking stiff, the joins
   tearing, or the wrong wing shape? Each needs a different fix.
6. **"Inside the original footprint": does that mean the fixed canvas, or the creature's original outline?** A
   tucked-wing master may leave no room for a full flap inside its outline.
7. **Is the Uvak master our own painted art?** The experiment below assumes it is (no donor art may ship).

## Annotation data model (GPT section D)

The general idea is **rigid regions, moving surfaces, attachment constraints, and visibility**. "Two eyes and two
shoulders" is one instance of it, not the schema. Required per facing:

| Field | Purpose |
|---|---|
| Master image and hash | identity and provenance |
| Fixed canvas, scale and anchor | stable delivery geometry |
| Completed body plate | the immutable rigid artwork, with holes the wings expose painted in |
| Protected visible-body mask | pixels that must never change |
| Allowed output envelope | stops clipping and footprint violations |
| Landmarks with role and visibility | review and independent measurement; a north-facing head line is called a head line, not an eye line |
| Moving-surface array | any number of wings or fins |
| Attachment per surface | a pivot, an axis, or a pinned seam (a bat membrane along a flank needs a seam, not a point) |
| Motion preset or key poses | defines the flap |
| Occlusion rules | front/back per surface per facing |
| West policy | explicit: mirror east, or authored west |

Illustrative shape (not yet a spec; our `flyer_cutout_sets/<Set>.json` holds `protect`, `wings[].poly`,
`wings[].hinge`, `poses` and `eyes` today, so it would grow into this):

```json
{"version": 1, "canvas": [256, 256], "coordinates": "normalized_top_left", "master_sha256": "...",
 "body": {"plate": "south_body.png", "protected_mask": "south_core.png"},
 "allowed_envelope": "south_envelope.png",
 "landmarks": [{"id": "eye_left", "role": "head", "xy": [0.46, 0.31], "visible": true},
               {"id": "thorax_mark", "role": "torso", "xy": [0.50, 0.49], "visible": true}],
 "surfaces": [{"id": "wing_left", "image": "south_wing_left.png", "root": [0.42, 0.43], "tip": [0.12, 0.36],
               "attachment_seam": [[0.42, 0.43], [0.43, 0.58]], "motion": "membrane_flap",
               "phase_offset": 0.0, "occlusion": "south_left_wing"}],
 "west_policy": "mirror_east"}
```

Presets give defaults (rigid insect wing, feathered wing, finger-supported membrane, manta-like fin, multi-wing
array). They never fix the wing count, eye count or body orientation. Distinguish the stationary anatomical
**root**, which may be hidden and then serves as a rig constraint, from a nearby visible body feature used for
measurement. Review: segmentation proposals, then one enlarged master showing the protected body in cyan, the
surfaces in distinct colours, the seams in yellow, the handles and the envelope, **with the two extreme poses
beside it**. A glance at the bare master cannot verify the flap. Labelme (polygons, lines, points) is a
reasonable editor to start from.

## The afternoon experiment (GPT section E), ready to run

Filed as `FLIER_AFTERNOON_EXPERIMENT_PROVE_STILL_TORSO`
(`infrastructure/state/items/FLIER_AFTERNOON_EXPERIMENT_PROVE_STILL_TORSO.md` holds the run sheet). In short:
Uvak **south**, after a short east sanity pass. Build a completed body plate, complete wing surfaces, a reviewed
root/seam annotation, eight baked frames, an exported-PNG body equality report, eye/head and shoulder/root
overlays, an HTML/canvas offline preview with a fixed centre crosshair, and a contact sheet of masks, seams and
extremes. Keep the canon recolour as a separate layer step. Success criteria and the fallback are in the item.
Offline only: no game, no bridge, no live flight.

## Claims checked (GPT read our code; we checked each by reading it, 2026-10-21)

| GPT claim | Verdict | Where |
|---|---|---|
| Failed ECC or too few inliers set `reposed = True` | TRUE, fixed (now UNMEASURED unless residual evidence) | `measure_facing` |
| The reference body mask is passed as `findTransformECC`'s `inputMask`, which is an input-image validity mask | TRUE, fixed. The cvenv OpenCV is 5.0.0 and has `findTransformECCWithMask`; the region now goes in as `templateMask` (also in `_ecc_refine`). MEASURED effect: small, as GPT predicted. At a 20 px body shift the old call was 0.23 px off at rho 0.918, the new one 0.05 px at 0.982. | `est_ecc`, `_ecc_refine` |
| `find_part` has no positive score floor; a missing part leaves the worst part shift at 0; feature scale is never in the verdict | TRUE, fixed: score floor 0.8, a part not found makes the frame low-confidence, scale gated at 1 px of body rim | `find_part`, `est_parts`, `measure_facing` |
| Feature coverage across the rigid anatomy is not checked | TRUE, **partly** fixed: the MASK must now cover every wing root and the torso past them; inlier spread across the body is still not checked | `coverage` |
| Several east annotations cover only head and neck | TRUE (audit; e.g. Uvak east `protect` is one box at x >= 175). The localizer now uses the whole plate region (protect + outside the wing polygons). | `body_mask_from` |
| `plate_identical = 1.0` is measured inside the chosen plate, on in-memory frames | TRUE (`flyer_cutout.cmd_build` computes it before/without re-reading the PNGs); the exported-PNG gate now covers it | `flyer_cutout.py` |
| `line_check` gates only the vertical midpoint and the angle (not horizontal drift, endpoint distance or line length) | TRUE, **not changed in this pass** (owed: 2D endpoint gate + length/head-to-root distances) | `line_check` |
| Points are constructed proxies (east snout on the eye's row, north head edges, east shoulder from hinge + chest, the first two hinges only) | TRUE; the labels already say so on the sheet, and the multi-wing case (Sketto, four wings) uses the first two hinges | `eye_points`, `shoulder_points` |
| `_body_match_mask` excludes reference wing polygons, not the moving-wing envelope; SIFT target candidates span the whole opaque creature; PCA halves are geometric, not semantic | TRUE, not changed | `_body_match_mask`, `est_features`, `split_parts` |
| The sprite-facing skill still tells agents to watch flight live, unattended | TRUE (`skills/rimworld-sprite-facings/SKILL.md`, the "Validation plan for a flier" paragraph). Filed as a lesson + rimflow note for the next curation pass; skills are not edited outside curation. | |

## Re-measurement of the six rebuilt sets after the fixes (2026-10-21)

Sets: Sketto, PekoPeko female, FireHawk, Uvak, Hawkbat, Hawkbat juvenile (18 facings). Output:
`D:\ClaudeWork\rimmandrake\scratch\flier_stab_2026-10-21\` (`before\`, `after\`).

- Owner's line test (`--lines`): 18/18 LEVEL before and after (unchanged).
- Wing motion: 18/18 FLAPS (largest pairwise silhouette change 0.71 to 0.99; smallest step 0.30).
- Exported-PNG body: 17/18 IDENTICAL; **Sketto east CHANGED 1 px**. The pixel (150, 109) sits at the hinge,
  inside protect, and has alpha 251 in the original master (its neighbours 250 to 252). A wing behind it shifts
  the blend by one level in frame 3. That is compositing through a not-quite-opaque painted pixel, not a redraw.
  The gate reports it because the rule is exact equality. A first pass also flagged 277 soft-rim pixels opaque
  only where a wing sat behind them; the gate now protects only pixels opaque in every frame, plus interior holes.
  Gap: master pixels painted at alpha < 255 are only checked where they read opaque in every frame.
- Body localizer: LOCKED 18/18 before, **17/18 after: Hawkbat east LOCKED -> DRIFT**. The localizer now includes
  the torso, and in frame 3 the near wing (order "over") covers it on the downstroke. One part template slides
  2.29 px under the wing, while features read 0.0 px on 124 inliers, ECC 0.07 px, and the exported PNG body is
  identical apart from 100 px under the near wing. This is occlusion fooling the PARTS estimator, not body motion.
  It is left as reported. The fix is occlusion-aware part masks (GPT section A3, P1).
