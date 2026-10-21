# Flier flip-book registration audit - 2026-10-20

Item: `FLIER_FRAMES_AUDIT_BODY_NOT_WING_EXTREMES`. Owner 2026-10-20: *"Their bodies should be kept static while the wings flap. So looking for extreme of the graphic image is not useful and couples wing motion to body motion incorrectly."*
Offline, read-only. Instrument: `src/RimMandrake/Utils/art/flier_frame_registration.py` (selftest `selftest_flier_frame_registration.py`). Raw numbers: `D:\ClaudeWork\rimmandrake\scratch\flierframes\audit.json` / `audit.txt`; contact strips (red cross = rigid-body centroid, blue = alpha-bbox centre, green lines = frame 1's body centroid) in `D:\ClaudeWork\rimmandrake\scratch\flierframes\strips\`.

## Result

37 (def, prefix) flip-book sets reference `flyingAnimationFramePathPrefix` in `src/` (male and female prefixes counted separately, shared art counted per def). 22 have 2+ frames on disk; **18 are OFFENDERS** (body moves >= 2 px AND >= 2% of body size between frames in at least one facing). Worst: RSW_Sketto south (103.8 px, 1.7x its body size - frame 3 is a different pose), RSW_PekoPeko female east (132.5 px), RM_FireHawk north (84 px). Five defs declare 4-8 frames but ship none in `src/` (MISSING: RM_Kirruk, RSW_Brezak, RSW_Drexl, RSW_Thranta, RSW_Tibidee); 10 sets are single-frame (no animation, nothing to jitter).

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
| RSW_Brezak | `Brezak_Flying_` | SWBestiary | 0 | - | - | - | - | - | - | MISSING |
| RSW_CanCell | `CanCell_Flying_` | SWBestiary | 4 | north | 0.0 | 0.000 | 0.0 | 3.3 | 27.5 | OK |
| RSW_ColonyPustuleHornet | `PustuleHornet_Flying_` | SWBestiary | 1 | - | - | - | - | - | - | SINGLE |
| RSW_ColonyPustuleHornetQueen | `PustuleHornetQueen_Flying_` | SWBestiary | 1 | - | - | - | - | - | - | SINGLE |
| RSW_Drexl | `Drexl_Flying_` | SWBestiary | 0 | - | - | - | - | - | - | MISSING |
| RSW_PustuleHornet | `PustuleHornet_Flying_` | SWBestiary | 1 | - | - | - | - | - | - | SINGLE |
| RSW_PustuleHornetQueen | `PustuleHornetQueen_Flying_` | SWBestiary | 1 | - | - | - | - | - | - | SINGLE |
| RSW_PustuleHornetSpawned | `PustuleHornet_Flying_` | SWBestiary | 1 | - | - | - | - | - | - | SINGLE |
| RSW_Sacapillar | `SacaPillar_Flying_` | SWBestiary | 1 | - | - | - | - | - | - | SINGLE |
| RSW_Screecher | `Screecher_Flying_` | SWBestiary | 1 | - | - | - | - | - | - | SINGLE |
| RSW_SmogMoth | `SmogMoth_Flying_` | SWBestiary | 1 | - | - | - | - | - | - | SINGLE |
| RSW_Strill | `Strill_Flying_` | SWBestiary | 1 | - | - | - | - | - | - | SINGLE |
| RSW_Thranta | `Thranta_Flying_` | SWBestiary | 0 | - | - | - | - | - | - | MISSING |
| RSW_Tibidee | `Tibidee_Flying_` | SWBestiary | 0 | - | - | - | - | - | - | MISSING |

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
