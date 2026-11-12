# JUDGE — BIOME_SHIP_CONTRIBUTIONS_1 (blind judge, CLAUDE_STEVEDESKTOP_OFFLINE2 seat, 2026-11-11)

Read: STATEMENT.md, NOTES.md, the item file `infrastructure/state/items/BIOME_SHIP_CONTRIBUTIONS_1.md`,
`rimflow show`, every file in evidence/ (all art images I judged opened), the four new defs' XML, the Blue Desert design doc §7.
Not read: DONE.md, BROADEN.md.
Rerun: `python3 src/RimMandrake/Utils/ship_contributions.py` -> exit 0, 24/24 PASS, the same verdict lines as
`evidence/ship_contributions_run.txt` (my copy: `/mnt/d/ClaudeWork/rimmandrake/judge_bsc1/run.txt`).

## Statement line

> "...is done as `infrastructure/state/items/BIOME_SHIP_CONTRIBUTIONS_1.md` says, shown by fresh evidence."

**false.** The item has a lot of solid work, but it is not done as its own spec says, and part of the evidence
undercuts it:

What holds (true as far as offline evidence goes):
- Coverage: every one of the 24 composed biome mods has a row naming defs that exist. Rerunning the checker reproduces
  this, and its selftest rejects 12 mutated lists (`selftest_ship_contributions.txt`).
- The new defs match what their rows say. RM_PatternHull has 480 HP and `CompProperties_SelfhealHitpoints`
  ticksPerHeal 500 (= 120 HP/day), Substructure affordance and Odyssey category. RM_TelluroxHexplate now costs 1 shell
  at Beauty 5, so the design judge's change was applied. RM_FurnaceHideBank is a fuel-free HeatPusher (6/s, cap 21 C).
  RM_FossilCase has Beauty 14.
- Art: I opened the pattern and spunstone wall sims, the 2x2 hexplate tile, the fossil case and the hide bank. All five
  look shippable and the links render correctly in the sims. The hexplate tiles without a visible seam. The spunstone hull
  shows a dark seam and the same braid at every cell join in a straight run. The art judge flagged this too and
  left it unfixed.

Why the line is false:
1. **The spec's last step was not done.** The spec says: "balance the set so every biome's gift is distinct ... and
   card the matrix to the owner." No card exists in the evidence. On distinctness, the design judge's own `duplicates`
   list names near-duplicates that were kept: Leaning Scrub's wind vaporator and Weeping Stones' condenser both pull
   water from the air, and Pyrelands, The Rot and The Abyss each give a cabin warmer. Three biomes give water and three
   give heat, so the "distinct" bar is only partly met.
2. **One row misattributes an owner ruling.** Blue Desert's row says "owner by card 2026-09-24" for `RM_ColdSinkRack`,
   a rack that cools a room without power. The card that doc §7 records (lines 260-264) ruled something else: blue-ice
   blocks as the ship's distilled-water stock, plus butane/Burner-gland chemfuel that is safe only while refrigerated.
   The listed def is a sibling idea, not what he ruled. Either the row's source line is wrong or the ruled gift was
   never built.
3. **The item was routed away from this lane.** It is kind=design. The 2026-11-03 OWNER-seat note says its design
   "still needs arguing out, so it waits for the Designer (per mod, on demand)". This pass chose 18 of 24 rows as
   *delegated* agent picks instead. The 2026-10-22 delegation and the 2026-10-30 Conductor ruling may cover that.
   Even so, the later item-specific note is not addressed anywhere in the evidence.
4. **The instrument behind the headline is not CLEAN.** `evidence/code_review.md` says so itself: round 5 found
   wildcard xpath and ParentName-rewrite blind spots, and its fixes have not been reviewed. Under project rules
   `ship_contributions.py` is still DIRTY, so the "24/24 PASS" comes from an unreviewed checker.
5. **Nothing was loaded in the game.** README says so. Four new defs, the Helix trader edit and five textures have never
   been through a game load. "Can stand on a gravship deck the way the engine decides it" is the checker's model of the
   engine. Nothing shows any of these placed on substructure, flown, or (for the pattern hull) actually healing.

## Staged or flattering evidence
- The run is 24 rows of PASS from a checker the builder wrote, scoped by its own README. It is reproducible, but it
  proves existence and placement rules, not that each gift is worth landing for.
- The art is stills on a flat ground. The wall sims are simulated linking, not an in-game render. No true-scale panel
  beside a pawn exists (the art judge says it lacked B3/D1 inputs).
- Nothing shows motion or behaviour (heat banking, self-heal, range multiplier, condenser output).

## What would settle it
A card of the matrix to the owner (or a recorded ruling that it is waived). Fix the Blue Desert row to match §7, or
build the water stock and refrigerated butane. A clean round on `ship_contributions.py`. One deploy and load round
showing the new defs load with no errors and can be placed on a substructure deck.

would show: no
