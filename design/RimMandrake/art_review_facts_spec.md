# Art review FACTS — the automatic sprite review ruleset

Owner, 2026-09-15, filing this ruleset: *"We should add a series of competent art
review rules, likely made into a skill, to enable competent automatic review."*

## 🔴 The framing ruling — these are FACTS, not quality metrics

Owner, verbatim, same sitting:

> *"These aren't 'quality' or 'downscaling' type metrics. These are basic facts
> that must be true. Different kind of metric."*

This is the load-bearing distinction of the whole document, and it is what keeps
this ruleset from becoming the thing he stood down on 2026-09-14 (*"the whole
scoring metric nonsense"* — the fitted 3-band legibility gate, demoted to
advisory-only by `ART_PAINTERLY_RESTORATION_1`).

| the gate he killed | this ruleset |
|---|---|
| produced a **score** | produces a **true/false** per stated fact |
| ranked art by predicted quality | asserts a fact the art must satisfy |
| a number to be optimised | a violation to be fixed |
| aggregated into a band | 🔴 **never aggregates — no total, no grade, no ranking** |

So a finding reads *"the north facing shows a face"*, never *"facing score
0.62"*. Where a check needs a numeric tolerance, the tolerance **operationalises
the fact** ("heights agree within 15%") — it is a boundary, not a measurement of
goodness. **A fact may refuse a render**; a score may not, and no score exists
here to try.

⚠️ **A lying fact-check is worse than a missing one.** Any check that cannot
resolve its input reports `UNMEASURED` and never falls back to an assumed value.

## Why this exists — measured, 2026-09-15

The owner reviewed 28 Pyrelands rows on a sheet. My pre-fill ranked rows by
*provenance* (had the restored painterly pipeline touched it) and he overruled 6
of the first 9. Reading his notes as a group, every single reason he gave was a
**checkable fact**, not a taste call:

| his note | the fact it asserts |
|---|---|
| *"North is HUGE compared to east"* (Anooba) | facings agree on height |
| *"South isn't south"* / *"Norht isn't north"* (Anooba, Orray, Iriaz) | facings actually face |
| *"north and south aren't the right color"* (Nuna male) | facings share the creature's palette |
| *"Four legs instead of 2. Not canon"* (Gizka) | anatomy matches the canon library |
| *"cartoonish, redo to canon"* (Bolotaur, Iriaz) | style is the shipped style |

Every one of those reached his eye because nothing checked it first. Two were
already mechanically detectable and I only found them by hand: the Anooba height
mismatch measured 1.85×, and three sprite sets turned out byte-identical to
another variant — which is what actually caused the Nuna colour complaint he
could not name.

## The ruleset

### Tier A — deterministic. Pure pixel math, no model.

| # | fact | instrument | status |
|---|---|---|---|
| A1 | Transparency is real — genuine alpha, no baked matte, no opaque border ring, no near-white/near-black fill behind the subject | alpha channel inspection | built |
| A2 | Boundaries are respected — drawn content does not touch or bleed off the canvas edge, and keeps a sane margin | alpha bbox vs canvas | built |
| A3 | Size agrees across facings — **height** specifically; an animal's height does not change with viewing angle, while width legitimately does | alpha-bbox height, max/min across the set | built, validated |
| A4 | Outline is coherent — a continuous dark keyline around the whole silhouette | fraction of alpha boundary with a dark pixel inside; largest unbroken gap | built |
| A5 | No facing or variant is a duplicate of another | sha256 of pixel data across facings and across `_f`/`_m`, `X`/`XW` variants | built, validated |
| A6 | Resolution is proportional to drawSize / bodySize — the canvas is what the creature's size warrants | `drawSize × 128` → next power of two; errs GENEROUS, so undersized is the violation and oversized is a note | owed |
| A7 | Coloration agrees across facings — the same creature's palette in all three views | hue/saturation distribution over opaque pixels only, area-weighted | owed |

🔑 **A3 is validated against the owner's eye.** It reports 1.85× on the one row he
flagged by hand, and flags 8 of 19 creature rows — including 6 he had not yet
reached. A first attempt using `sqrt(w×h)` produced false positives on quadrupeds
because it conflates aspect with scale; **height only** is the correct measure.

⚠️ **A6's input is the trap.** The offline def dump DROPS `drawSize`, and
`infrastructure/artpipe/drawsize_backfill.json` holds 12 keys with zero entries
for the Pyrelands roster (recorded in `PYRELANDS_CREATURE_RERENDER_1`). The real
source is mod XML — `PawnKindDef`/`ThingDef` → `lifeStages` → `bodyGraphicData` →
`drawSize`. Unresolvable ⇒ `UNMEASURED`, never an assumed default.

⚠️ **A7 cannot catch a wrong-palette duplicate.** When `Nuna_m`'s north and south
are byte-identical copies of `Nuna_f`, their histograms match *perfectly* while
the colour is still wrong for a male. **A5 is what catches that case**, not A7.
Neither check should be described as covering it alone.

### Tier B — requires LOOKING. A vision pass, not arithmetic.

| # | fact | note |
|---|---|---|
| B1 | The facings actually face — north away, south toward, east in profile | the dominant defect; `ARTPIPE_FACING_COHERENCE_1` |
| B2 | No face or eyes are visible in the north posture | measured 2026-09-15: Anooba north is a full frontal face, teeth to camera |
| B3 | Eyes ARE visible in the south posture, **if the creature has eyes** | the conditional is required — `AA_GreenGoo` is a faceless slime and has no rear cue possible either |
| B4 | Anatomy matches the canon library | owner on Gizka: two legs, not four |
| B5 | The style is the shipped painterly style, not the stood-down cartoonish one | owner rejected Bolotaur and Iriaz as *"cartoonish"* despite both passing through the painterly wave |

⚠️ B1–B3 defeat pixel math outright. Orray's north is a clean, competent side
profile and Anooba's north is a clean, competent frontal face — both are
well-formed images with correct alpha, coherent outlines and consistent palettes.
**Only something that looks at them can tell they are the wrong view.** This is
why the ruleset has two tiers and cannot have one.

## Open questions

- **Does a Tier B violation refuse, or advise?** The framing ruling says facts may
  refuse, and B1–B3 are facts. But a vision pass is itself a judgement, so a false
  positive there blocks good art. Unruled.
- **B5 vs the advisory demotion.** "Reads cartoonish" is the owner's real
  criterion and he overruled me twice on it — but it is the closest of these to a
  taste call. Whether it can refuse is unruled.
- **Where does this run?** Inside the artpipe daemon before a render is accepted,
  or as a separate sweep over what is already on disk. Both, probably, but the
  daemon hook is what stops defects reaching his eye.

## Consumers

- `infrastructure/artpipe/` — the daemon and `fill_queue.py`; a Tier A violation
  should requeue rather than deliver.
- `ARTPIPE_FACING_COHERENCE_1` — B1–B3 are its automatic detector.
- `PYRELANDS_CREATURE_RERENDER_1` — the 28-row sheet is the validation corpus,
  with owner verdicts in `Transient/pyrelands_art_review/pyrelands_art_decisions.json`.
- `ART_PAINTERLY_RESTORATION_1` — owns the style law B5 tests against.
