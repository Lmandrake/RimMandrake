# register-analytics (PROPOSED SKILL — draft, not installed)

_Drafted 2026-09-05 by the creature-distribution analysis pass. skills/ is curated
only in fresh-context sessions; this file is the full draft for that session to
adopt, trim, or reject. Proven on: creature register (figs 1–8,
`design/Jawa/worldbuilding/review/viz/`), where the method found a doctrine patch
that skipped our own mod and quantified three biome curation workloads._

## Description (for the skill listing)
Turn any `*_register_rows.json` (creatures, plants, furniture, turrets, pawns —
anything gen_*_register.py emits) into a decision-grade distribution analysis: the
live-population discipline, provenance-based law classification, reference laws
drawn never fitted, per-mod strips, named outliers, and a committed
generator + portfolio notes pair. Use when the owner asks "analyze the register",
"what's the distribution", "who's the outlier", "did the pass land", or before/after
any normalization pass that moves a stat many defs share.

## The method

### 1. Population discipline first (the wrong-population trap)
- **LIVE = not cut, not commonality-zeroed, not modDropped.** Compute it first,
  print it, use it everywhere. Rankings over the full register are a different and
  WRONG worklist (proven twice now: the Jurassic 2.5× "finding" was mostly cut
  creatures; 65 of 232 out-of-band sizes were cut).
- Rows with `statsResolved: false` are UNMEASURED on every stat axis — name them,
  drop them, never zero-fill.
- Anything the register cannot see (life stages, DPS shapes, C#-driven behavior)
  is written UNMEASURED with the instrument that could measure it named.

### 2. Classify by PROVENANCE, not by tolerance
When testing a population against a law (yield curves, size laws, damage bands):
- **A def that never authored the stat follows the engine default by
  construction.** Split `statBase present` from `statBase absent` BEFORE any
  tolerance test — tolerance-testing the default population manufactures fake
  escapes wherever the engine curve bends (the meat postProcessCurve kink at
  bs 0.286 produced 43 of them before this fix).
- The interesting classes fall out: engine-default / authored-conforming /
  authored-escaping / authored-zero. Every escape gets a NAME and a judgment
  (intentional-with-reason vs unexplained), never just a count.
- Where a project patch generates per-mod operations (`PatchOperationFindMod`
  blocks), check which mods it MISSED — a generated patch silently skips mods
  added after it was cut. That check found RSW Sea Beasts unpatched.

### 3. Reference laws are measured, never fitted
Draw the law the project WROTE (doctrine docs, patch generators, vanilla source),
cite where each came from on the figure, and never fit a curve to the population
being judged. If two laws coexist (vanilla default + doctrine override), draw both;
the population between them is the finding.

### 4. The standard views (pick per question, one question per figure)
- **law scatter** (RELATIONSHIP): x = the driver (log if spanning decades),
  y = the governed stat, reference laws, provenance classes as hue+shape, zero
  handled on a disclosed rail (log axes cannot show zero).
- **per-mod strip** (COMPARISON_ACROSS_GROUPS): one shared derived measure
  (÷ the driver so mods compare), every def a jittered point, medians as ticks,
  target band shaded, in-band share as zero-anchored gutter bars, n<8 mods pooled
  and labeled. This is the view that shows WHERE a normalization pass landed.
- **law-gap panel** (DEVIATION): per group (biome, faction, tier), the population
  on the law's own axis with the banned region shaded and violators weighted by
  the stat that decides how much they matter (spawn commonality, market value).
  When the law gives prose not numbers, state your thresholds ON the figure as
  analytic choices.
- **dominance scatter / cross-tab heatmap** as supplementary exploration, labeled
  as such — honesty over quota; don't score filler members.

### 5. Ship shape
- One committed generator per portfolio (`gen_<subject>_portfolio.py`) writing
  PNG+SVG into `review/viz/`, plus `PORTFOLIO_<subject>.md` carrying: decision
  frame, question slate, member case files with repair history, trade-off cards
  or condensed equivalents, 4-axis score, and a findings section where every
  number is MEASURED and every outlier is named.
- Run the MandrakeVisuals stack (visual-intent → … → visual-render-qa) and
  actually LOOK at the rendered PNGs before shipping; one inspect-and-repair
  round minimum. Figures are the before-photos of the pass they guide —
  re-render after the pass as validation.
- Commit generator + figs + notes together, push immediately.

## Failure modes this skill exists to prevent
- Ranking cut content into a worklist (wrong population).
- Tolerance-testing engine defaults against a law with a kink (fake escapes).
- Fitting the reference to the data being judged (self-licking law).
- A count where a name is needed ("16 escapes" without the 16 defNames).
- Redoing a question a sibling portfolio already answered (check
  `review/viz/PORTFOLIO_*.md` first; extend, don't fork).
