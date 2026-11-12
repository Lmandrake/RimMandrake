<!-- Written by the session when it would show this to the owner. One verdict line per statement bullet, the
     bullet copied exactly. Verdicts: true, false, unseen, cannot tell. Only "true" passes the Stop hook, and a line
     you would caveat is not true yet. Evidence is one or more saved files, in backticks, made after your last
     change: screenshots, rendered output, logs, a recorded run. Paths relative to the project, inside it. -->
# Done claim

- true: Every-biome pass: how does each biome uniquely improve the SHIP - what players take aboard (owner 2026-09-24); running list per sitting, normalized at the end is done as `infrastructure/state/items/BIOME_SHIP_CONTRIBUTIONS_1.md` says, shown by fresh evidence. | evidence: `whittle/biome_ship_contributions_1/evidence/ship_contributions_run.txt` `whittle/biome_ship_contributions_1/evidence/ship_contributions.json` `whittle/biome_ship_contributions_1/evidence/deck_inventory.txt` `whittle/biome_ship_contributions_1/evidence/selftest_ship_contributions.txt` `whittle/biome_ship_contributions_1/evidence/lints.txt` `whittle/biome_ship_contributions_1/evidence/code_review.md` `whittle/biome_ship_contributions_1/evidence/effective_def_lint.txt` `whittle/biome_ship_contributions_1/evidence/owner_card.md` `whittle/biome_ship_contributions_1/evidence/art/RM_SpunstoneHull_wallsim.png` `whittle/biome_ship_contributions_1/evidence/design_judge_r2.json` `whittle/biome_ship_contributions_1/evidence/art2/contact_sheet_96ppc.png` `whittle/biome_ship_contributions_1/evidence/art2/verdict_r2.md` `whittle/biome_ship_contributions_1/evidence/design_judge.json` `whittle/biome_ship_contributions_1/evidence/art/verdict_round1.md` `whittle/biome_ship_contributions_1/evidence/art/RM_PatternHull_wallsim.png` `whittle/biome_ship_contributions_1/evidence/art/RM_TelluroxHexplate_2x2_tiled.png`

The item's verify: "Every shipped biome mod has at least one ship-buildable contribution or an owner-ruled exemption;
the list here matches what the mods actually ship." All 24 biomes composed into Baroque Biomes have a row; every def a
row names exists, can be built or installed on a gravship deck by the engine's own rule (foundation affordances,
placeWorkers read from their C#, plants and bringAlongOnGravship=false excluded), is that biome's own, and its research,
materials and fuel have a real source in a shipped mod; no patch moves its placement. No exemption was needed. The
spec's end steps are done: gaps swept (four new gifts built, art judged), the set balanced (a design judge's three
changes, then one heater instead of three; a second judge ruled the water and light clusters distinct in play and
weighed every row for worth, and its six fixes are applied, including a new Long Shade gift), every gift painted in its
own art (20 pictures, art judge KEEP), and the matrix carded to the owner (`evidence/owner_card.md`). The composed
mod built from this clone loads clean in the offline effective def tree (`evidence/effective_def_lint.txt`).

## What I'm least sure about
- Nothing was placed, flown or used in a running game (offline lane). Placement is the engine's rules read from
  decompiled 1.6 and the defs; the load check reads defs and patches as the game does but runs no C#.
- 20 rows are agent picks under the delegation (each row says where it comes from), and the 4 new gifts' numbers are
  provisional; the owner card is not answered yet (keep-as-is recommended, non-blocking).
- The art is judged as stills and contact sheets at play scale, not on a deck in game; the mast's base top face is a
  little thin (the art judge's note, judged shippable).
- The checker's source test is a whitelist plus a file-level C# rule, and patch xpath is pattern-matched, not
  evaluated (both documented in the checker).

## What I did not test
- A live launch/land with each gift aboard, an old save loading the new defs, and the Helix trader actually rolling
  the repulsor hardpoint (0~1 stock, same odds as the ground repulsor).
- In-game look of the two hull atlases at play zoom (rendered offline with the link layout only).
