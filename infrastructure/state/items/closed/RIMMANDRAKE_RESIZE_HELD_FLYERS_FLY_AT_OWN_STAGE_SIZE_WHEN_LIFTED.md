# RIMMANDRAKE_RESIZE_HELD_FLYERS_FLY_AT_OWN_STAGE_SIZE_WHEN_LIFTED

## spec

Seven flyers fly at their first life stage's size, so the adults fly smaller than they walk. RimWorld 1.6
(`AnimationDefGenerator_Flying`) sizes every stage's flight frames from the first stage when
`flyingAnimationInheritColors` is false, and caches them by `bodyGraphicData` colour when it is true. Their mods are on
the owner's hold list (`src/RimMandrake/rimflow/mod_owner_hold.json`), so the parent item
`RIMMANDRAKE_RESIZE_FLYERS_ADULTS_FLY_AT_BABY_SIZE_TWENTY_OF_THEM` did not touch them.

| flyer | mod (held) |
|---|---|
| RM_Sparkleech | Contagion |
| RM_Skellick | FeverWood |
| RM_Dwommo | GelatinousSlime |
| RM_Zellik, RM_Dustflutter, RM_Shirrel | LeaningScrub |
| RM_Soorrak | Stillsand |

When a mod's hold lifts, fix its flyers with `python3 src/RimMandrake/Utils/art/flyer_stage_colours.py <PawnKindDef> ...`
(the tool that made the parent's fix, abbfb368). Do not lift a hold for this item.

## verify

- Offline: `python3 src/RimMandrake/Utils/art/flyer_size_census.py` exits 0 (today it lists the seven as OFF).
- Live, on a game with the mod deployed: `python.exe src/RimMandrake/Utils/art/live_flyer_flight_sizes.py <PawnKindDef> ...`
  exits 0.
