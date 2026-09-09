# Gemini contrast batch — ART_PIPELINE_DAEMON_1, 2026-09-09

Image-conditioned `gemini_image.py generate --ref <same-facing reference>` against
the same 2 machines (AutomatedSmelter Wrecked/Repaired) × 4 facings (N/S/E/W) the
Codex calibration (`Transient/artpipe_calibration_2026-09-09/CALIBRATION.md`) used.
Hard cap was 20 generations; **8 used, 0 retries** (every job passed validation on
the first attempt, no quota/billing error encountered).

## Per-job validator verdicts

Pipeline: `gemini_image.py generate --ref` → `rembg_cut.py` (alpha cutout, no
native alpha from this API) → `conform_sprite.py` (fit to reference canvas) →
`validate_sprite.py --reference <ref> --candidate <conformed>`.

| job | model | gen time | rembg opaque% | validator |
|---|---|---|---|---|
| wrecked_north | gemini-3-pro-image | 20.5s | 59% | **PASS** (1 warn: faint soft-edge pixels) |
| wrecked_south | gemini-3-pro-image | 16.6s | 60% | **PASS** (1 warn) |
| wrecked_east | gemini-3-pro-image | 41.2s | 62% | **PASS** (2 warn: soft-edge + minor blue rim spill) |
| wrecked_west | gemini-3-pro-image | 16.8s | 62% | **PASS** (1 warn) |
| repaired_north | gemini-3-pro-image | 17.3s | 60% | **PASS** (1 warn) |
| repaired_south | gemini-3-pro-image | 16.2s | 60% | **PASS** (1 warn) |
| repaired_east | gemini-3-pro-image | 17.5s | 62% | **PASS** (1 warn) |
| repaired_west | gemini-3-pro-image | 15.4s | 62% | **PASS** (1 warn) |

All warnings are the validator's faint-alpha / rim-spill advisories, none are
rejections. Conformed subject boxes land within 0-3px and <1% aspect of the
reference on every job (e.g. wrecked_north: subject 367x537 at (71,49) for
both reference and candidate).

## Pass rate: Gemini vs Codex

| | PASS | WARN-only PASS | REJECT |
|---|---|---|---|
| **Gemini** (image-conditioned, this batch) | **8/8** | 8/8 | 0/8 |
| **Codex** (generate-mode, calibration, N4) | 0/8 | — | 8/8 |
| Codex (generate-mode, all N∈{1,2,4,6}) | 0/32 | — | 32/32 |

Codex's generate-mode failures were geometric (subject height/aspect off the
reference by up to -27%, squashed proportions) because it word-anchors the
machine instead of conditioning on the reference image. Gemini's `--ref`
conditioning fixes exactly that failure mode — the whole point of this batch.

## Spend

8 images × `gemini-3-pro-image` (Nano Banana Pro), all at 1K/2K output
resolution (928x1152 / 1152x928, no 4K requested). At Google's published list
price of **$0.134/image** for this tier: **≈ $1.07 of the $25 prepaid balance**
(≈4.3%). This is a list-price approximation, not a live billing read —
no billing/quota error surfaced during the batch (all 8 `exit_code=0`), so
nothing suggests the balance was in danger.

## Cross-facing consistency (does N/S/E/W look like the same machine)

Looked at `CONTRAST_sheet.png` (8 rows × [reference | Gemini | Codex N4]):

- **Wrecked**: all 4 facings hold the same dome silhouette, same torn-hole
  damage language, same rust-brown palette, same vent-bay layout — reads
  unambiguously as one machine turned four ways, and the silhouette outline
  tracks the reference almost exactly in every facing.
- **Repaired**: north/south/west share the same grey-green metal and amber
  indicator-light ring; **east drifts slightly cooler/more saturated
  green-teal** with slightly heavier pipe detailing than the other three —
  a real but minor palette inconsistency, not a different machine (dome
  shape, rivet layout, vent bays and light ring all still match).
- **Gemini vs Codex, both axes**: Gemini's four facings are visibly the same
  object as each other AND as the reference; Codex's four facings are
  consistent with *each other* (same rendered machine) but not with the
  reference — Codex reinvented a taller, 3D-shaded, differently-proportioned
  furnace with no image conditioning to anchor it, which is exactly why it
  scored 0/32 on the geometric gate.

## Files

    out/{job}.png            — raw gemini-3-pro-image generations (RGB, no alpha)
    cut/{job}.png            — rembg alpha cutouts
    conformed/{job}.png      — fit to reference canvas/pose
    manifests/{job}.json     — per-job prompt, ref, timing, exit code
    validate_gemini_output.txt — full validate_sprite.py transcript, all 8 jobs
    CONTRAST_sheet.png       — the 8-row x 3-column comparison sheet
    CONTRAST.md              — this file
