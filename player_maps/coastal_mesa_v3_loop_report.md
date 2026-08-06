# LLM-in-the-loop improvement — `coastal_mesa` (iteration 3)

The region decomposition, judgments, and edits below were authored by the LLM reasoning over the perceived map; this script only executed the primitives and measured the result.

## Region decomposition + judgment (LLM)

Scores 0-10. realism = looks like a real place · interest = worth exploring/fighting over · tactical = meaningful combat geography · artificiality = looks generator-stamped (LOWER is better).

| Region | Real | Intr | Tact | Artif | Problem → Intent |
|---|---|---|---|---|---|
| Ocean (W strip) | 3 | 2 | 5 | 9 | v2 shredded the waterline into salt-and-pepper because fractalize_edge had no spatial coherence; tool now rewritten to move the frontier by a smooth along-coast noise profile (headlands/inlets, not speckle) → clean depth ramp, then coherent meander via the fixed fractalize, then a few patchy wet-beach spots |
| Central sand flat | 5 | 2 | 2 | 4 | v2 vegetation still speckly (per-cell); scatter now grows coherent patches → wash + hill + soil hollow retained; vegetation as a few scrub STANDS |
| Rock massif | 6 | 4 | 7 | 3 | cave + talus foot already good in v1/v2 → keep |
| Gravel outcrops | 6 | 3 | 4 | 4 | ruin good; needs a final smooth to hit the fragmentation guardrail → keep ruin; smooth twice at the end |

## Edits executed (each tied to a region + rationale)

1. **Depth ramp** _(region: Ocean, op: `terrain_gradient`, 1920 cells)_
   - Water column x0-15 W->E: deep, deep, shallow, sand. No mud in the order.
2. **Coherent coastline meander** _(region: Ocean, op: `fractalize_edge`, 19 cells)_
   - Rewritten fractalize moves the land/water frontier along the coast by a smooth noise profile, reach 4 - carves headlands and inlets instead of noise.
3. **Patchy wet beach** _(region: Ocean, op: `scatter`, 25 cells)_
   - A few coherent Mud patches on sand right at the waterline x12-19 - wet spots, not a band.
4. **Old dry wash** _(region: Central sand flat, op: `path`, 137 cells)_
   - Gravel wash SW->NE through the dead center.
5. **Scrub stands** _(region: Central sand flat, op: `scatter`, 61 cells)_
   - Coherent mossy patches (a handful of stands) over sand only - reads as clumped desert scrub.
6. **Fertile hollow by the wash** _(region: Central sand flat, op: `blob`, 17 cells)_
   - Soil catchment at the wash bend (~45,60) - the map's farm start.
7. **Mid-flat outcrop hill** _(region: Central sand flat, op: `hill`, 84 cells)_
   - High-ground cover at ~(38,52).
8. **Cave chamber (SE massif)** _(region: Rock massif, op: `carve_chamber`, 251 cells)_
   - Carve solid RockFace core ~(95,92); stays enclosed.
9. **Talus foot (NE lobe)** _(region: Rock massif, op: `hill`, 63 cells)_
   - Rubble apron ~(66,44).
10. **Ruined structure** _(region: Gravel outcrops, op: `rect`, 49 cells)_
   - Ancient-concrete footprint ~(28,61).
11. **Confetti cleanup pass 1+2** _(region: Gravel outcrops, op: `smooth`, 75 cells)_
   - Two majority-smooth passes over non-water families to absorb specks and hit the fragmentation guardrail.

## Metric deltas (objective guardrails, not the judge)

- **transition_coherence**: 1.0 → 1.0  (flat)
- **fragmentation_tiny_patches**: 7 → 18  (worse)
- **family_diversity**: 0.9211 → 0.652  (worse)  _(diversity is informational — interpret in context)_

## Layering notes (pawns / items / story)

- Cave chamber: ancient danger / infestation deep inside.
- Ruined structure: slain ancients + salvage (Factory-ship scavenger theme).
- Fertile hollow: the farm start; raids approach along the wash.
- Wet beach: brackish/non-potable - water-scarcity pillar.
