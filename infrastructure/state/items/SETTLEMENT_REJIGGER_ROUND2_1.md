# SETTLEMENT_REJIGGER_ROUND2_1 — re-shift the settlements to fit the frozen biomes

Owner, 2026-09-06, verbatim in intent: *"once the biomes are pre-frozen for the
animal/plant work, we also should go back and potentially re-shift the settlements to
make the most sense. This is a big 'round 2 rejigger' to make sure everything is
reasonably harmonious. That should happen right AFTER the biome review, but before the
animal/plant work."*

## sequence (ruled)
`BIOME_FREEZE_FABLE_REVIEW_1` (the biomes pre-frozen) → **THIS** → the animal/plant
assignment (`BIOME_FAUNA_ASSIGNMENT_SITTING_1`) and the inhabited injections.

## spec
- Inputs: the frozen sheets (every biome's §8 Inhabited objects + who-lives-here
  rulings — e.g. Moisture Farmers in the Badlands' canyons, Junkers terminator-bound at
  the Wasteland dump, the Free Droid Enclave's four nightside seats, Wildsteam's sacred
  groves in the Rot and their bend around the Slime, the Helix at the Contagion's valley
  mouths, the Hutts, the Trade Moot, the Empire's orbital + surface holdings), the
  faction specs (`design/Jawa/faction_*`, `FACTION_SPEC.md`), the current settlement
  placement on the frozen world (MEASURED via the world tools / CSV — never a doc's
  number), the semipermanent-bases seed.
- For every settlement/base: does its biome, region and neighbors make sense under the
  frozen sheet? Table: settlement · faction · current tile/biome · sheet says · verdict
  (stay / move → where / drop) · reason. Card every move to the owner; nothing moves
  without his yes (the world is his; `design/**` on his word).
- Harmony checks: water access (cisterns, fog line, floods), the anti-bullseye pattern
  of faction ranges, road/caravan plausibility, the Empire's reach, who is near whom
  (enemies adjacent on purpose only).
- Then: repaint settlements via the world tools + `world_commit`, re-freeze the
  savegame (back up Saves keepers), re-render `worldview.py` for the owner.

## verify
The settlement table exists as data with an owner verdict per row; the frozen world's
settlements match the table (MEASURED read-back); the assignment sitting starts from it.
