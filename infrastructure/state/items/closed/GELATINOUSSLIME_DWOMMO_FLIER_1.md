# GELATINOUSSLIME_DWOMMO_FLIER_1 — the dwommo: the flying aristocracy, a gas-float lobe-eater

**Free tier**, `mandrake.rm.gelatinousslime`. Design: `design/Jawa/worldbuilding/biomes/gelatinousslime_bedazzle_review_2026-10-02.md` §1 (a) 2, §3 (fliers row), §4 row 0a, §8.
Caused by `GELATINOUSSLIME_SCORING_SITTING_1` (turn 1). Ruling: build first, land what was decided (decision taken by question card 2026-10-02 ~14:25 PDT). Underlying rulings: sheet `the_slime.md` §4 (owner's rulings on the filter-feeder family, the flying aristocracy, the resistant characters), Q14 of `design/RimMandrake/biome_mod_architecture.md` §7 (by card 2026-09-23: the free def stays donor-free, holes filled with creatures of ours), Q11a (every `RM_` roster rich enough to stand alone).

## What exists

No flier of any tier on either Slime def (MEASURED in the review, 2026-10-02). The donor template the sheet
names (the aerofleet's hydrogen-float) is in the homeless reserve and stays there (Q14).

## spec

1. `RM_Dwommo`: a translucent amber gas bladder trailing feeding fronds, drifting over the body, eating
   gelatid-sized lobes; lands only on hardened slime. Immune to the wading trap (sheet: *"the aristocracy"*).
2. **Real flight** per the standing flyer rule: `MaxFlightTime`/`FlightCooldown` stats and the race flight
   fields (Locust shape, CLAUDE.md). No flip-book frames needed to ship; flying without them is correct.
3. Wire inline on `RM_GelatinousSlime/wildAnimals` (commonality `// INVENTED`, low).
4. ⛔ Flight is verified by a state read (`Pawn_FlightTracker`), never an unattended live flight hunt.

## criteria

- `jawa/get_defs` `ThingDef/RM_Dwommo` `foundCount` 1; its `MaxFlightTime` > 0.
- Art from `gelatinousslime_turn1_2026-10-02.csv`.
