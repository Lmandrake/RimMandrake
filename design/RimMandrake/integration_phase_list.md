# What waits for the integration phase

The integration phase tests every mod together on the full mod list. It starts when the owner says so, at about version 0.3.0 of
every mod (`design/RimMandrake/standing_rulings.md` §Mod development runs on small lists). Until then nobody works a line of this
page, and no line has a live ticket (a ticket older than the ruling is parked with a wait). Add a line when a small list cannot decide a claim.

## Claims that moved here

- **Pyrelands:** on the full list one lit fire walks as a front, and Pyrelands writes no error (`sc_full_list_smoke`; visit 8 read it PASS).
- **FlowWorks:** the moat season scene beside every other mod (`sc_walk`; PASS on the full list in visits 2 to 8; it runs on FlowWorks' small list now).
- **Gimme Some Slack:** the walk map on the full list (`sc_walk`; PASS on 0.1.0, 0.1.1 and 0.2.0).
- **Explosive Knockback:** the mortar barrage frame time and the raid walk on the full list.
- **Graffiti:** the long soak and the walk on the full list.
- Every mod: a load of the full list with no error that names the mod.
- Every mod: the performance of a colony among all the mods.
- The painted world: real tile ids, biomes on tiles, world testing.

## Faults that only the full list showed, still open

- Explosive Knockback: LWM's gun locker draws its guns on the full list and hides them on the 24-mod list. A mod of the full list draws them
  [guess ~60%: Weapon Racks]. The blast kept the guns (all 5 of `LWM_WeaponsLocker` at station 8, `EK_VISIT5_WALK_20261123_CLEAR.rws`). The mod
  classes the locker closed from its def (`showContents` false, `RM_KnockbackCompat.IsClosedDef`) and cannot see another mod's drawing.
  First find the mod that draws. Then stop the drawing (the owner's proposal, 2026-11-23), or class the locker open so its guns fly
  ("Anything that draws its contents is open", 2026-11-12). This line's parked item: `RIMMANDRAKE_SETTLE_GUN_LOCKER_DRAWS_ITS_GUNS_BUT_KEEPS_THEM`.
- Explosive Knockback: two storms of null errors in the raid walk after a load (780 and 447 lines). Not reproduced on 34 mods. Cause unknown.
- Pyrelands: foreign animals (Zhakka, womp rats) on the full-list map though the roster is clean. Cause unknown.
- All mods: freezes of 50 to 100 ms with the mod on or off. Cause unknown.
- Gimme Some Slack: pale rectangles on plain soil of the review map, unchanged with the mod off [guess ~70%: another mod].

## Traps to know on that day

- Prepatcher rewrites loaded assemblies in memory: a hash of the running image differs from the file.
- `ModsConfig` may name a mod that is not installed (`koth.isid`, `kutte.stairs`): the game then loads fewer mods than the list.
- The full list zooms with Camera+. A test tier zooms with SimpleCameraSetting. A save of one refuses the other.
- Dubs Bad Hygiene's thirst kills colonists on a site with no water.
