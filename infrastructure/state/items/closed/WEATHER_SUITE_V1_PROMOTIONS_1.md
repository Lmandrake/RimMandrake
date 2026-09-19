# WEATHER_SUITE_V1_PROMOTIONS_1

`WEATHER_SUITE_SLICE_1`'s original v1 ladder (terminator storms, dark-side
auroras, forecasting) is fully built, confirmed clean-building, and
superseded to this item (FOUNDRY fork, 2026-09-02). Same day, the owner's
`PROPOSAL_SUITE_REVIEW_1` sitting promoted three more systems from v2 to
v1 in `design/Jawa/proposals/weather_suite_deep_design.md` (§30-44, frozen
source `design/Jawa/worldbuilding/review/proposal_suite_review.decisions.json`).
None of the three exist anywhere in `src/RimStarWars/WeatherSuite/` or
`src/RimUtinni/AshkarrWeatherSuite/` — genuinely new scope, not a gap in
already-claimed work.

## spec

Three systems, each closer to its own item than one combined build —
**recommend splitting on claim**, don't build all three in one pass:

**1. Glass-sand storms** (doc §2, owner: *"Love this! Violent weather for
the win."*) — least C#, most bounded. A `WeatherDef GlassStorm`, rare, high
weight only during an active static season (see #2), vanilla-shaped
`IncidentDef`/stat-offset work: sight/accuracy penalties, sparse shrapnel
ticks (armor-sensitive), solar-panel fouling + wind-power surge
simultaneously. **The one C# hook needed**: a lightning-strike-resolution
hook that drops a harvestable "fulgurite node" prop on bare silica terrain
after a strike during the storm — doc says this is precedented by the
Pyrelands fire-glass hook in the sibling fire-ecology doc; find and mirror
that pattern rather than inventing a new one.

**2. Static seasons** (doc §3, owner: *"...this should add battery power
while doing all the other things you said. Accelerates the rate at which
droids become... eccentric."*) — needs a `GameCondition` subclass with an
escalating tier state machine (vanilla conditions are mostly
single-intensity; this ratchets: early=minor shocks/accuracy penalty,
mid=battery drain increase + droid coherence-need disruption, late=resolves
into a Glass Storm or fades). The owner's note ADDS "battery power" drain
explicitly (the doc's own §3 draft already has this) — confirm the disruption
hook works on `ArtificialBeings.CompCoherenceNeed` (doc says "already
confirmed present and ungated... worth a spike to confirm the comp exposes
a clean external hook before committing" — do that spike first, don't
assume). Glass storms (#1) should be gate-weighted to fire mainly while a
static season is active, per the doc's "signature payoff weather" framing.

**3. Spore blooms** (doc §6, owner: *"Yes! Awesome. Also poisons wildlife
providing a lot of free meat. Hiding indoors helps a lot."*) — a
`WeatherDef SporeBloom` triggered near ocular-forest terrain, tiered by
distance (near-source haze + toxicity, downwind cosmetic haze + navigation
tell, post-bloom a short abnormal-plant-growth window per R-H3). 🔴 **The
owner's note adds wildlife poisoning + free meat, which is NOT in the doc's
§6 draft** (that section only covers pawn toxicity and plant regrowth) —
this needs its own small mechanic: wildlife in the bloom radius dies/is
poisoned and leaves corpses, i.e. a genuine free-meat windfall, not just
flavor text. Don't skip this half of the ruling because the doc draft
didn't cover it.

## verify

Each system gets its own build/deploy/live-quicktest cycle following
`WEATHER_SUITE_SLICE_1`'s own established pattern (that item's closing
notes name the exact commit and verify steps to mirror). Static seasons'
`CompCoherenceNeed` hook needs the spike confirmed BEFORE the state machine
is built around it — don't build the hook on an assumption.

## criteria

- [ ] Claimed as (recommended) three separate sub-passes, not one.
- [ ] Glass-sand storms: `WeatherDef` + fulgurite-node lightning hook, built,
      deployed, live-quicktest-owed.
- [ ] Static seasons: `GameCondition` escalating state machine + confirmed
      (not assumed) `CompCoherenceNeed` hook, built, deployed,
      live-quicktest-owed.
- [ ] Spore blooms: `WeatherDef` + the owner's wildlife-poison/free-meat
      addition (not just the doc draft's pawn-toxicity/plant-regrowth half),
      built, deployed, live-quicktest-owed.
