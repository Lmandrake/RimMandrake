# ARTPIPE_DOWNSCALE_INSTEAD_OF_REJECT_1

Downscale the 1254x1254 worker output instead of failing `size_mismatch`.

## What is true

MEASURED 2026-09-26 (`Transient/artpipe_concurrency_measurement_2026-09-26.md`): a
`size_mismatch` job is **not** a failed generation. The image was generated, the weekly
quota was spent, and a full PNG is sitting on disk — 46 recent rejects were checked and
every one had `infrastructure/artpipe/_artsrc/<id>/<id>.png` present at 1254x1254
(324k-626k bytes). The daemon discards it solely because the canvas is not the size the
job asked for.

This is the binding constraint on artpipe concurrency. MEASURED rates:

| -N | size_mismatch rate |
|---|---|
| 3 | 1.8% (n=563) |
| 8 | 8.0% (n=25) |
| 12 | 44.4% (n=45) |
| 16 | 56% (n=16) |
| 32 | 75% (n=32) |

The account refuses nothing even at N=32 — no 429, no usage-limit text, no timeout. The
Codex agent simply skips its resize step more often as concurrency rises (median wall
clock FALLS with N: 107.9s at 8, 80.5s at 12, 65.2s at 32 — it is finishing early, not
being throttled).

## Why it matters

The weekly budget is finite and MEASURED at ~13.7 jobs per percentage point, i.e. **~1,370
image jobs per weekly window** (resets 2026-10-03 11:04). A discarded render costs exactly
as much of that budget as a kept one. At N=32 only 3.4 of every 13.7 jobs per meter point
survive.

Fixing this moves the usable concurrency ceiling from **8 to 32+** and roughly triples
throughput again on top of the 2.09x already realised.

## NEXT

Resize the harvested PNG to the job's requested canvas before the size gate, rather than
rejecting. The repo already carries the `image_scaling` skill; RimWorld sprite work also
has `generating-rimworld-sprites`' validator to keep honest about legibility after a
downscale. Keep the gate as a backstop for a result that is not merely the wrong size.

⛔ Do not delete the existing 1254x1254 renders in `_artsrc/` — they are real art and a
ready-made corpus to test the downscale against.
