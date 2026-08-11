# LLM-in-the-loop improvement — `coastal_mesa` (iteration 2)

The region decomposition, judgments, and edits below were authored by the LLM reasoning over the perceived map; this script only executed the primitives and measured the result.

## Region decomposition + judgment (LLM)

Scores 0-10. realism = looks like a real place · interest = worth exploring/fighting over · tactical = meaningful combat geography · artificiality = looks generator-stamped (LOWER is better).

| Region | Real | Intr | Tact | Artif | Problem → Intent |
|---|---|---|---|---|---|
| Ocean (W strip) | 3 | 2 | 5 | 9 | v1 fixed the straightness but introduced a continuous straight MUD WALL - traded one artifact for another; gradient ran after fractalize and re-straightened it → depth ramp ONLY (deep->shallow->sand), then fractalize the coast LAST, then scatter mud as wet-beach patches not a band |
| Central sand flat | 5 | 2 | 2 | 4 | v1 wash + hill good; vegetation too faint to read → keep wash+hill, raise vegetation density and give it a couple of soil clumps |
| Rock massif | 6 | 4 | 7 | 3 | v1 cave + talus foot worked well → keep as-is |
| Gravel outcrops | 6 | 3 | 4 | 4 | v1 ruin + smooth worked → keep; smooth again at the end to absorb new confetti from the coast edits |

## Edits executed (each tied to a region + rationale)

1. **Depth ramp only (no mud band)** _(region: Ocean, op: `terrain_gradient`, 2040 cells)_
   - Repaint just the water column x0-16 W->E as deep->shallow->shallow->sand. No mud in the order, so no brown wall. This sets a clean depth ramp that we will then roughen.
2. **Wet-beach mud patches (not a band)** _(region: Ocean, op: `scatter`, 89 cells)_
   - A brackish beach is patchy, not a stripe. Scatter Mud only onto sand cells in the narrow shore band x10-20, low density and clumped, so wet spots cluster near the waterline.
3. **Old dry wash across the flat** _(region: Central sand flat, op: `path`, 137 cells)_
   - Same gravel wash SW->NE; a line of movement and a soft chokepoint through the dead center.
4. **Desert scrub (denser)** _(region: Central sand flat, op: `scatter`, 216 cells)_
   - Raise mossy scatter density and cluster it so vegetation actually reads on the flat.
5. **Small fertile hollow by the wash** _(region: Central sand flat, op: `blob`, 16 cells)_
   - One soil clump near the wash bend (~44,62) - a plausible catchment where runoff pools, and the map's only decent farm spot (scarcity anchor).
6. **Small outcrop hill mid-flat** _(region: Central sand flat, op: `hill`, 84 cells)_
   - Low hill at ~(38,52) for high-ground cover in the dead zone.
7. **Cave chamber in SE massif** _(region: Rock massif, op: `carve_chamber`, 251 cells)_
   - Carve into the solid RockFace core (~95,92); carve_chamber only eats solid rock so it stays enclosed.
8. **Talus foot at NE lobe** _(region: Rock massif, op: `hill`, 63 cells)_
   - Rubble apron at ~(66,44) to soften the abrupt rock/sand foot and add light cover.
9. **Ruined structure on mid-west outcrop** _(region: Gravel outcrops, op: `rect`, 49 cells)_
   - Ancient-concrete footprint at ~(28,61): a landmark ruin + defensible strongpoint.
10. **Roughen the coastline (LAST)** _(region: Ocean, op: `fractalize_edge`, 224 cells)_
   - Run fractalize AFTER the gradient this time so nothing re-straightens it. Push shallow water in/out irregularly against sand for a meandering shore.
11. **Final confetti cleanup** _(region: Gravel outcrops, op: `smooth`, 216 cells)_
   - Majority-smooth non-water families to absorb single-cell specks created by the coast + scatter edits.

## Metric deltas (objective guardrails, not the judge)

- **transition_coherence**: 1.0 → 1.0  (flat)
- **fragmentation_tiny_patches**: 7 → 84  (worse)
- **family_diversity**: 0.9211 → 0.6639  (worse)  _(diversity is informational — interpret in context)_

## Layering notes (pawns / items / story)

- Cave chamber: seed ancient danger / infestation deep inside - not free real estate.
- Ruined structure: slain ancients + salvage; crashed-Factory-ship scavenger theme.
- Fertile hollow by the wash: the natural farm start - raids will approach along the open wash.
- Wet-beach mud: brackish/non-potable - reinforces water-scarcity pillar (desalinate to drink).
