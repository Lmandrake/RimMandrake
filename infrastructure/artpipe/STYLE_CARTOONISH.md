# STYLE_CARTOONISH.md — the toy-figurine lawset, preserved as an OPTION

**Not the default style.** ART_PAINTERLY_RESTORATION_1 (owner, 2026-09-14)
stood this lawset down as a requirement and restored the wave-4/5 painterly
prompt family (see `README.md`) as canonical. The owner's own words on why
this file exists at all: *"That was a good creation, and we should capture it
as 'how to make cartoonish stuff.'"* — so it is captured here, selectable by
whoever deliberately wants this look for a specific creature or mod, never
applied by default and never auto-appended to a job.

Source: `infrastructure/artpipe/README.md` history (commits `d27b960be`,
`b2d7ea116`, `52674def9`), the 2026-09-13 graded-sheet lineage, and job files
filed under that lawset (e.g. `infrastructure/artpipe/failed/*razorjack*`,
`infrastructure/artpipe/active/pyrelands_razorjack_v1_south.json`).

## The prompt shape

```
RimWorld creature sprite, side view, flat cel-shaded vanilla-RimWorld
toy-figurine art style: [canon identity + short description]. Single
creature, centered, calm standing pose, no ground shadow, no background
scenery. Heavy, clean black outline around the whole silhouette and all
major internal linework, thick enough to read clearly at standard RimWorld
zoom and below. Toy-figurine convention, strict: calm neutral standing pose
-- never mid-stride, stalking, leaping or rearing; pure flat side profile
with no three-quarter perspective; no visible musculature, tendon or
anatomy detail; flat cel shading with large simple color areas and minimal
surface texture, clean vanilla-RimWorld style. Leg policy, strict RimWorld
dialect: legs are used SPARINGLY. The body is a low-slung mass whose belly
hangs close to the ground; show at most TWO short, thick stub legs -- one
front, one rear -- with the far-side legs hidden inside the body mass
entirely; leg length at most one quarter of the body height; no joints, no
claws detailed beyond a simple rounded nub. Most of the creature is one
bold ground-hugging silhouette, like the MegaFauna and Alpha Animals mods.
```

Identity limbs (birds, spiders, wings, tentacles) were the named exception —
kept prominent-simple rather than crushed into the leg-budget rule.

## The lawset, as it stood (PYRELANDS_CREATURE_RERENDER_1 spec, 2026-09-13)

- **Toy-figurine law**: calm neutral pose, flat side profile, flat cel
  shading, no anatomy detail.
- **Leg budget**: low-slung mass, ≤2 fused stub legs, quarter-height, EXCEPT
  identity limbs kept prominent-simple.
- **Vivid distinctive coloration** — no dull-brown collapse (this half
  SURVIVES the ruling; it was never style-specific — the peko-peko cobalt
  render is the exemplar under either lawset).

## The downscale-metric craft

`src/RimMandrake/Utils/art_legibility.py` scores a sprite at 96/32/18 px
(1:1 plus two play-zoom-outs) on keyline weight, shape count/structure,
body-vs-ground value separation, and alpha coverage, calibrated against p25
of Alpha Animals' 471 shipping sprites minus margin
(`legibility_thresholds.json`, `legibility_model_fitted.json` — the
owner-graded 3-band fit, LOO ρ=0.81). `art_zoom_sim.py` renders the same
zoom tiers for a human eye check.

Sizing: `canvas` 256×256 default for a ~1-cell creature
(`drawSize×128`, next power of two) — the frostmite pilot (2026-09-12) found
a 512² source pixel-identical on screen to 256² at every VANILLA play zoom
(RMSE 5-7) while costing ~4× the atlas VRAM. **Caveat that survives into the
restored style**: that finding was measured at vanilla zoom tiers
(96/32/18 px) only, and the owner is not convinced it holds at the enhanced
zoom levels in the current mod stack — treat any resolution ceiling as
generous, not proven, until re-measured at the modded maximum zoom-in.

Reinforcement: a borderline-scoring sprite could auto-take an OUTSIDE
keyline stroke (`art_legibility.py reinforce`, opacity 1.0, 2% ring) and
rescore; outcomes were distinct statuses (`REINFORCED_PASS` ·
`legibility_borderline_unrescued` · `insufficient_margin` · `reinforce_failed`),
with the pre-stroke original kept as `*_prestroke.png`. The prompt template
also demanded ~3% transparent margin on every side so the stroke had room to
draw.

## How to use this style deliberately

1. Write the prompt from the shape above, filling in the creature's canon
   identity and a short description in place of the bracketed text.
2. Set `style_notes` on the `fill_queue.py` row to name the toy-figurine
   convention explicitly (as done historically — see the sourced job files)
   so a reader of the job later understands why the prompt reads this way.
3. If legibility scoring/reinforcement is wanted for this job specifically,
   set `ARTPIPE_LEGIBILITY_THRESHOLDS=<path to legibility_thresholds.json>`
   for that run — the gate is disabled by default (advisory-only,
   ART_PAINTERLY_RESTORATION_1) and must be opted into per invocation.
