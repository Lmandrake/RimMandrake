# Flier flip-book registration audit - 2026-10-20

Item: `FLIER_FRAMES_AUDIT_BODY_NOT_WING_EXTREMES`. Owner 2026-10-20: *"Their bodies should be kept static while the wings flap. So looking for extreme of the graphic image is not useful and couples wing motion to body motion incorrectly."*
Offline, read-only. Instrument: `src/RimMandrake/Utils/art/flier_frame_registration.py` (selftest `selftest_flier_frame_registration.py`). Raw numbers: `D:\ClaudeWork\rimmandrake\scratch\flierframes\audit.json` / `audit.txt`; contact strips (red cross = rigid-body centroid, blue = alpha-bbox centre, green lines = frame 1's body centroid) in `D:\ClaudeWork\rimmandrake\scratch\flierframes\strips\`.

## Result

(Counts below are as first measured; the four donor sets were installed later the same day and now appear in the table as OFFENDER rows, so the table lists 22 offenders, not 18.) 37 (def, prefix) flip-book sets reference `flyingAnimationFramePathPrefix` in `src/` (male and female prefixes counted separately, shared art counted per def). 22 have 2+ frames on disk; **18 are OFFENDERS** (body moves >= 2 px AND >= 2% of body size between frames in at least one facing). Worst: RSW_Sketto south (103.8 px, 1.7x its body size - frame 3 is a different pose), RSW_PekoPeko female east (132.5 px), RM_FireHawk north (84 px). Five defs declared 4-8 frames but shipped none in `src/` (RM_Kirruk uses vanilla Chicken frames; Brezak, Drexl, Thranta, Tibidee got donor frames 2026-10-20, section at the end); 10 sets are single-frame (no animation, nothing to jitter).

**The dominant cause is not sub-pixel registration: the generated frames are separate repaints, so the body itself is redrawn (position, pose, even facing of the head) in different frames.** Seen directly in the strips: Uvak south frame 3 is a different drawing from frames 1/2/4; Sketto south frame 3 is a foreshortened re-pose; FireHawk north head/torso sit at different heights every frame; Urusai and PekoPeko likewise. Re-registering by translation fixes only the translation share; a re-posed body needs the `flyer_lock` plate recipe (below).

## Method and trust

- **Body per frame:** alpha > 127, morphological opening (square, side ~ 2*10% of sqrt(area)+1, halved until something survives) so thin wings/tails drop, then the components >= 25% of the largest (a head+thorax+abdomen body opens into several blobs; keeping only the largest flipped between frames - measured, fixed).
- **Primary drift (`body drift px`):** translation that maximises the overlap of each frame's opened body with frame 1's, span = max pairwise shift (worst facing). `open-centroid` (centroid of the same mask) and the colour-match registration (`flyer_lock.align`-style, reported in `audit.json` as `colour_px`/`colour_share`; untrustworthy when the share is low because repainted frames share no pixel colours) are cross-checks. `alpha-bbox px` is the WRONG metric, shown only to quantify what a bbox-registering tool sees.
- **Sanity probe (selftest):** synthetic rigid body + flapping thin wing: body drift 0.00 px while the alpha-bbox centre drifts 15.5 px; same set with the body shifted 3 px in one frame: 3.00 px, verdict OFFENDER. The instrument can fail and can pass.
- **Caveats:** there is NO positive control in shipped art: the one set meant to be body-locked (Sketto) was never installed locked (`flyer_lock.py check --facing east`: locked_share 0.0004 < floor 0.45). Where wings are broad (north/south views) the opened mask can include wing bases, so absolute px are approximate; the three methods disagree by tens of px on the worst sets, but all agree they are far above threshold. Marginal calls (Convor, Porg, Beldon) should be eyeballed, not trusted to a number. Beldon female (`BeldonC_Flying_`) has 0.0 everywhere on every method: its frames are identical copies, i.e. no animation at all (separate finding).

## Table

| flier (def) | prefix | mod | frames | worst facing | body drift px | frac of body | worst step px | open-centroid px | alpha-bbox px (wrong metric) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| RSW_Sketto | `Sketto_Flying_` | SWBestiary | 4 | south | 103.8 | 1.702 | 103.8 | 108.6 | 35.5 | OFFENDER |
| RSW_Uvak | `Uvak_Flying_` | SWBestiary | 4 | south | 58.6 | 0.497 | 58.6 | 37.1 | 59.2 | OFFENDER |
| RM_FireHawk | `FireHawk_Flying_` | Pyrelands | 5 | north | 84.0 | 0.457 | 65.1 | 49.0 | 52.0 | OFFENDER |
| RSW_PekoPeko | `PekoPeko_f_Flying_` | SWBestiary | 4 | east | 132.5 | 0.429 | 132.5 | 74.7 | 24.0 | OFFENDER |
| RSW_Hawkbat | `Hawkbat_Flying_` | SWBestiary | 4 | south | 67.2 | 0.398 | 67.2 | 26.4 | 43.0 | OFFENDER |
| RSW_Bogwing | `Bogwing_Flying_` | SWBestiary | 4 | north | 56.3 | 0.380 | 56.3 | 45.2 | 31.6 | OFFENDER |
| RSW_Urusai | `Urusai_Flying_` | SWBestiary | 4 | north | 63.4 | 0.380 | 63.4 | 47.5 | 66.0 | OFFENDER |
| RSW_Hawkbat | `Hawkbat_j_Flying_` | SWBestiary | 4 | north | 53.0 | 0.308 | 35.0 | 30.4 | 34.5 | OFFENDER |
| RM_Krizzak | `RM_Krizzak_Flying_` | Abyss | 5 | north | 53.6 | 0.278 | 52.5 | 43.0 | 18.5 | OFFENDER |
| RSW_Shyrack | `Shyrack_Flying_` | SWBestiary | 3 | south | 55.7 | 0.260 | 55.7 | 37.6 | 21.0 | OFFENDER |
| RSW_Neebray | `Neebray_Flying_` | SWBestiary | 4 | east | 53.1 | 0.252 | 53.1 | 68.5 | 77.6 | OFFENDER |
| RSW_ScrapNestBird | `Whisperbird_Flying_` | SWBestiary | 4 | north | 53.0 | 0.249 | 41.0 | 38.9 | 41.5 | OFFENDER |
| RSW_Whisperbird | `Whisperbird_Flying_` | SWBestiary | 4 | north | 53.0 | 0.249 | 41.0 | 38.9 | 41.5 | OFFENDER |
| RSW_Convor | `Convor_Flying_` | SWBestiary | 4 | east | 28.2 | 0.207 | 28.2 | 34.1 | 37.5 | OFFENDER |
| RSW_Convor | `Convor_f_Flying_` | SWBestiary | 4 | east | 28.2 | 0.207 | 28.2 | 34.2 | 37.5 | OFFENDER |
| RM_FireWasp | `FireWasp_Fly_` | Pyrelands | 8 | south | 19.1 | 0.174 | 19.1 | 20.9 | 45.5 | OFFENDER |
| RSW_PekoPeko | `PekoPeko_m_Flying_` | SWBestiary | 4 | north | 17.0 | 0.098 | 17.0 | 18.9 | 1.0 | OFFENDER |
| RSW_Beldon | `Beldon_Flying_` | SWBestiary | 3 | south | 25.7 | 0.062 | 25.7 | 23.0 | 9.2 | OFFENDER |
| RSW_Porg | `Porg_Flying_` | SWBestiary | 4 | south | 1.0 | 0.005 | 1.0 | 6.8 | 14.0 | OK |
| RSW_Porg | `Porg_f_Flying_` | SWBestiary | 4 | south | 1.0 | 0.005 | 1.0 | 6.8 | 14.0 | OK |
| RM_Kirruk | `Chicken_Flying_` | WeepingStones | 0 | - | - | - | - | - | - | MISSING |
| RSW_Beldon | `BeldonC_Flying_` | SWBestiary | 3 | north | 0.0 | 0.000 | 0.0 | 0.0 | 0.0 | OK |
| RSW_BloodletterPetrel | `BloodletterPetrel_Flying_` | SWBestiary | 1 | - | - | - | - | - | - | SINGLE |
| RSW_Brezak | `Brezak_Flying_` | SWBestiary | 4 | south | 17.0 | 0.107 | 17.0 | 20.6 | 33.5 | OFFENDER |
| RSW_CanCell | `CanCell_Flying_` | SWBestiary | 4 | north | 0.0 | 0.000 | 0.0 | 3.3 | 27.5 | OK |
| RSW_ColonyPustuleHornet | `PustuleHornet_Flying_` | SWBestiary | 1 | - | - | - | - | - | - | SINGLE |
| RSW_ColonyPustuleHornetQueen | `PustuleHornetQueen_Flying_` | SWBestiary | 1 | - | - | - | - | - | - | SINGLE |
| RSW_Drexl | `Drexl_Flying_` | SWBestiary | 4 | north | 53.0 | 0.306 | 53.0 | 48.2 | 52.0 | OFFENDER |
| RSW_PustuleHornet | `PustuleHornet_Flying_` | SWBestiary | 1 | - | - | - | - | - | - | SINGLE |
| RSW_PustuleHornetQueen | `PustuleHornetQueen_Flying_` | SWBestiary | 1 | - | - | - | - | - | - | SINGLE |
| RSW_PustuleHornetSpawned | `PustuleHornet_Flying_` | SWBestiary | 1 | - | - | - | - | - | - | SINGLE |
| RSW_Sacapillar | `SacaPillar_Flying_` | SWBestiary | 1 | - | - | - | - | - | - | SINGLE |
| RSW_Screecher | `Screecher_Flying_` | SWBestiary | 1 | - | - | - | - | - | - | SINGLE |
| RSW_SmogMoth | `SmogMoth_Flying_` | SWBestiary | 1 | - | - | - | - | - | - | SINGLE |
| RSW_Strill | `Strill_Flying_` | SWBestiary | 1 | - | - | - | - | - | - | SINGLE |
| RSW_Thranta | `Thranta_Flying_` | SWBestiary | 4 | east | 53.2 | 0.443 | 53.2 | 41.0 | 59.5 | OFFENDER |
| RSW_Tibidee | `Tibidee_Flying_` | SWBestiary | 4 | north | 29.0 | 0.156 | 29.0 | 26.1 | 77.0 | OFFENDER |

## Tools that align, crop, centre, scale, trim or validate sprites (flip-book relevance)

| tool | what it does | registration basis | touches flip-book frames? |
|---|---|---|---|
| `src/RimMandrake/Utils/art/flyer_lock.py` (`lock`, `compose`, `check`) | pastes ONE wingless body plate into every frame; `align` finds the translation by counting plate pixels the frame matches in colour | **body anchor (plate)** | yes, the intended path; `check` measures locked share |
| `src/RimMandrake/Utils/art/flyer_plate_from_master.py` | builds the body plate from the master (opening to drop wings) | body anchor | yes |
| `src/RimMandrake/Utils/art/facing_regen.py` + `facing_scale_lint.py` | rescales a facing about its bottom-centre ground contact and re-centres on the alpha bbox / feet row | **alpha bbox** | not flip-book aware; would bbox-register and couple wings to body if pointed at a flip-book |
| `src/RimMandrake/Utils/art/fit_head_canvas.py`, `head_facing_fix.py` | head bbox as canvas fractions; aligns each facing's bbox bottom | **alpha bbox** | head art only; not flip-book |
| `src/RimMandrake/Utils/artpipe/facing_set_audit.py` | anchor-drift flag = bbox bottom edge, percent of canvas height; trims to bbox for coverage | **alpha bbox** (diagnostic) | finds `*_north/_south/_east` only; would mis-judge a flip-book |
| `src/RimMandrake/Utils/art/sea_shadows.py` | mean bbox w/h of two facings | alpha bbox (measurement) | no |
| `src/RimMandrake/Utils/art_checks.py` (`visible_bbox`) , `check_sprite.py`, `skills/generating-rimworld-sprites/scripts/validate_sprite.py` | silhouette bbox / centroid for validation, ref-vs-candidate offsets | alpha bbox (validation; none rewrite art) | validators only; a flip-book candidate is judged per frame on its own bbox |
| `skills/generating-rimworld-sprites/scripts/conform_sprite.py` | lays art on a reference by mask search; bbox-centre only behind `--centre` | mask search (bbox optional) | not flip-book aware |
| `src/RimMandrake/Utils/art_legibility.py` / `art_zoom_sim.py` | trims to bbox to simulate on-screen size | alpha bbox (display only) | read-only |
| `src/RimMandrake/Utils/artpipe/artpiped.py` (`_downscale_oversized_png`) | uniform BOX downscale of the whole canvas, no trim | unaffected | yes, harmless |
| `src/RimMandrake/Utils/art/art_sheet.py` (`flipbook_cols`), `sheet_slots.py`, `game_art.py` | review-sheet layout / thumbnails | unaffected (display) | display only |
| `art.py enact`/`artwrite.py`/`bulk_accept_renders.py` | copy accepted PNGs into Textures | unaffected (no pixel edits) | install path never recentres |

**Finding:** no tool in the install path registers flip-book frames on a bbox - the jitter is baked in at generation, not introduced by a normaliser. The bbox risk is latent: `facing_regen`/`facing_scale_lint`/`facing_set_audit` would be wrong to run on a flip-book. They should refuse `_Flying_` sets, or take a `--body-anchor` mode (below). Nothing was modified.

## Fix plan (no repaint here; owner reviews first)

Per offender, in order of what is cheapest and sound:
1. **Frames that are the same body, only translated** (small spans: Convor, Beldon, Porg-class): re-register by translating each frame to frame 1's body anchor with `flyer_lock.align` (plate = body), preserving wings; a new `flyer_lock register` verb (translate-only, refuses a re-posed body) is the change.
2. **Frames where the body is redrawn** (Uvak, Sketto, FireHawk, Urusai, PekoPeko m/f, Hawkbat m/f, Krizzak, Shyrack, Neebray, Whisperbird/ScrapNestBird, Bogwing, FireWasp): do NOT translate. Rebuild per the Sketto recipe: one wingless body plate per facing (`flyer_plate_from_master.py`), then `flyer_lock lock` or `compose` with wing-only layers per pose, gated by `flyer_lock check` (locked share floor 0.45). This is regen work and needs a decision per creature (cosmetic changes need owner permission, CLAUDE.md).
3. **Tool changes:** (a) `facing_set_audit.py`, `facing_scale_lint.py`, `facing_regen.py`: refuse `_Flying_<N>_` files with a message pointing at `flyer_lock`; (b) add this audit to the flier art gate as a read-only check (`flier_frame_registration.py --set <def>`), so a new flip-book cannot ship with body drift >= 2 px/2%; (c) `check` in `flyer_lock.py` should measure the shipped facings the def draws (north/south too - Sketto's lock recipe only ever covered east).
4. **MISSING sets** (Brezak, Drexl, Thranta, Tibidee declare 4 frames, Kirruk 8 vanilla Chicken frames): defs name frames that are not in `src/`; Kirruk uses vanilla Chicken art by design, the other four need either the frames or the field removed - a separate item, not part of registration.

## Tool guards (2026-10-20)

`src/RimMandrake/Utils/art/flier_guard.py` recognises flier flip-book inputs (any path, texPath or directory holding a `*_Flying_*` frame, i.e. the sets `flyingAnimationFramePathPrefix` names) and makes the alpha-bbox rewriting tools REFUSE them by name, pointing at `flyer_lock.py` / `flyer_plate_from_master.py` and this document: `facing_regen.py` (every verb), `facing_scale_lint.py` (`reseat`, `fix`), `facing_set_audit.py`, `head_facing_fix.py` (`shift`, `mask`) and `fit_head_canvas.py` (`fit`). Read-only measuring tools are unchanged (`flier_frame_registration.py`, `facing_scale_lint.py lint`, `calibrate`, `fit_head_canvas.py measure/check`, `flyer_lock.py check`). No pipeline caller depends on the old behaviour: `facing_regen_batch.py` drives only the regenerate-class base creature rows, none of which is a `_Flying_` set. Proof: `src/RimMandrake/Utils/art/selftest_flier_guard.py` (each refusal, plus a non-flier input still passing).

## Rebuild and body localiser (2026-10-20, owner by card "Fliers: rebuild all 18 now")

**Rebuild recipe** - `src/RimMandrake/Utils/art/flyer_cutout.py` (selftest `selftest_flyer_cutout.py`), one config per set in `src/RimMandrake/Utils/art/flyer_cutout_sets/<Set>.json`. Per facing ONE master frame (the painted frame that matches the grounded art) is cut into a body PLATE and wing layers by hand-drawn polygons (`protect` = head, torso, legs, tail; `wings` = one polygon per wing with its shoulder hinge). Every frame = the same plate plus the wing layers turned about the hinge (north/south: in-plane rotation, optionally half-folded by a scale where the raised span would leave the canvas; east: vertical squash about the shoulder row, negative = below the body). Membrane wings flex near the flank (motion fades in over `falloff` px from the body, read at the output pixel); insect wings turn rigidly. No pixel is generated: palette and identity are the master's; body pixels are byte-identical in every frame by construction (`plate_identical` 1.0).

**Body localiser** - `src/RimMandrake/Utils/art/flier_body_stabilize.py` (selftest `selftest_flier_body_stabilize.py`), read-only, OpenCV (runs under `<agent storage>\rimmandrake\build\cvenv`). No alpha bbox, alpha centroid, whole-image statistic or single opened mask. The body region is the person-drawn `protect` annotation of the reference frame; three estimators must agree:
- **ECC**: `cv2.findTransformECC`, MOTION_EUCLIDEAN, `inputMask` = body region, on edge-weighted grey (Sobel magnitude); gives dx, dy, angle and rho (Evangelidis & Psarakis 2008, OpenCV `findTransformECC` docs).
- **Features**: SIFT keypoints inside the body, ratio-test matches, `cv2.estimateAffinePartial2D` with RANSAC (4-DOF similarity); moving wings fall out as outliers. Pipeline after learnopencv's point-feature stabiliser (`github.com/spmallick/learnopencv`, `VideoStabilization/video_stabilization.py`: goodFeaturesToTrack -> calcOpticalFlowPyrLK -> estimateAffinePartial2D RANSAC -> dx, dy, da = atan2), descriptors instead of optical flow because frames are not a smooth video.
- **Parts**: the body region split across its principal axis into FRONT (head/shoulders) and BACK (hips/tail root) templates, each found by masked `matchTemplate` (TM_CCORR_NORMED) over a +/-12 deg sweep with sub-pixel refinement; the part-to-part line gives pitch independently.
Verdicts: LOCKED (all <= 1 px and 0.5 deg; parts <= 1.5 px / 1 deg), DRIFT, RE-POSED (ECC rho < 0.6 or < 8 RANSAC inliers: no rigid transform describes the body). Fixture proof: static body LOCKED at <= 0.05 px/deg; a body moved (+3, -2) px and turned 4 deg is recovered to 0.1 px / 0.08 deg (ECC) and 0.02 px / 0.02 deg (features), verdict DRIFT; a different drawing is RE-POSED. Overlay strips (body outline as ECC places it, part boxes, RANSAC inliers on every frame) and JSON: `D:\ClaudeWork\rimmandrake\scratch\flierfix\stab\`.

**Installed (`842bca0`)**: Sketto, PekoPeko female, FireHawk, Uvak, Hawkbat, Hawkbat juvenile - every facing LOCKED (worst 0.23 px / 0.32 deg, ECC); the shipped frames were RE-POSED in every measurable facing (PekoPeko female north/south mixed 256/512 canvases, UNMEASURED). East facings of PekoPeko/FireHawk/Uvak/Hawkbat m/j are annotated head-and-neck only, so their localiser anchor is the head.

**Instrument finding**: the mask-overlap figure above (`body drift px`) over-reports where broad wings survive the opening. Colour registration finds the body pixel-static already (0 px at 37-64 % share) in Urusai (all facings), Neebray (all), Convor m/f north/east and PekoPeko male north/south: those are not body-drift offenders; Convor south moves 2-3 px (translation only) and PekoPeko male east mixes a 512 frame with 256 ones.

**Held** (owner feedback first, 2026-10-20): Bogwing, Krizzak, Shyrack, Whisperbird/ScrapNestBird have draft configs, not installed; Urusai, Neebray, Convor m/f, FireWasp, PekoPeko male and Beldon not started.

## The four MISSING sets installed (2026-10-20, owner by card "Install donor art")

Card, 2026-10-20 7:36 PM PDT: *"Four flying creatures (Brezak, Drexl, Thranta, Tibidee) have no flight frames in the
game. Install donor art?"* -> **"Install donor art"**. The donor frames (Mlie Star Wars Animal Collection bundle,
extracted at `D:\ClaudeWork\rimmandrake\build\mlie_extract\swanimals\`) were renamed to the capitalised paths
the defs declare and installed through `art.py install` (48 files, 256x256 RGBA, real alpha; east faces right, north
is the back, south the face, checked by eye against the grounded art). Their rows in the table above are re-measured
on the installed files (`flier_frame_registration.py --set <K>`); Kirruk stays on vanilla Chicken frames.
Colour registration, the cross-check this document trusts where broad wings survive the opening, puts the body at
**0.0 px** in Drexl, Thranta and Tibidee (46-50 % share) and **4.1 px** in Brezak (56 %), so the mask-overlap
numbers likely over-report here too; none was run through `flier_body_stabilize.py` (no `protect` annotation yet).
They are donor cartoon-style frames on painterly regenerated grounded art, so the style changes at take-off.
Not rewritten (the guards refuse bbox rewriting of `_Flying_` sets); candidates for the body-lock rebuild after the
owner reviews the Sketto strip.
