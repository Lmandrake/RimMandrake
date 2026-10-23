# ART_PAINTERLY_RESTORATION_1 — MAJOR RULING: the painterly style returns, the cartoonish pipeline stands down

Filed by BENCH 2026-09-14, at the first in-game art walk, on the owner's word.

## Owner ruling, verbatim (2026-09-14)

> "MAJOR RULING. Please stand down the 'cartoonish' art regeneration pipeline.
> That was a good creation, and we should capture it as 'how to make cartoonish
> stuff.' But I'm looking at the Art we were making before such as the Ronto on
> this map, and it's absolutely beautiful. So let's go back to just how it was
> before we did all of this HUGE BLACK stuff. It's back to OK to have legs, OK
> to be high resolution (as long as the user will actually see the resolution)
> etc. Go back to that art prompt you were using before, before we did the
> whole scoring metric nonsense for art, and let's keep going. It's really
> beautiful, and we love it."

## The restored style — archeology result

The exemplar the owner pointed at (Ronto, this map) is job `ronto_v1_east`
(`infrastructure/artpipe/done/ronto_v1_east.json`, ART_REGEN_WAVE4_QUEUE_1,
2026-09-11, canvas 512). **The wave-4/5 prompt family is the canonical style
again**, shape:

> "RimWorld creature sprite, side view, **painterly vanilla-RimWorld animal art
> style**: [canon identity + rich anatomical description — legs, hide, folds,
> real creature]. Single creature, centered, standing pose, no ground shadow,
> no background scenery. Heavy, clean black outline around the whole silhouette
> and all major internal linework, thick enough to read clearly at standard
> RimWorld zoom and below."

## STOOD DOWN (was owner-ruled 2026-09-13; reversed by this ruling)

- The toy-figurine law (calm-flat-cel, no anatomy detail) as a REQUIREMENT.
- The leg budget (≤2 fused stubs, quarter-height).
- The "no painterly" word-ban — the word is back, it names the style.
- The HUGE-BLACK keyline mandate and the automatic outside-stroke reinforce
  pass as requirements.
- The fitted 3-band legibility gate as a hard REFUSAL ("the whole scoring
  metric nonsense") — it may live on as an advisory number, never as a
  rejector.
- The 256 canvas ceiling as a refusal: high resolution is OK **as long as the
  player will actually see the resolution** (owner's words) — drawSize×128
  next-pow2 remains the sizing rule of thumb.

## SURVIVES (explicitly, so propagation does not overshoot)

- **ARTPIPE_FACING_COHERENCE_1** — N faces away, S faces toward, facings
  derived from one master. Orthogonal to style; the owner ruled it minutes
  before this and it stands.
- **Canon reference library law** — prompts for canon creatures cite the
  library; identity is not style.
- **reference= means reskin-validate** — semantics unchanged.
- **The artpipe daemon/queue machinery itself** — the pipeline runs; only the
  style law and metric gate change.

## 🔴 The cartoonish capture is REVOKED — owner, 2026-09-15

*"Please close immediately as terminated by user, leave no trace of
cartoon-generating art!"* The earlier instruction to preserve the toy-figurine
craft as a selectable style option is **withdrawn**. `STYLE_CARTOONISH.md`, the
TOYFIG_LAW_PILOT_1 pilot art, and all 30 toyfig job specs are deleted. Painterly
is the only style law; there is no cartoonish option to select. Nothing is owed
here.

## Propagation debt (delete-don't-supersede, each in place)

- `infrastructure/artpipe/README.md` — LOCKED RULES block and gate description
  rewritten to match this ruling.
- `fill_queue.py` — ceiling refusal relaxed per above; downscale auto-append
  block removed or made style-conditional.
- `artpiped.py` — legibility gate demoted to advisory
  (`ARTPIPE_LEGIBILITY_THRESHOLDS=` empty disables; daemon restart required).
- `PYRELANDS_CREATURE_RERENDER_1` spec §2 — lawset bullet now points here.
- Session memories asserting the lawset as canon — updated same day.
- The 7 Pyrelands invented creatures + canon 5 rendered today in the cartoonish
  style: owner will verdict in-game; re-render through the painterly family as
  he directs (do NOT mass-revert unbidden).

## Re-ruling debt (owner, same sitting)

> "This is going to mess up what art we have and haven't done yet. We have to
> examine them and rule it again, and that sucks, but it's the way we're gonna
> do it."

Every render produced or accepted under the cartoonish lawset (2026-09-12 →
2026-09-14 waves) is back on the table: EXAMINE and RE-RULE each, in-game walk
first, sheets where side-by-side helps. No acceptance from that era is
presumed valid; no render is presumed dead either — the Green Goo praise shows
some survive on their merits.

## Resolution caveat (owner, same sitting)

The resexp finding ("stored resolution above 128 changes nothing measurable")
was measured at VANILLA zoom tiers (96/32/18 px). Owner: "I'm not sure that's
true with the enhanced zoom in our current mod stack." Until re-measured at the
modded maximum zoom-in, canvas sizing errs GENEROUS (512 fine for large
drawSize) — the old ceiling logic must not quote resexp against high-res.
