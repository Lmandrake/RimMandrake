<!-- Written by the session when it would show this to the owner. One verdict line per statement bullet, the
     bullet copied exactly. Verdicts: true, false, unseen, cannot tell. Only "true" passes the Stop hook, and a line
     you would caveat is not true yet. Evidence is one or more saved files, in backticks, made after your last
     change: screenshots, rendered output, logs, a recorded run. Paths relative to the project, inside it. -->
# Done claim

- true: Every-biome pass: how does each biome uniquely improve the SHIP - what players take aboard (owner 2026-09-24); running list per sitting, normalized at the end is done as `infrastructure/state/items/BIOME_SHIP_CONTRIBUTIONS_1.md` says, shown by fresh evidence. | evidence: `whittle/biome_ship_contributions_1/evidence/ship_contributions_run.txt` `whittle/biome_ship_contributions_1/evidence/ship_contributions.json` `whittle/biome_ship_contributions_1/evidence/deck_inventory.txt` `whittle/biome_ship_contributions_1/evidence/selftest_ship_contributions.txt` `whittle/biome_ship_contributions_1/evidence/lints.txt` `whittle/biome_ship_contributions_1/evidence/code_review.md` `whittle/biome_ship_contributions_1/evidence/design_judge.json` `whittle/biome_ship_contributions_1/evidence/art/verdict_round1.md` `whittle/biome_ship_contributions_1/evidence/art/RM_PatternHull_wallsim.png` `whittle/biome_ship_contributions_1/evidence/art/RM_TelluroxHexplate_2x2_tiled.png`

The item's verify: "Every shipped biome mod has at least one ship-buildable contribution or an owner-ruled exemption;
the list here matches what the mods actually ship." All 24 biomes composed into Baroque Biomes have a row; every def a
row names exists, can be built or installed on a gravship deck by the engine's own rule (foundation affordances,
placeWorkers read from their C#, plants and bringAlongOnGravship=false excluded), is that biome's own, and its research,
materials and fuel have a real source in a shipped mod. No exemption was needed. The spec's end-of-pass normalization
is done: the list is one table, one row per biome, the broken joined row fixed, the Stillsand row corrected to what
ships, and a design judge balanced the set (three changes applied).

## What I'm least sure about
- Nothing was placed, flown or used in a running game (offline lane). The verdicts are the engine's placement rules read
  from decompiled 1.6 source and the defs, not a launch. The new defs and the new atlases have not been loaded.
- 17 of 24 rows are agent picks (delegated, `delegation_policy.md` §2), and the 4 new gifts' numbers are provisional.
  The matrix went to him as a non-blocking review block (lane OWNER_QUESTIONS.md, keep-as-is recommended) and the
  picks are in his daily digest; he has not answered yet.
- The "a source hands it out" test is a whitelist of contexts plus a file-level C# rule; a C# file that both spawns
  something and merely names a material counts as its source. Patch xpath is pattern-matched, not evaluated.
- Five fresh code reviews shaped the checker; round 5's last fixes have had no review of their own, so the two
  files are not marked CLEAN.

## What I did not test
- A live launch/land with each gift aboard, an old save loading the new defs, and the Helix trader actually rolling
  the repulsor hardpoint (0~1 stock, same odds as the ground repulsor).
- In-game look of the two hull atlases at play zoom (rendered offline with the link layout only).
