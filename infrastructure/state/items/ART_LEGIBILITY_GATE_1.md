# ART_LEGIBILITY_GATE_1 — automated downscale-legibility gate + the resolution experiment

Filed and worked by BENCH, 2026-09-13, on the owner's direct instruction
("work that item hard right now"). Owner's ask: automated quality assurance
at the requested 1:1 zoom plus two zoom-outs, with metrics that clearly
measure it — and prove or refute "it may push us to more resolution than the
game natively uses."

## spec

Built `src/RimMandrake/Utils/art_legibility.py`: renders a sprite exactly as
`art_zoom_sim.py` does (trim → BOX downscale ≈ GPU mipmap → composite over
Ash'karr brown) at tiers 96/32/18 px, then measures four normalized metrics —
keyline (boundary ring darker than interior + distinct from terrain),
structure (interior gradient energy + luminance spread after downscale),
ground (body-vs-terrain separation + camouflage fraction), coverage (alpha
area retained vs native silhouette). Composite 0-100 per tier; fixed weights,
CALIBRATED thresholds (never guessed) at
`infrastructure/artpipe/legibility_thresholds.json`. Wired into `artpiped.py`
after the geometry validator: transparent-bg candidates below the line fail
as `legibility_below_gate` with the weakest metric named (feeds the retry);
same skip/error discipline as run_validator; `ARTPIPE_LEGIBILITY_THRESHOLDS`
env overrides (empty = disabled — how the e2e selftests run).

## verify

- Instrument reproduces the frostmite pilot: known-bad 46.3 vs known-good
  64.3 at 32 px; gate at p25-of-corpus separates them (bad FAILS naming
  keyline weakest; good passes with margin). Fixtures committed at
  `src/RimMandrake/Utils/artpipe/testdata/legibility_known_{bad,good}_256.png`.
- Calibration corpus: 471 Alpha Animals shipping sprites (MEASURED
  distribution in the thresholds file: p25 65.5/52.2/41.1 at 96/32/18 px).
- Selftest `test_legibility_gate_rejects_mud_passes_shipping_and_disables_cleanly`
  covers reject/pass/env-disable/daemon-wiring; full artpipe selftest: all
  checks passed; run_selftests: 50/51 → re-run green after the fix.

## criteria — the resolution question, MEASURED

`resexp` over 35 hi-res _artsrc masters, stored at 64/128/256/512 (LANCZOS,
the shipping downscale), each rendered to 96/32/18 px (BOX, the GPU path):
score deltas between 128/256/512 stored are ≤0.1 at EVERY tier; only
64-stored drops (−5 at 96 px). Pixel RMSE corroborates (≤5.7 worst).
**The owner's statement is REFUTED: the gate does not push resolution up.
The knee is ~128 px stored for a 1-cell creature — set by the 1:1 tier
alone — and the 256 default already has 2× headroom. Legibility at play
zooms is bought with keyline/shapes/contrast, not pixels.**
Raw rows: `Transient/legibility_resexp_2026-09-13.json`.

## Watch out

- The running daemon must be RESTARTED to pick up the gate (it holds old
  code); active/ was empty at the time — reconciliation covers a mid-job
  restart anyway.
- Thresholds decay with the corpus: if AA leaves the mod list or our own
  accepted art becomes the better exemplar pool, recalibrate — the file
  records corpus_n and gate_pct.
- The gate judges CREATURE-shaped transparent sprites; buildings ship at
  bigger canvases per the skill's drawSize table and were not calibrated
  here — extend the corpus before gating building art.
