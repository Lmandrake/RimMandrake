# BLUEDESERT_GPT_ENRICHMENT_1 — four GPT-suggested enrichments the owner picked

Source: a GPT enrichment consult (codex exec, gpt-5.6-sol xhigh, 2026-09-30) on the Blue Desert. The
owner picked these four by question card; GPT's eight other ideas were not picked, so they are out.
Builds on `BLUEDESERT_RULED_CONTENT_1` and `BLUEDESERT_MECHANICS_BUILD_1`, and must stay inside what the
Blue Desert sitting ruled.

## spec

1. **Blue-ice heat sink.** Loading blue ice into a rack holds a room cold through a power failure. The
   blocks slowly cloud from deep blue to white while the rack groans and drips into sealed water cans,
   so during a blackout the Cold Hold warms by degrees rather than at once. Build: a `CompRefuelable`
   cold-sink rack, a room-temperature offset, spent-block-to-water conversion and a heat-capacity
   inspect string, plus XML items, the building and a recipe. Small C#. **Model: sonnet.**
2. **The line gives back slowly.** Ablation-salvage incidents unfold over several hours. First comes a
   distant crack, then a dark silhouette under thinning ice, then the exposed wreckage, meteoritic metal
   or a named freeze-dried corpse. Vekkit tracks and circling vrisk mark the spot before the letter
   arrives. Build: a staged `IncidentWorker`, emergence markers, edge-biased placement and
   corpse-history generation, plus XML incident variants and sounds. Small C#. **Model: sonnet.**
3. **Carbon Garden plants, hydrocarbon plants only.** The owner typed on the card: *"Only hydrocarbon
   plants please."* The candidates are milelace (creeping mats that stitch fresh drifts, yielding
   insulating frost-fibre), the Ninefold Censer (opens after Haze and exhales visible hydrocarbon
   breath) and longglass (branching, turns toward the wind, frosts on new growth). All are small,
   transparent, unsowable and dangerously warm-reactive, on `RM_CompPlantCharge`. Keep a candidate only
   if it is genuinely hydrocarbon-bodied, and reshape or drop any that is not. Coordinate with
   `BEDAZZLE_FLORA_EXPANSION_1`, which also owes the Blue Desert more flora. Build: XML only, plus small
   C# if they flower on Haze. New names must be collision-swept and go through art commission, with art
   to an owner review sheet before any def ships. **Model: sonnet.**
4. **The vhaulk road**, which deepens the ruled giant. Its pillar feet compress blue ice into a broad
   rime road, nearby flora is cropped flat, cistern seams boom at long intervals and frost hangs in its
   wake. It departs with a map-edge trail and a letter, never by silently despawning. Build: a movement
   comp that places temporary terrain or filth and grazing scars, plus entrance and departure handling.
   It must respect the ruled heat, ion and lightning detonation gates. Small C#. **Model: sonnet.**

Each ships a Mod Settings toggle and tuning.

## criteria

Each of the four is quicktest-proven. The vhaulk always leaves a trail.
