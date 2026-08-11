# LLM-in-the-loop improvement — `coastal_mesa` (iteration 1)

The region decomposition, judgments, and edits below were authored by the LLM reasoning over the perceived map; this script only executed the primitives and measured the result.

## Region decomposition + judgment (LLM)

Scores 0-10. realism = looks like a real place · interest = worth exploring/fighting over · tactical = meaningful combat geography · artificiality = looks generator-stamped (LOWER is better).

| Region | Real | Intr | Tact | Artif | Problem → Intent |
|---|---|---|---|---|---|
| Ocean (W strip, x0-21) | 3 | 2 | 5 | 9 | ruler-straight coast, hard sand/ocean line, only 2 depth bands - reads stamped-on → fractalize the shoreline and lay a proper deep->shallow->beach->flat gradient |
| Central sand flat (x22-55) | 5 | 2 | 2 | 4 | large featureless dead zone - no cover, no reason to move through it → add a dry wash/old path across it and a scatter of vegetation + a small hill for cover |
| Rock massif (NE + SE lobes) | 6 | 4 | 7 | 3 | solid inert stone - a mountain with no interior and abrupt feet → carve a mysterious cave chamber into the SE core; add talus/hill at a foot |
| Gravel outcrops (scattered) | 6 | 3 | 4 | 4 | fine as texture but a bit noisy; one can host a ruined structure → site an old ruin on the mid-west outcrop as a landmark; smooth confetti |

## Edits executed (each tied to a region + rationale)

1. **Roughen the coastline** _(region: Ocean, op: `fractalize_edge`, 80 cells)_
   - A dead-straight N-S coast is the map's biggest artificiality tell. Push shallow water in/out irregularly so the land/sea boundary meanders like a real shore.
2. **Deep->shallow->beach->flat gradient** _(region: Ocean, op: `terrain_gradient`, 3720 cells)_
   - Real coasts ramp through depth then a wet beach then dry flat. Repaint the coastal band x0-30 W->E as ocean deep, ocean shallow, wet sand, dry sand so there is no hard line.
3. **Old dry wash / trail across the flat** _(region: Central sand flat, op: `path`, 165 cells)_
   - A gravel wash from the SW toward the NE massif gives the empty center a line of movement, a subtle chokepoint, and a story (old traffic). Waypoints stay in open sand per the briefing.
4. **Sparse hardy vegetation on the flat** _(region: Central sand flat, op: `scatter`, 125 cells)_
   - Bare sand with zero flora looks lifeless. Sprinkle mossy/soil patches (desert scrub) lightly, clumped, only over sand, so a few plants cluster in hollows.
5. **Small outcrop hill mid-flat** _(region: Central sand flat, op: `hill`, 84 cells)_
   - A lone low hill at ~(38,52) breaks the dead zone, gives high-ground cover, and reads as a natural erosional remnant near the wash.
6. **Mysterious cave chamber in the SE massif** _(region: Rock massif, op: `carve_chamber`, 251 cells)_
   - Region #3 (mountain, centroid ~92,92) is solid RockFace. Carve a chamber into its core - carve_chamber only eats solid rock, so it stays enclosed. A cave gives a fortress/high-risk interior.
7. **Talus foot at the NE lobe** _(region: Rock massif, op: `hill`, 63 cells)_
   - The NE rock lobe (~70,32) meets sand abruptly. A rubble hill at its foot softens the transition and adds light cover on that approach.
8. **Ruined structure on the mid-west outcrop** _(region: Gravel outcrops, op: `rect`, 49 cells)_
   - Outcrop #6 (~28,61) is a natural landmark site. Lay an ancient-concrete footprint as a ruined building pad - a story beat and a defensible strongpoint.
9. **Kill single-cell confetti** _(region: Gravel outcrops, op: `smooth`, 151 cells)_
   - 7 tiny patches flagged by the fragmentation metric. Majority-smooth non-water families so lone specks dissolve into their surroundings.

## Metric deltas (objective guardrails, not the judge)

- **transition_coherence**: 1.0 → 1.0  (flat)
- **fragmentation_tiny_patches**: 7 → 18  (worse)
- **family_diversity**: 0.9211 → 0.6836  (worse)  _(diversity is informational — interpret in context)_

## Layering notes (pawns / items / story)

- Cave chamber: layer ancient danger or an infestation deep in - the interior is not free real estate.
- Ruined structure: a few slain ancients + salvage; ties to the crashed-Factory-ship scavenger theme.
- Old wash/path: expect raiders to path along it - anchor a killbox where it meets the base.
- Coastal mud beach: brackish, non-potable - reinforces the water-scarcity pillar (must desalinate).
