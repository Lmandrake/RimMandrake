## spec
On a 4 m (8 level) covered spiked pit, two raiders are held and no free raider gets a ladder job. `ProofFetchPlan` reads
`depths=0/8 reach=6 slots=null` on every planned read (game b, build 58cfa254e87e). On a 3 m pit the same raid sets a
ladder and brings a man out (`sc_fetch_fallen` PASS). The limit is our own rule, not a bar: `portableLadderMaxLevels` is 6,
and `RaiderTrenchChecks` pins "4 m is past a 3 m ladder (shallower pits only)".

Evidence against leaving it: `scenes.json` `sc_pit_trap_raid` expects "the rest try a ladder under arrows, are driven off,
the fallen become prisoners in the pit". By his card a pit is a prison only when superdeep (4 m). So one pit cannot show
both today.

His question: should raiders reach a fallen comrade in a 4 m pit (a longer rescue ladder, more wood), or does a 4 m pit
stay ladder-proof and the showcase use a 3 m pit for the ladder beat?

## verify
Acceptance test: none, an owner decision. If he says "reach it": `concept_scenes.py` `_pit_trap(depth=8)` with the FETCH
rows is the check; it is red today (`slots=null`, no ladder).

## refs
file: design/concepts/FlowWorks/version/in_game/visit_2/evidence/exp/fetch_fourmetre_pit_no_ladder_20261121.json
file: design/concepts/FlowWorks/version/in_game/visit_2/evidence/exp/fetch_fourmetre_pit_no_ladder_20261121.png
file: src/RimMandrake/FlowWorks/Source/Superdeep/RM_RaiderTrenchMath.cs

## criteria
- He has answered; the answer is recorded on this item, and the build or the showcase follows it.

## What the card said

<!-- answered 2026-11-21T19:48:54Z; recorded by `note` (OWNER); written by rimflow, never by hand -->

**Question:** FlowWorks pits. Last night's fix makes raiders fetch a ladder for a comrade who fell in a pit, and it works on a 3 m pit. A portable ladder reaches 3 m. A pit only holds prisoners at 4 m (your earlier ruling), so at a 4 m pit raiders do nothing: no ladder job at all. Your pit-trap showcase says the rest 'try a ladder under arrows, are driven off, the fallen become prisoners'. One pit cannot show both today. (Hard to read? Type STE, Binding or Both for a rewrite.) What should raiders do at a 4 m prison pit?
**Picked:** Try, and fall short (Recommended)
**Its description:** Why: it is your showcase sentence as written. Raiders carry a ladder to the 4 m pit, it is visibly too short, and they are driven off. Buys the drama and keeps 4 m a true prison. Costs a new failed-attempt behaviour to build and test live. Recommended: the only option that matches the showcase without weakening the prison.
**Other options:** 4 m stays ladder-proof · A longer rescue ladder
