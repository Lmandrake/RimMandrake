# SUMP_KETHREL_BUILD_1

Spec: `design/Jawa/worldbuilding/biomes/sump_bedazzle_review_2026-10-01.md` §3 ("the kethrel"), from the GPT consult `Transient/bedazzle_gpt_enrich_2026-10-01/sump.md` #5. Ruled by the owner, turn 1, by card.

1. `RM_Kethrel` (free tier, Sump-only, inline in `RM_TheSump`): a boneless hydrocarbon surface animal that picks up loose rigid things (dropped weapons, slag, components, scrap) and wears them as an armour shell. Load raises armour and mass and lowers speed; footstep sound changes with load.
2. Carried things live in a real `ThingOwner`, listed on an inspect tab, dropped on molt, death or leaving the map (a molt cairn and a letter if it leaves). Nothing vanishes.
3. A handler can coax a molt (animal-handling job); a bad roll is a panicked charge.
4. Four armour stages as four whole-body static sprite sets (bare, light, heavy, full carapace), three facings each, swapped by load. No animation.
5. Mod Settings: on/off, density, value ceiling, taking colony property (toggle), molt threshold, handling difficulty.

Art: `infrastructure/artpipe/art_lists/sump_bedazzle_cast.csv`.

## verify
- Quicktest: a kethrel picks up dropped weapons, its sprite steps up a stage, its inspect tab lists them, and a molt drops every item.
