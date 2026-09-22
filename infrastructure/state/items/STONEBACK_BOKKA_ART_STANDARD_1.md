# STONEBACK_BOKKA_ART_STANDARD_1 — is the bokka's art up to modern standards?

## the ask — a question, not an order

**Owner, 2026-09-22**, sheet note on the bokka row of the identity picker:
*"Arid biome approved, make sure our art is up to modern standards."*

🔑 He asked for a **judgement**, not a regeneration. Read it that way: look at the art, decide
whether it meets the bar the newer creatures set, and regenerate only if it does not. A regen
fired without looking spends a quota-limited job and throws away art that may be fine.

## what exists — MEASURED 2026-09-22

`RSW_Stoneback` (the bokka, bodySize 0.4, our port of Biomes! Caverns' `BMT_Stoneback`) has
**three facings of our own art**, unchanged since the port landed:

```
src/RimStarWars/SWBestiary/Textures/swanimals/BiomesTeam/BMT_Caverns/Things/Animal/Stoneback/
    Stoneback_south.png   22,481 bytes   2026-09-11
    Stoneback_east.png    19,480 bytes   2026-09-11
    Stoneback_north.png   19,638 bytes   2026-09-11
```

Its texPath is correctly ours (`swanimals/...`), not the donor's — unlike its former
namesake, `KORRUM_ART_REGEN_1`.

## spec

1. **Look at it** against the newer creature art in the same mod, and against the bar the
   `reading-rimworld-graphics` / `generating-rimworld-sprites` skills describe — resolution,
   legibility at RimWorld's on-map scale, facing coherence (the three facings are independent
   side-profiles, per `ARTPIPE_FACING_COHERENCE_1`), and whether it reads as a small arid
   burrowing reptile rather than a generic lizard.
2. **Before queuing anything**, search `infrastructure/artpipe/done/`, `_artsrc/`,
   `registry.jsonl` and any `Transient/*.decisions.json` for existing bokka/stoneback art —
   the standing rule, and it has already caught three plants that had finished art nobody
   wired.
3. Only if it falls short: queue a regen, and put the result in front of him rather than
   swapping it in silently (cosmetic changes need his permission — they can break animated
   faces).

## verify

A stated verdict with the reason — kept, or regenerated with the old and new side by side.
⛔ Not "regenerated because the note said make sure": that is not what he asked.

## criteria

The bokka looks like it belongs beside the creatures we are making now.
