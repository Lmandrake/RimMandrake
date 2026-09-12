# FEVER_WOOD_MECHANICS_1 — the Fever Wood C# kit, spec drafted

## spec
The authoritative brief is the FROZEN lore sheet
`design/Jawa/worldbuilding/biomes/the_fever_wood.md` (Owed section = ruling
scope). **Kit spec DRAFTED 2026-09-11:
`design/Jawa/worldbuilding/biomes/kits/fever_wood_kit_spec.md`** — 9 mechanics
(F1–F9) engine-mapped against RimSage source, 3 sibling-kit reuses from
`greentide_kit_spec.md` (causeway GenStep, Greatbole/LivingRegrowth class,
silence cue), 7 new RM_/RUT_ classes (1 L, 4 M, 2 S). **3 owner cards open**
(hidden plumbing factions vs ban §6.2 · Tenant vs player pawns · fear radius)
— `KIT_SPECS_CARD_SITTING_1` closed before this draft, so they need the next
card sitting.

The filing title's four systems all land in the spec: the Tenant as
map-spanning aquifer entity (F1: pool-strike logic, never-resolved rule),
evidence + mirror-break events (F2), marsh building-refusal terrain (F5),
pool-state intelligence (F3). The sheet's Owed additions likewise: boughway
network (F6, static in v1 — moving lanes parked on
`EXPLOSIVE_PLANT_GROWTH_1` v2, same posture as the Greentide's clause),
nectar-for-safety herd economy (F8, ban §6.6 enforced in the comp), two-front
war with ant theft-hauling + raid-back quest (F9), and the deep thing built in
full but dormant (F4 — defs + art ship, referenced by nothing; the emergence
event files with the plot when its moment is chosen).

"The Tenant" is the internal working name only (live in `water_taxonomy.csv`
row `fever_pool`); hard ban §6.1 keeps it out of player-facing text.

Build dependencies: `GREENTIDE_MECHANICS_1` M9/M12 land before F6/F7; F9's
raid-back quest may trail its raids by one build. ❓-marked engine seams in the
spec must be re-verified against the live 1.6 assembly before spending C#
(the RimSage index reads as 1.5-era).

## verify
- [ ] No Tenant ThingDef is reachable from any ambient IncidentDef/ThinkTree —
      the emergence spawner is referenced by nothing (ban §6.1, linter check).
- [ ] `Gathered()` on a below-floor-calm thornbug yields zero regardless of
      caller (ban §6.6 enforced in code).
- [ ] Pool terrains grant no buildable affordance; marsh grounds never carry
      Heavy; `RUT_StiltPlatform` is the only Heavy route at ground level.
- [ ] Ant raid exits with living thornbugs → they are recoverable alive
      (theft, not slaughter), once the raid-back quest ships.

## criteria
- [ ] The three cards ruled at a card sitting before C# is spent on
      F1 (card 2 changes its strike behavior) or F9 (card 1 changes its
      architecture).
- [ ] Build lands per the spec's order, or this file's spec section is updated
      to say what shipped and what remains.
