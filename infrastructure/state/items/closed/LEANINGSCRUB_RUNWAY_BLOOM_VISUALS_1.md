# LEANINGSCRUB_RUNWAY_BLOOM_VISUALS_1 — ribbonwhip sway and burrower exit holes

From `LEANINGSCRUB_GPT_ENRICHMENT_1` part 2. The runway bloom's behaviour is built in
`src/RimMandrake/LeaningScrub/Source/RM_RunwayBloom.cs`: crustweevils scatter, fuzzrunners bolt,
dustflutters erupt into real flight about 40 cells and land, and visslers shed. Two pieces are
visual and need art or animation, so they are not built:

- **"ribbonwhips sway"** is a crown-floor animation. It has no behaviour of its own.
- **"burrowers leave exit holes"** means a filth or terrain mark where a burrower surfaced.

## open questions

1. **Which species are the burrowers?** No def says so. Candidates are crustweevil and surrik
   (whose comment says "crust-swimming / surfacing strike").
2. Sway: is a short `RM_RunwayBloomResponse` that plays an animation def wanted, or is a static
   graphic swap enough? Check `rimworld-sprite-facings` before choosing.
3. Exit hole: a new filth def with art. Check artpipe `done/` / `_artsrc/` / `registry.jsonl` first.

## criteria

- Both show on a bloom, gated under the existing "The runway bloom" setting.
